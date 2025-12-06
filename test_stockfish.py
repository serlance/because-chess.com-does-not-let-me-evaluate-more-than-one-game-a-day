import chess
from engine.stockfish_engine import StockfishEngine

ENGINE_PATH = "data/stockfish/stockfish.exe"  # make sure this path is correct

def main():
    engine = StockfishEngine(ENGINE_PATH)
    board = chess.Board()  # starting position

    best_move = engine.best_move(board)
    evaluation = engine.evaluate(board)

    print(f"Best move: {best_move}")
    print(f"Evaluation (centipawns): {evaluation}")

    engine.quit()

if __name__ == "__main__":
    main()
