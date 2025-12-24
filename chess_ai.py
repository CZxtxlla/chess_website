import chess
import chess.polyglot
import time


"""
minimax chess bot/ai
next stuff to implement:
- alpha-beta pruning X
- ordering moves X
- improved evaluation function
    > piece-square tables X
- transpositions
- iterative deepening


"""

transposition_table = {}

#piece-square tables

# pawn
pawn_table = [0,  0,  0,  0,  0,  0,  0,  0,
              50, 50, 50, 50, 50, 50, 50, 50,
              10, 10, 20, 30, 30, 20, 10, 10,
              5,  5, 10, 25, 25, 10,  5,  5,
              0,  0,  0, 20, 20,  0,  0,  0,
              5, -5,-10,  0,  0,-10, -5,  5,
              5, 10, 10,-20,-20, 10, 10,  5,
              0,  0,  0,  0,  0,  0,  0,  0]

# knight
knight_table = [-50,-40,-30,-30,-30,-30,-40,-50,
                -40,-20,  0,  0,  0,  0,-20,-40,
                -30,  0, 10, 15, 15, 10,  0,-30,
                -30,  5, 15, 20, 20, 15,  5,-30,
                -30,  0, 15, 20, 20, 15,  0,-30,
                -30,  5, 10, 15, 15, 10,  5,-30,
                -40,-20,  0,  5,  5,  0,-20,-40,
                -50,-40,-30,-30,-30,-30,-40,-50]

# bishop
bishop_table = [-20,-10,-10,-10,-10,-10,-10,-20,
                -10,  0,  0,  0,  0,  0,  0,-10,
                -10,  0,  5, 10, 10,  5,  0,-10,
                -10,  5,  5, 10, 10,  5,  5,-10,
                -10,  0, 10, 10, 10, 10,  0,-10,
                -10, 10, 10, 10, 10, 10, 10,-10,
                -10,  5,  0,  0,  0,  0,  5,-10,
                -20,-10,-10,-10,-10,-10,-10,-20]

# rook
rook_table = [0,  0,  0,  0,  0,  0,  0,  0,
              5, 10, 10, 10, 10, 10, 10,  5,
              -5,  0,  0,  0,  0,  0,  0, -5,
              -5,  0,  0,  0,  0,  0,  0, -5,
              -5,  0,  0,  0,  0,  0,  0, -5,
              -5,  0,  0,  0,  0,  0,  0, -5,
              -5,  0,  0,  0,  0,  0,  0, -5,
              0,  0,  0,  5,  5,  0,  0,  0]

# queen
queen_table = [-20,-10,-10, -5, -5,-10,-10,-20,
-10,  0,  0,  0,  0,  0,  0,-10,
-10,  0,  5,  5,  5,  5,  0,-10,
 -5,  0,  5,  5,  5,  5,  0, -5,
  0,  0,  5,  5,  5,  5,  0, -5,
-10,  5,  5,  5,  5,  5,  0,-10,
-10,  0,  5,  0,  0,  0,  0,-10,
-20,-10,-10, -5, -5,-10,-10,-20]

# king
king_table = [-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-30,-40,-40,-50,-50,-40,-40,-30,
-20,-30,-30,-40,-40,-30,-30,-20,
-10,-20,-20,-20,-20,-20,-20,-10,
 20, 20,  0,  0,  0,  0, 20, 20,
 20, 30, 10,  0,  0, 10, 30, 20]

#king endgame
king_endgame_table = [
-50,-40,-30,-20,-20,-30,-40,-50,
-30,-20,-10,  0,  0,-10,-20,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 30, 40, 40, 30,-10,-30,
-30,-10, 20, 30, 30, 20,-10,-30,
-30,-30,  0,  0,  0,  0,-30,-30,
-50,-30,-30,-30,-30,-30,-30,-50]

def endgame_weight(board):
    """
    Returns a weight for the endgame based on the number of non-pawn pieces left
    """
    pieces = board.piece_map().values()
    num_non_pawn_pieces = 0
    num_of_queens = 0

    for piece in pieces:
        if piece.piece_type != chess.PAWN:
            num_non_pawn_pieces += 1
            if piece.piece_type == chess.QUEEN:
                num_of_queens += 1
    """
    if num_non_pawn_pieces <= 12:
        score = min(-2* (num_non_pawn_pieces-12)/12, 1)
    else:
        score = 0
    return score
    """
    if (num_non_pawn_pieces <= 8 and num_of_queens == 0) or num_non_pawn_pieces <= 6:
        return 1
    elif num_non_pawn_pieces <= 10:
        return 0.5
    else:
        return 0


def piece_square_value(board, piece, square, color, weight):
    """
    Returns the piece-square value for a given piece and square
    """
    if color == chess.WHITE:
        square = chess.square_mirror(square)
    if piece == chess.PAWN:
        if weight >= 0.7:
            return 2 * pawn_table[square]
        return pawn_table[square]
    elif piece == chess.KNIGHT:
        return knight_table[square]
    elif piece == chess.BISHOP:
        return bishop_table[square]
    elif piece == chess.ROOK:
        return rook_table[square]
    elif piece == chess.QUEEN:
        return queen_table[square]
    elif piece == chess.KING:
        if weight >= 0.9:
            return 0.5 * king_endgame_table[square]
        return king_table[square]
    return 0

