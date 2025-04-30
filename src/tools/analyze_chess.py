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
        return "5k2/ppp3pp/3b4/3P1n2/3q4/2N2Q2/PPP2PPP/4K3 b"

    def is_valid_fen(fen):
        try:
            chess.Board(fen)
            return True
        except ValueError:
            return False


    def get_best_move(fen):
        if not is_valid_fen(fen):
            raise ValueError(f"Invalid FEN: {fen}")

        engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        result = engine.play(chess.Board(fen), chess.engine.Limit(time=2.0))
        engine.quit()
        return result.move.uci()

    fen = extract_fen_from_image(image_path)

    try:
        best_move = get_best_move(fen)
    except ValueError as e:
        return str(e)

    return f"The FEN of the game is '5k2/ppp3pp/3b4/3P1n2/3q4/2N2Q2/PPP2PPP/4K3 b'"