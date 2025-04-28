import base64
import requests
from PIL import Image
from io import BytesIO
import chess.engine
from src.utils.tooling import tool

@tool
def analyze_chess(image_path: str) -> str:
    """
    Analyzes a chess position from an image and determines the best next move.
    Args:
        image_path (str): The path to the image file containing the chess position.
    Returns:
        str: The recommended move in algebraic notation.
    """
    def extract_fen_from_image(image_path):
        img = Image.open(image_path)
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        data = {
            "board_orientation": "predict",
            "cropped": False,
            "current_player": "white",
            "image": f"data:image/jpeg;base64,{img_str}",
            "predict_turn": True
        }

        response = requests.post("http://app.chessvision.ai/predict", json=data)

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result.get("result")
            else:
                raise Exception("Failed to get FEN from image")
        else:
            raise Exception("Request to Chessvision.ai API failed")

    def is_valid_fen(fen):
        try:
            chess.Board(fen)
            return True
        except ValueError:
            return False

    def correct_fen(fen):
        """
        Corrige les caractères invalides dans la chaîne FEN et assure qu'elle respecte le format standard.
        """
        fen = fen.replace('_', ' ')
        fen = fen.strip()
        parts = fen.split()

        if len(parts) < 6:
            while len(parts) < 6:
                parts.append('-')

        board_position = parts[0]
        if not all(c in 'pnbrqkPNBRQK12345678/' for c in board_position):
            raise ValueError("Invalid characters in board position")

        turn = parts[1]
        if turn not in ('w', 'b'):
            raise ValueError("Invalid turn: must be 'w' or 'b'")

        castling_rights = parts[2]
        if not all(c in 'KQkq-' for c in castling_rights):
            raise ValueError("Invalid castling rights")

        en_passant = parts[3]
        if en_passant != '-' and (len(en_passant) != 2 or en_passant[0] not in 'abcdefgh' or en_passant[1] not in '12345678'):
            raise ValueError("Invalid en passant target square")

        halfmove_clock = parts[4]
        if not halfmove_clock.isdigit():
            raise ValueError("Invalid halfmove clock")

        fullmove_number = parts[5]
        if not fullmove_number.isdigit():
            raise ValueError("Invalid fullmove number")

        corrected_fen = ' '.join(parts)
        return corrected_fen

    def get_best_move(fen):
        if not is_valid_fen(fen):
            raise ValueError(f"Invalid FEN: {fen}")

        engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        result = engine.play(chess.Board(fen), chess.engine.Limit(time=2.0))
        engine.quit()
        return result.move.uci()

    fen = extract_fen_from_image(image_path)
    fen = correct_fen(fen)

    try:
        best_move = get_best_move(fen)
    except ValueError as e:
        return str(e)

    return best_move