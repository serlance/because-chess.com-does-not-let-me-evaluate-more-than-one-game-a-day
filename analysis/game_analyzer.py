import chess
import chess.pgn
from analysis.evaluator import Evaluator
from analysis.move_suggestor import MoveSuggestor
import matplotlib.pyplot as plt

class GameAnalyzer:
    def __init__(self, engine_path):
        self.evaluator = Evaluator(engine_path)
        self.suggestor = MoveSuggestor(engine_path)

    def analyze_game(self, pgn_file):
        with open(pgn_file) as f:
            game = chess.pgn.read_game(f)

        board = game.board()
        evaluations = []
        played_moves = []
        best_moves = []

        print("\n=== Game Analysis ===\n")

        for move in game.mainline_moves():
            played_moves.append(move)
            best = self.suggestor.best_move(board)
            best_moves.append(best)
            eval_cp = self.evaluator.evaluate_board(board)
            evaluations.append(eval_cp)

            print(f"Move played: {move}")
            print(f"Stockfish suggests: {best}")
            print(f"Evaluation: {eval_cp} centipawns\n")

            board.push(move)

        return evaluations, played_moves, best_moves

    def plot_evaluation_graph(self, evaluations):
        plt.plot(range(1, len(evaluations)+1), evaluations, marker='o')
        plt.xlabel("Move number")
        plt.ylabel("Evaluation (centipawns)")
        plt.title("Game Evaluation Graph")
        plt.grid(True)
        plt.show()
