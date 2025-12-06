import chess.pgn

def load_pgn(file_path):
    with open(file_path) as f:
        game = chess.pgn.read_game(f)
    return game
