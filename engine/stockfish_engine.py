import chess
import chess.engine

class StockfishEngine:
    def __init__(self, engine_path: str):
        self.engine_path = engine_path
        self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    def evaluate(self, board: chess.Board, time=0.1):
        info = self.engine.analyse(board, chess.engine.Limit(time=time))
        return info["score"].white().score(mate_score=10000)

    def best_move(self, board: chess.Board, time=0.1):
        result = self.engine.play(board, chess.engine.Limit(time=time))
        return result.move

    def quit(self):
        self.engine.quit()
