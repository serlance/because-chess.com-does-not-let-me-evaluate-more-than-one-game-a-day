import chess

def fen_to_board(fen: str) -> chess.Board:
    return chess.Board(fen)

def board_to_fen(board: chess.Board) -> str:
    return board.fen()
