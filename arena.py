import chess
import chess.engine
import random
import time
from chess_ai import best_move, iterative_deepening

# Configuration
NUM_GAMES = 10
TIME_LIMIT = 0.5  # Seconds per move for your bot
MAX_MOVES = 150   # Prevent infinite games

def get_random_move(board):
    return random.choice(list(board.legal_moves))

def get_stockfish_move(board, engine, limit=0.1):
    result = engine.play(board, chess.engine.Limit(time=limit))
    return result.move

def play_game(game_id, white_player="my_bot", black_player="random"):
    board = chess.Board()
    moves_played = 0
    
    # Setup Stockfish if needed
    engine = None
    if "stockfish" in [white_player, black_player]:
        # UPDATE THIS PATH to your local stockfish installation
        try:
            engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        except:
            print("Stockfish not found. Falling back to random.")
            if white_player == "stockfish": white_player = "random"
            if black_player == "stockfish": black_player = "random"

    print(f"--- Game {game_id + 1} ({white_player} vs {black_player}) ---")

    while not board.is_game_over() and moves_played < MAX_MOVES:
        # Determine whose turn it is
        current_player = white_player if board.turn == chess.WHITE else black_player
        
        start = time.time()
        
        # --- SELECT MOVE ---
        if current_player == "my_bot1":
            # Using your iterative deepening function
            move = best_move(board, depth=3)
            # Fallback if AI returns None (bug safety)
            if move is None:
                print("Bot returned None, picking random.")
                move = get_random_move(board)

        elif current_player == "my_bot2":
            move = iterative_deepening(board, max_depth=4, time_limit=TIME_LIMIT)

            if move is None:
                print("Bot returned None, picking random.")
                move = get_random_move(board)
                
        elif current_player == "random":
            move = get_random_move(board)
            
        elif current_player == "stockfish":
            move = get_stockfish_move(board, engine)

        # --- APPLY MOVE ---
        board.push(move)
        moves_played += 1
        
        # Optional: Print board every 10 moves to show progress
        # if moves_played % 10 == 0:
        #    print(f"Move {moves_played}:\n{board}")

    # --- GAME OVER ---
    if engine: engine.quit()
    
    result = board.result()
    print(f"Game Over in {moves_played} moves. Result: {result}")
    
    # Return winner color: '1-0' (White), '0-1' (Black), '1/2-1/2' (Draw)
    return result

def run_tournament():
    results = {"white_wins": 0, "black_wins": 0, "draws": 0}
    
    for i in range(NUM_GAMES):
        # CHANGE THESE to "my_bot", "random", or "stockfish"
        outcome = play_game(i, white_player="my_bot1", black_player="random")
        
        if outcome == "1-0":
            results["white_wins"] += 1
        elif outcome == "0-1":
            results["black_wins"] += 1
        else:
            results["draws"] += 1
            
    print("\n--- TOURNAMENT RESULTS ---")
    print(f"Total Games: {NUM_GAMES}")
    print(f"White Wins: {results['white_wins']}")
    print(f"Black Wins: {results['black_wins']}")
    print(f"Draws:      {results['draws']}")

if __name__ == "__main__":
    run_tournament()