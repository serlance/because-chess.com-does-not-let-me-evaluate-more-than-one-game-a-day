import chess
from engine.stockfish_engine import StockfishEngine

class MoveSuggestor:
    def __init__(self, engine_path):
        self.engine = StockfishEngine(engine_path)

    def best_move(self, board: chess.Board):
        return self.engine.best_move(board)
