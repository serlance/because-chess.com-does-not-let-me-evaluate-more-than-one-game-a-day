import chess
from engine.stockfish_engine import StockfishEngine

class Evaluator:
    def __init__(self, engine_path):
        self.engine = StockfishEngine(engine_path)

    def evaluate_board(self, board: chess.Board):
        return self.engine.evaluate(board)
