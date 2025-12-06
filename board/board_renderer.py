import chess
import chess.svg
import cairosvg

def render_board(board: chess.Board, filename="board.png"):
    svg_data = chess.svg.board(board=board)
    cairosvg.svg2png(bytestring=svg_data, write_to=filename)