def force_king_to_corner_endgame(board, weight):
    """
    Forces the enemy king to the corner in the endgame by encouraging central control
    """
    
    opponent_king_square = board.king(not board.turn)  # Get opponent's king square
    opponent_king_rank = chess.square_rank(opponent_king_square)
    opponent_king_file = chess.square_file(opponent_king_square)
    
    # Distance to the center of the board
    opponent_king_dist_to_centre_file = max(3 - opponent_king_file, opponent_king_file - 4)
    opponent_king_dist_to_centre_rank = max(3 - opponent_king_rank, opponent_king_rank - 4)
    opponent_king_dist_to_centre = opponent_king_dist_to_centre_file + opponent_king_dist_to_centre_rank
    
    # Encouraging distance from center (forcing to corner)
    evaluation = opponent_king_dist_to_centre  

    friendly_king_square = board.king(board.turn)  # Get friendly king square
    friendly_king_rank = chess.square_rank(friendly_king_square)
    friendly_king_file = chess.square_file(friendly_king_square)

    # Manhattan distance between kings
    dist_between_kings = abs(friendly_king_file - opponent_king_file) + abs(friendly_king_rank - opponent_king_rank)
    
    # Encouraging kings to be closer (to box opponent in)
    evaluation += 14 - dist_between_kings

    return evaluation * weight




def evaluate_board(board):
    """
    Simple evaluation: count material, piece-square values, and endgame weight
    """
    values = {
        chess.PAWN: 100, 
        chess.KNIGHT: 320, 
        chess.BISHOP: 330, 
        chess.ROOK: 500, 
        chess.QUEEN: 900
    }
    if board.is_checkmate():
        return -9999999 if board.turn == chess.WHITE else 9999999
    if board.is_stalemate():
        return 0
    if board.is_fivefold_repetition():
        return 0
    score = 0
    for piece, value in values.items():
        score += len(board.pieces(piece, chess.WHITE)) * value
        score -= len(board.pieces(piece, chess.BLACK)) * value
    
    # Add piece-square values
    weight = endgame_weight(board)
    multiplier = 1
    for square, piece in board.piece_map().items():
        if piece.color == chess.WHITE:
            score += multiplier * piece_square_value(board, piece.piece_type, square, piece.color, weight)
        else:
            score -= multiplier * piece_square_value(board, piece.piece_type, square, piece.color, weight)
    if board.turn == chess.WHITE:
        score += force_king_to_corner_endgame(board, weight)
    else:
        score -= force_king_to_corner_endgame(board, weight)
    return score

def order_moves(board, moves):
    """Orders moves based on captures and checks for better alpha-beta pruning"""

    values = {
        chess.PAWN: 100, 
        chess.KNIGHT: 320, 
        chess.BISHOP: 330, 
        chess.ROOK: 500, 
        chess.QUEEN: 900
    }

    def is_square_attacked_by_pawn(board, square, color):
        if color == chess.WHITE:
            # For a white piece, enemy pawns (black) would be one rank ahead (i.e. rank+1)
            attack_offsets = [-9, -7]  # relative offsets for black pawns (since board squares increase upward)
        else:
            attack_offsets = [7, 9]    # for black pieces, enemy white pawns attack downward
        
        for offset in attack_offsets:
            attacker_square = square + offset
            if 0 <= attacker_square < 64:
                attacker = board.piece_at(attacker_square)
                if attacker and attacker.piece_type == chess.PAWN and attacker.color != color:
                    return True
        return False

    def move_value(move):
        score = 0
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                captured_value = values.get(captured_piece.piece_type, 0)  # Default to 0 if piece is not found in values
                moved_piece = board.piece_at(move.from_square)
                moved_value = values.get(moved_piece.piece_type, 0)  # Default to 0 if piece is not found in values
                score = 10 * captured_value - moved_value  # Prioritize captures
        if move.promotion:
            score += values.get(move.promotion, 0)  # Prioritize promotions based on piece value
        if is_square_attacked_by_pawn(board, move.to_square, board.turn):
            moved_piece = board.piece_at(move.from_square)
            moved_value = values.get(moved_piece.piece_type, 0)  # Default to 0 if piece is not found in values
            score -= moved_value  # Penalize moves that land on squares attacked by pawns
        return score

    return sorted(moves, key=move_value, reverse=True)

def quiescence(board, alpha, beta, maximizing):
    score = evaluate_board(board)
    # For a maximizing node, a high evaluation is good;
    # for a minimizing node, a low evaluation is good.
    if maximizing:
        if score >= beta:
            return beta
        if alpha < score:
            alpha = score
    else:
        if score <= alpha:
            return alpha
        if beta > score:
            beta = score

    # Only consider capture moves.
    capture_moves = [move for move in board.legal_moves if board.is_capture(move)]
    capture_moves = order_moves(board, capture_moves)

    if maximizing:
        for move in capture_moves:
            board.push(move)
            score = quiescence(board, alpha, beta, False)
            board.pop()
            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha
    else:
        for move in capture_moves:
            board.push(move)
            score = quiescence(board, alpha, beta, True)
            board.pop()
            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta



