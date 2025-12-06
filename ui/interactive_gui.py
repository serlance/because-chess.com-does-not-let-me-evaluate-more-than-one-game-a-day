import sys
import os
import threading
import traceback
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import chess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    from analysis.game_analyzer import GameAnalyzer
except Exception:
    GameAnalyzer = None

DEFAULT_MODEL_PATH = os.path.normpath(os.path.join(ROOT_DIR, "models", "llama-2-7b-chat.Q4_K_M.gguf"))
LLAMA_MODEL_PATH = os.environ.get("LLAMA_MODEL_PATH", DEFAULT_MODEL_PATH)

llm = None
try:
    from llama_cpp import Llama

    if os.path.exists(LLAMA_MODEL_PATH):
        try:
            llm = Llama(model_path=LLAMA_MODEL_PATH)
            print(f"Llama loaded from {LLAMA_MODEL_PATH}")
        except Exception as e:
            print("Failed to initialize Llama:", e)
            llm = None
    else:
        print("LLAMA model path does not exist:", LLAMA_MODEL_PATH)
except Exception as e:
    print("llama_cpp import failed:", e)
    llm = None

ENGINE_PATH = os.path.join(ROOT_DIR, "data", "stockfish", "stockfish.exe")
PGN_FILE = os.path.join(ROOT_DIR, "data", "pgn_samples", "sample_game.pgn")
IMAGE_DIR = os.path.join(ROOT_DIR, "images")

SQUARE_SIZE = 60
BOARD_SIZE = SQUARE_SIZE * 8
EVAL_BAR_HEIGHT = 400
EVAL_BAR_MID = EVAL_BAR_HEIGHT // 2

