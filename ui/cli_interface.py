from analysis.game_analyzer import GameAnalyzer

ENGINE_PATH = "data/stockfish/stockfish.exe"

def run_cli():
    analyzer = GameAnalyzer(ENGINE_PATH)
    print("=== Chess Analysis CLI ===")
    pgn_file = input("Enter PGN filename (e.g., data/pgn_samples/sample.pgn): ")

    evaluations, played_moves, best_moves = analyzer.analyze_game(pgn_file)
    analyzer.plot_evaluation_graph(evaluations)