def minimax(board, depth, alpha, beta, maximizing):
    global minimax_calls
    global transpositions
    minimax_calls += 1
    alpha_orig = alpha
    beta_orig = beta
    
    # Use Zobrist hash
    key = chess.polyglot.zobrist_hash(board)

    # Check the transposition table.
    if key in transposition_table:
        entry = transposition_table[key]
        transpositions += 1
        if entry['depth'] >= depth:
            if entry['flag'] == "EXACT":
                return entry['score']
            elif entry['flag'] == "LOWERBOUND":
                alpha = max(alpha, entry['score'])
            elif entry['flag'] == "UPPERBOUND":
                beta = min(beta, entry['score'])
            if alpha >= beta:
                return entry['score']

    # Terminal condition: leaf node
    if depth == 0 or board.is_game_over():
        if board.is_checkmate():
            score = -9999999 - (10 * depth) if board.turn == chess.WHITE else 9999999 + (10 * depth)
        elif board.is_fivefold_repetition() or board.is_stalemate():
            score = 0
        else:
            score = quiescence(board, alpha, beta, maximizing)
        transposition_table[key] = {"depth": depth, "score": score, "flag": "EXACT"}
        return score

    # Maximizing player's turn.
    if maximizing:
        max_eval = float('-inf')
        moves = order_moves(board, board.legal_moves)
        if not moves:
            if board.is_checkmate():
                score = -9999999 - (10 * depth) if board.turn == chess.WHITE else 9999999 + (10 * depth)
            else:
                score = 0
            transposition_table[key] = {"depth": depth, "score": score, "flag": "EXACT"}
            return score

        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:  # Alpha-beta cutoff.
                break
        score = max_eval

    # Minimizing player's turn.
    else:
        min_eval = float('inf')
        moves = order_moves(board, board.legal_moves)
        if not moves:
            if board.is_checkmate():
                score = -9999999 - (10 * depth) if board.turn == chess.WHITE else 9999999 + (10 * depth)
            else:
                score = 0
            transposition_table[key] = {"depth": depth, "score": score, "flag": "EXACT"}
            return score

        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:  # Alpha-beta cutoff.
                break
        score = min_eval

    
    # Determine the flag for the transposition table entry.
    if score <= alpha_orig:
        flag = "UPPERBOUND"
    elif score >= beta_orig:
        flag = "LOWERBOUND"
    else:
        flag = "EXACT"

    transposition_table[key] = {"depth": depth, "score": score, "flag": flag}
    
    return score

def iterative_deepening(board, max_depth, time_limit=None):
    """
    Iteratively deepens the search to a maximum depth or until the time limit is reached
    """
    
    best_move_found = None
    start_time = time.time()
    
    for current_depth in range(1, max_depth + 1):
        # Check if time limit exceeded
        if time_limit and (time.time() - start_time) > time_limit:
            print("Time limit reached at depth:", current_depth)
            break
        
        print(f"Searching at depth {current_depth}...")
        current_best = best_move(board, depth=current_depth)
        if current_best is not None:
            best_move_found = current_best
        print(f"Depth {current_depth}: Best move so far: {best_move_found}")
    
    return best_move_found


def best_move(board, depth):
    """
    Find the best move using Minimax
    """
    global minimax_calls
    global transpositions
    minimax_calls = 0
    transpositions = 0
    moves = order_moves(board, board.legal_moves)
    if board.turn == chess.WHITE:
        best = None
        max_eval = float('-inf')
        alpha = float('-inf')
        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, float('inf'), False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best = move
            alpha = max(alpha, eval_score)
        print("max eval {}".format(max_eval))
        print("number of calls {}".format(minimax_calls))
        return best
    else:
        best = None
        min_eval = float('inf')
        beta = float('inf')
        for move in moves:
            board.push(move)
            eval_score = minimax(board, depth - 1, -float('inf'), beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best = move
            beta = min(beta, eval_score)
        print("min eval {}".format(min_eval))
        print("best move {}".format(best))
        print("number of calls {}".format(minimax_calls))
        print("number of transpositions {}".format(transpositions))
        return best
    
if __name__ == "__main__":
    # Initialize a chess board
    board = chess.Board()

    # Print the starting position of the board
    print("Starting position:\n")
    print(board)

    # Play a game for a few moves with the bot making moves
    while not board.is_game_over():
        print("\nCurrent board position:")
        print(board)

        # Get the best move from the bot (AI)
        move = iterative_deepening(board, max_depth=10, time_limit=10)
        
        # Print the move of the bot
        print(f"Bot plays: {move}")
        
        # Make the move on the board
        board.push(move)

        if not board.is_game_over():
            print("Opponent's turn...")

    # Print the final board position and the result of the game
    print("\nGame over!")
    print(board)
    print(f"Result: {board.result()}")