from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
from chess_ai import best_move, iterative_deepening  # Your minimax-based AI (if needed)

app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Global board variable
custom_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
#custom_fen = "8/3K4/4P3/8/8/8/6k1/7q w - - 0 1"
board = chess.Board(custom_fen)

@app.route('/move', methods=['POST'])
def make_move():
    global board
    data = request.json  # Get the move from frontend
    
    if "move" not in data:
        return jsonify({"error": "Move not provided."}), 400

    try:
        move = chess.Move.from_uci(data["move"])
        if move in board.legal_moves:
            board.push(move)  # Player move

            # AI move using your minimax-based engine
            ai_move = best_move(board, depth=4)
            #ai_move = iterative_deepening(board, max_depth=7, time_limit=0.5)
            if ai_move:
                board.push(ai_move)
                return jsonify({"ai_move": ai_move.uci()})
            else:
                return jsonify({"message": "AI has no moves left."})
        else:
            return jsonify({"error": "Illegal move"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/evaluate', methods=['POST'])
def evaluate_position():
    global board
    try:
        # Adjust the path to the Stockfish binary as needed.
        engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        # Analyze the board with a short time limit (0.1 seconds)
        info = engine.analyse(board, chess.engine.Limit(time=0.1))
        engine.quit()
        # Extract evaluation (convert to centipawns, use a high value for mate)
        score = info["score"].white().score(mate_score=100000)
        return jsonify({"evaluation": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/reset', methods=['POST'])
def reset_board():
    global board
    custom_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    #custom_fen = "8/3K4/4P3/8/8/8/6k1/7q w - - 0 1"
    board = chess.Board(custom_fen)
    return jsonify({"message": "Board reset to custom position."})


if __name__ == '__main__':
    app.run(debug=True)