MOVE_CLASSES = [
    (-float('inf'), -300, "Blunder"),
    (-300, -100, "Mistake"),
    (-100, -50, "Miss"),
    (-50, 50, "Good"),
    (50, 150, "Great"),
    (150, float('inf'), "Brilliant")
]


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Chess Analyzer")
        self.root.resizable(False, False)

        if GameAnalyzer is not None:
            try:
                self.analyzer = GameAnalyzer(ENGINE_PATH)
                analyze_result = self.analyzer.analyze_game(PGN_FILE)
                if isinstance(analyze_result, tuple) and len(analyze_result) >= 2:
                    self.evals = analyze_result[0] or []
                    self.played_moves = analyze_result[1] or []
                    self.best_moves = analyze_result[2] if len(analyze_result) > 2 else []
                else:
                    self.evals, self.played_moves, self.best_moves = [], [], []
            except Exception:
                print("GameAnalyzer failed:", traceback.format_exc())
                self.evals, self.played_moves, self.best_moves = [], [], []
        else:
            print("GameAnalyzer not available — running with empty game.")
            self.evals, self.played_moves, self.best_moves = [], [], []

        self.board = chess.Board()
        self.move_index = 0

        self.piece_images = {}
        self._load_piece_images()

        left_frame = tk.Frame(root, padx=10, pady=10, bg="#f5f5f5")
        left_frame.pack(side=tk.LEFT)
        right_frame = tk.Frame(root, padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(left_frame, width=BOARD_SIZE, height=BOARD_SIZE, highlightthickness=0)
        self.canvas.pack()

        self.eval_canvas = tk.Canvas(right_frame, width=80, height=EVAL_BAR_HEIGHT, bg="#121212", highlightthickness=0)
        self.eval_canvas.pack(pady=(0, 10))

        controls = tk.Frame(right_frame)
        controls.pack(pady=6)
        ttk.Button(controls, text="◀ Previous", command=self.prev_move, width=12).grid(row=0, column=0, padx=3, pady=3)
        ttk.Button(controls, text="Next ▶", command=self.next_move, width=12).grid(row=0, column=1, padx=3, pady=3)

        self.commentary_label = tk.Label(right_frame, text="", wraplength=220, justify="left", font=("Segoe UI", 10))
        self.commentary_label.pack(pady=6)

        self.quality_label = tk.Label(right_frame, text="Move Quality: —", font=("Segoe UI", 11, "bold"))
        self.quality_label.pack(pady=(10, 2))

        self.acpl_label = tk.Label(right_frame, text="ACPL  O:—  M:—  E:—", font=("Segoe UI", 10))
        self.acpl_label.pack(pady=4)

        self.san_label = tk.Label(right_frame, text="Move: —", font=("Segoe UI", 10))
        self.san_label.pack(pady=4)
        self.eval_label = tk.Label(right_frame, text="Eval: — cp", font=("Segoe UI", 10))
        self.eval_label.pack(pady=4)

        self.update_gui(initial=True)

    def _load_piece_images(self):
        mapping = {'P': 'pawn', 'R': 'rook', 'N': 'knight', 'B': 'bishop', 'Q': 'queen', 'K': 'king'}
        for color in ('white', 'black'):
            for p, name in mapping.items():
                fname = f"{color}-{name}.png"
                path = os.path.join(IMAGE_DIR, fname)
                try:
                    img = Image.open(path).convert("RGBA")
                    img = ImageOps.contain(img, (SQUARE_SIZE - 6, SQUARE_SIZE - 6))
                    self.piece_images[f"{'w' if color == 'white' else 'b'}{p}"] = ImageTk.PhotoImage(img)
                except Exception:
                    from PIL import ImageDraw
                    ph = Image.new("RGBA", (SQUARE_SIZE - 6, SQUARE_SIZE - 6), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(ph)
                    col = (220, 220, 220, 255) if color == 'white' else (40, 40, 40, 255)
                    draw.ellipse([2, 2, SQUARE_SIZE - 8, SQUARE_SIZE - 8], fill=col)
                    self.piece_images[f"{'w' if color == 'white' else 'b'}{p}"] = ImageTk.PhotoImage(ph)

    def draw_board(self):
        self.canvas.delete("all")
        light, dark = "#F0D9B5", "#B58863"
        for rank in range(8):
            for file in range(8):
                x0, y0 = file * SQUARE_SIZE, (7 - rank) * SQUARE_SIZE
                x1, y1 = x0 + SQUARE_SIZE, y0 + SQUARE_SIZE
                fill = light if (file + rank) % 2 == 0 else dark
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=fill, outline=fill)

        if 0 < self.move_index <= len(self.played_moves):
            last_move = self.played_moves[self.move_index - 1]
            if isinstance(last_move, chess.Move):
                self.draw_move_arrow(last_move)

        for sq in chess.SQUARES:
            piece = self.board.piece_at(sq)
            if piece:
                cx = chess.square_file(sq) * SQUARE_SIZE + SQUARE_SIZE // 2
                cy = (7 - chess.square_rank(sq)) * SQUARE_SIZE + SQUARE_SIZE // 2
                key = f"{'w' if piece.color else 'b'}{piece.symbol().upper()}"
                img = self.piece_images.get(key)
                if img:
                    self.canvas.create_image(cx, cy, image=img)

    def draw_move_arrow(self, move, color="#1976D2"):
        try:
            x1 = chess.square_file(move.from_square) * SQUARE_SIZE + SQUARE_SIZE // 2
            y1 = (7 - chess.square_rank(move.from_square)) * SQUARE_SIZE + SQUARE_SIZE // 2
            x2 = chess.square_file(move.to_square) * SQUARE_SIZE + SQUARE_SIZE // 2
            y2 = (7 - chess.square_rank(move.to_square)) * SQUARE_SIZE + SQUARE_SIZE // 2
            self.canvas.create_line(x1, y1, x2, y2, width=5, fill=color, arrow=tk.LAST, arrowshape=(16, 20, 8),
                                    capstyle=tk.ROUND)
        except Exception:
            pass

    def update_eval_bar(self):
        self.eval_canvas.delete("all")
        self.eval_canvas.create_rectangle(0, 0, 80, EVAL_BAR_HEIGHT, fill="#121212", outline="")
        self.eval_canvas.create_line(10, EVAL_BAR_MID, 70, EVAL_BAR_MID, fill="#444", width=1)

        cp = 0
        if 0 <= self.move_index < len(self.evals):
            try:
                cp = int(self.evals[self.move_index])
            except Exception:
                cp = 0

        frac = max(min(cp / 800.0, 1.0), -1.0)
        height = int(frac * (EVAL_BAR_MID - 10))

        if height >= 0:
            self.eval_canvas.create_rectangle(20, EVAL_BAR_MID - height, 60, EVAL_BAR_MID, fill="#4CAF50", outline="")
        else:
            self.eval_canvas.create_rectangle(20, EVAL_BAR_MID, 60, EVAL_BAR_MID - height, fill="#E53935", outline="")

        self.eval_canvas.create_text(40, 10, text=f"{cp} cp", fill="#fff", font=("Segoe UI", 10, "bold"))

    def classify_move_label(self, index):
        if index == 0:
            return "Start"
        if index - 1 < 0 or index >= len(self.evals):
            return "—"
        before = self.evals[index - 1]
        after = self.evals[index]
        try:
            diff = float(after) - float(before)
            loss = abs(diff)
        except Exception:
            return "—"
        if loss < 10:
            return "Brilliant"
        if loss < 30:
            return "Great"
        if loss < 70:
            return "Best"
        if loss < 150:
            return "Mistake"
        if loss < 400:
            return "Miss"
        return "Blunder"

    def compute_section_acpl(self):
        def acpl_for(seg):
            if len(seg) < 2:
                return 0
            diffs = []
            for i in range(1, len(seg)):
                try:
                    diffs.append(abs(float(seg[i]) - float(seg[i - 1])))
                except Exception:
                    pass
            return int(sum(diffs) / len(diffs)) if diffs else 0

        opening = self.evals[:12] if len(self.evals) >= 12 else self.evals
        middle = self.evals[12:30] if len(self.evals) > 12 else []
        end = self.evals[30:] if len(self.evals) > 30 else []
        return acpl_for(opening), acpl_for(middle), acpl_for(end)

    def generate_move_comment_sync(self, move):
        if llm is None:
            return "LLM not available."

        try:
            temp_board = chess.Board()
            for i in range(self.move_index - 1):
                temp_board.push(self.played_moves[i])
            try:
                san = temp_board.san(move)
            except:
                san = move.uci()
            fen = temp_board.fen()
        except Exception as e:
            return f"(commentary error preparing move) {e}"

        prompt = (
            f"Comment in 1 short sentence (max 15 words) on how this move affects the current game.\n"
            f"Focus only on positional changes for White or Black.\n"
            f"If the effect is small, say 'Minor positional change.'\n"
            f"FEN: {fen}\n"
            f"Move: {san}\n"
        )

        try:
            res = llm(prompt, max_tokens=64, stop=["\n"])
            if isinstance(res, dict):
                if "choices" in res and len(res["choices"]) > 0:
                    if "text" in res["choices"][0]:
                        return res["choices"][0]["text"].strip()
            return str(res).strip()
        except Exception as e:
            return f"(LLM error) {e}"

    def generate_move_comment_async(self, move):
        def worker():
            try:
                comment = self.generate_move_comment_sync(move)
            except Exception as e:
                comment = f"(commentary error) {e}"
            self.root.after(0, lambda: self.commentary_label.config(text=comment))

        threading.Thread(target=worker, daemon=True).start()

    def update_gui(self, initial=False):
        self.draw_board()
        self.update_eval_bar()

        try:
            if self.move_index == 0:
                san_text = "Start"
            elif len(self.board.move_stack) > 0:
                last_move = self.board.peek()
                san_text = self.board.san(last_move)
            else:
                san_text = "—"
        except Exception:
            san_text = "—"
        self.san_label.config(text=f"Move: {san_text}")

        quality = self.classify_move_label(self.move_index)
        self.quality_label.config(text=f"Move Quality: {quality}")

        o, m, e = self.compute_section_acpl()
        self.acpl_label.config(text=f"ACPL  O:{o}  M:{m}  E:{e}")

        cp_text = "—"
        if 0 <= self.move_index < len(self.evals):
            try:
                cp_text = f"{int(self.evals[self.move_index])} cp"
            except Exception:
                cp_text = str(self.evals[self.move_index])
        self.eval_label.config(text=f"Eval: {cp_text}")

        if 0 < self.move_index <= len(self.played_moves):
            move = self.played_moves[self.move_index - 1]
            self.commentary_label.config(text="Generating commentary...")
            self.generate_move_comment_async(move)
        else:
            self.commentary_label.config(text="")

    def next_move(self):
        if self.move_index < len(self.played_moves):
            next_move = self.played_moves[self.move_index]
            try:
                self.board.push(next_move)
            except Exception:
                try:
                    if isinstance(next_move, str):
                        self.board.push(chess.Move.from_uci(next_move))
                except Exception:
                    pass
            self.move_index += 1
            self.update_gui()

    def prev_move(self):
        if self.move_index > 0:
            try:
                self.board.pop()
            except Exception:
                pass
            self.move_index -= 1
            self.update_gui()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()
