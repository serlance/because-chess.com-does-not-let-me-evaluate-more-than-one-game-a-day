# because-chess.com-does-not-let-me-evaluate-more-than-one-game-a-day


# Chess Move Evaluator

This is a Python project I built to give **quick, game-specific comments on chess moves**. The main goal is to understand how a move affects the position in this game without giving long, generic explanations.

---

## Project Structure

```
CHESS_ANALYSIS/
│
├── .env/ # Virtual environment files
│ ├── Include/
│ ├── Lib/
│ └── Scripts/
├── .gitignore # Git ignore file
├── pyvenv.cfg # Virtual environment configuration
├── .vscode/ # VSCode settings
│
├── analysis/ # Core analysis logic
│ ├── init.py
│ ├── evaluator.py # Evaluates moves using LLaMA & Stockfish
│ ├── game_analyzer.py # Analyzes full games, produces insights
│ └── move_suggestor.py # Suggests best moves
│
├── board/ # Chess board handling
│ ├── init.py
│ ├── board_renderer.py # Renders board images/diagrams
│ └── fen_utils.py # FEN validation & conversion utilities
│
├── data/ # Sample and engine data
│ ├── pgn_samples/ # Example PGN game files
│ └── stockfish/ # Stockfish binaries for evaluation
│
├── engine/ # Chess engine interface
│ ├── init.py
│ └── stockfish_engine.py # Wrapper for interacting with Stockfish
│
├── images/ # Chess piece images
│ ├── black-bishop.png
│ ├── black-king.png
│ ├── black-knight.png
│ ├── black-pawn.png
│ ├── black-queen.png
│ ├── black-rook.png
│ ├── white-bishop.png
│ ├── white-king.png
│ ├── white-knight.png
│ ├── white-pawn.png
│ ├── white-queen.png
│ └── white-rook.png
│
├── models/ # LLaMA model storage
│ └── llama-2-7b-chat.Q4_K_M.gguf
│
├── ui/ # User interfaces
│ ├── pycache/
│ ├── init.py
│ ├── cli_interface.py # Command-line interface
│ ├── gui.py # GUI main window
│ └── interactive_gui.py # Interactive GUI components
│
├── utils/ # Helper functions
│ ├── init.py
│ └── helpers.py # Utility functions for various modules
│
├── main.py # Main entry point of the project
├── README.md # Project documentation
└── requirements.txt # Python dependencies
```

---

## How It Works

1. **Input**

   * The program takes a chess **position in FEN format** and a **move in SAN notation**.

2. **Prompt Generation**

   * It builds a **concise prompt** for the LLaMA-based language model to generate a comment.
   * The prompt focuses only on **this game’s position** and **positional impact**, ignoring general chess strategy.

3. **Model Evaluation**

   * The LLaMA model reads the prompt and outputs a **short, meaningful comment**.
   * For additional analysis, the program can optionally use **Stockfish** to evaluate move strength.
   * Minor moves are handled with `"Minor positional change."` to avoid empty responses.

4. **Output**

   * The program returns a **1-sentence comment** that tells you how the move affects your or the opponent’s position in this specific game.

---

## Example Usage

```python
from evaluator import evaluate_move

fen = "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 2 3"
move = "Bc4"

comment = evaluate_move(fen, move)
print(comment)
```

**Sample Output:**

```
"Pins the f7 pawn and pressures Black's kingside."
```

---

## Dependencies

* Python 3.10+
* Python packages:

```bash
pip install python-chess torch transformers matplotlib cairosvg stockfish
```

* LLaMA-based language model (HuggingFace checkpoint or `llama.cpp`)

  * Place the model in the `models/` folder and ensure `evaluator.py` can access it.

* Stockfish binary (optional, for additional move evaluation)

  * Make sure Stockfish executable is in your system PATH or in the project folder.

---
## How to Acquire Required Models & Tools

### 1. LLaMA Model

- **HuggingFace:** [https://huggingface.co/models](https://huggingface.co/models)  
  – download a LLaMA checkpoint.

- **llama.cpp:** [https://github.com/ggerganov/llama.cpp](https://github.com/ggerganov/llama.cpp)  
  – follow local inference instructions.

- Place the model in the `models/` folder.

### 2. Stockfish Chess Engine (optional)

- Download from [https://stockfishchess.org/download/](https://stockfishchess.org/download/)  

- Add the binary to your **system PATH** or place it in the project folder.

- Verify installation:

```bash
stockfish
```
### 3. Image Sources

All chessboard and piece images used in this project are acquired from [GreenChess.net](https://greenchess.net).

---


## Resources Used

* **Chess Libraries:** `python-chess` for FEN and SAN handling
* **Language Model:** LLaMA (via HuggingFace or local setup) for generating move comments
* **Chess Engine:** Stockfish for move evaluation
* **Visualization (Optional):** `matplotlib`, `cairosvg` for board diagrams
* **Programming Language:** Python 3.10+

---

## Notes

* Comments are **specific to the game** and position; they do not teach general chess strategy.
* The project is intended for **fast feedback** while analyzing games.
* You can expand it by adding GUI support or batch analysis of games.

---

## License

Open-source project. Feel free to use or modify it for personal projects.

---

*nai™*