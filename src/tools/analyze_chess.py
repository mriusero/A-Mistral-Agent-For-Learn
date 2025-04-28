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
    try:
        import chess.engine
        from PIL import Image
        import cv2
        import numpy as np
    except ImportError as e:
        raise ImportError(
            "You must install packages `python-chess`, `Pillow`, and `opencv-python` to run this tool."
            "For instance, run `pip install chess pillow opencv-python`."
        ) from e

    def preprocess_image(image_path):
        image = Image.open(image_path)
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        return image

    def detect_board_position(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)      # For example, use contour detection to find the chessboard
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        board_contour = max(contours, key=cv2.contourArea)      # Assume the largest contour is the chessboard
        return board_contour

    def extract_fen_from_image(image):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"        # Placeholder FEN string
        return fen

    def get_best_move(fen):

        engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")         # Initialize the chess engine
        board = chess.Board(fen)                                                            # Create a board from the FEN string
        result = engine.play(board, chess.engine.Limit(time=2.0))                           # Get the best move
        engine.quit()
        return result.move.uci()

    image = preprocess_image(image_path)            # Preprocess the image
    board_contour = detect_board_position(image)    # Detect the board position
    fen = extract_fen_from_image(image)             # Extract the FEN string from the image
    best_move = get_best_move(fen)                  # Get the best move

    return best_move
