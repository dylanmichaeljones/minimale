"""
Minimax AI engine with Alpha-Beta pruning, move ordering, quiescence search,
piece-square evaluation, and difficulty levels for 5x5 Mini-Chess.
"""
import random
import time
from typing import Optional, Tuple, List, Dict
from board import Board, Move
from constants import (
    WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    PIECE_VALUES, BOARD_SIZE
)

# Positional Piece-Square Tables (5x5) for WHITE
# (Row 0 is Rank 5, Row 4 is Rank 1)

PST_PAWN_WHITE = [
    [  0,   0,   0,   0,   0],  # Row 0: Promotion
    [ 40,  45,  50,  45,  40],  # Row 1: High promotion threat
    [ 15,  20,  30,  20,  15],  # Row 2: Advanced center
    [  0,   5,  15,   5,   0],  # Row 3: Initial rank
    [  0,   0,   0,   0,   0],  # Row 4: Base
]

PST_KNIGHT_WHITE = [
    [-25, -10,  -5, -10, -25],
    [-10,  10,  20,  10, -10],
    [ -5,  20,  35,  20,  -5],
    [-10,  10,  20,  10, -10],
    [-25, -10,  -5, -10, -25],
]

PST_BISHOP_WHITE = [
    [-10,  -5,  -5,  -5, -10],
    [ -5,  10,  15,  10,  -5],
    [ -5,  15,  25,  15,  -5],
    [ -5,  10,  15,  10,  -5],
    [-10,  -5,  -5,  -5, -10],
]

PST_ROOK_WHITE = [
    [ 15,  20,  25,  20,  15],  # 5th rank (enemy back rank)
    [ 10,  15,  20,  15,  10],  # 4th rank
    [  0,   5,  10,   5,   0],
    [  0,   0,   5,   0,   0],
    [  0,   5,  10,   5,   0],
]

PST_QUEEN_WHITE = [
    [-10,  -5,   0,  -5, -10],
    [ -5,   5,  10,   5,  -5],
    [  0,  10,  20,  10,   0],
    [ -5,   5,  10,   5,  -5],
    [-10,  -5,   0,  -5, -10],
]

PST_KING_MID_WHITE = [
    [-30, -30, -30, -30, -30],
    [-20, -20, -20, -20, -20],
    [-10, -10, -10, -10, -10],
    [  5,   5,   0,   0,   5],
    [ 15,  20,  10,  10,  15],  # Safe on back rank
]

PST_KING_END = [
    [-10,  -5,   0,  -5, -10],
    [ -5,  15,  20,  15,  -5],
    [  0,  20,  30,  20,   0],
    [ -5,  15,  20,  15,  -5],
    [-10,  -5,   0,  -5, -10],
]

# Transposition table entry flags
EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

CHECKMATE_SCORE = 100000


class ChessAI:
    def __init__(self, difficulty: str = "keskmine"):
        """
        difficulty: 'lihtne', 'keskmine', 'raske'
        """
        self.difficulty = difficulty.lower()
        self.transposition_table: Dict[str, Tuple[int, int, int, Optional[Move]]] = {}
        self.nodes_evaluated = 0

    def set_difficulty(self, difficulty: str):
        self.difficulty = difficulty.lower()

    def get_search_depth(self) -> int:
        if self.difficulty == "lihtne":
            return 2
        elif self.difficulty == "keskmine":
            return 3
        else:  # 'raske'
            return 4

    def evaluate(self, board: Board) -> int:
        """
        Static evaluation of board from WHITE perspective:
        Positive = White advantage, Negative = Black advantage.
        """
        white_material = 0
        black_material = 0
        pst_score = 0

        # Calculate material and PST
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = board.grid[r][c]
                if p is None:
                    continue

                val = PIECE_VALUES[p.type]
                pst_val = self._get_pst_value(p.type, p.color, r, c)

                if p.color == WHITE:
                    if p.type != KING:
                        white_material += val
                    pst_score += pst_val
                else:
                    if p.type != KING:
                        black_material += val
                    pst_score -= pst_val

        material_diff = white_material - black_material

        # Check bonus
        check_score = 0
        if board.is_in_check(BLACK):
            check_score += 35
        elif board.is_in_check(WHITE):
            check_score -= 35

        return material_diff + pst_score + check_score

    def _get_pst_value(self, piece_type: str, color: int, row: int, col: int) -> int:
        r = row if color == WHITE else (BOARD_SIZE - 1 - row)
        c = col

        if piece_type == PAWN:
            return PST_PAWN_WHITE[r][c]
        elif piece_type == KNIGHT:
            return PST_KNIGHT_WHITE[r][c]
        elif piece_type == BISHOP:
            return PST_BISHOP_WHITE[r][c]
        elif piece_type == ROOK:
            return PST_ROOK_WHITE[r][c]
        elif piece_type == QUEEN:
            return PST_QUEEN_WHITE[r][c]
        elif piece_type == KING:
            return PST_KING_MID_WHITE[r][c]
        return 0

    def _score_move_for_ordering(self, move: Move, tt_move: Optional[Move] = None) -> int:
        """Scores a move for optimal alpha-beta branch ordering."""
        # 1. Best move from transposition table
        if tt_move is not None:
            if move.from_pos == tt_move.from_pos and move.to_pos == tt_move.to_pos and move.promotion == tt_move.promotion:
                return 1000000

        score = 0
        # 2. Captures scored by MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
        if move.piece_captured is not None:
            victim_val = PIECE_VALUES[move.piece_captured.type]
            aggressor_val = PIECE_VALUES[move.piece_moved.type]
            score += 10000 + (victim_val * 10 - aggressor_val)

        # 3. Promotions
        if move.promotion is not None:
            score += 8000 + PIECE_VALUES[move.promotion]

        return score

    def order_moves(self, board: Board, moves: List[Move], tt_move: Optional[Move] = None) -> List[Move]:
        return sorted(moves, key=lambda m: self._score_move_for_ordering(m, tt_move), reverse=True)

    def quiescence(self, board: Board, alpha: int, beta: int, max_q_depth: int = 3) -> int:
        """Quiescence search to evaluate captures and avoid the horizon effect."""
        self.nodes_evaluated += 1
        stand_pat = self.evaluate(board) if board.turn == WHITE else -self.evaluate(board)

        if max_q_depth <= 0:
            return stand_pat

        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        # Generate and search only capture moves
        legal_moves = board.get_legal_moves()
        capture_moves = [m for m in legal_moves if m.piece_captured is not None or m.promotion is not None]
        capture_moves = self.order_moves(board, capture_moves)

        for move in capture_moves:
            board.make_move(move)
            score = -self.quiescence(board, -beta, -alpha, max_q_depth - 1)
            board.undo_move()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score

        return alpha

    def minimax(self, board: Board, depth: int, alpha: int, beta: int, is_root: bool = False) -> Tuple[int, Optional[Move]]:
        """
        Negamax formulation with Alpha-Beta pruning and Transposition Table.
        Returns (score_from_current_player_perspective, best_move).
        """
        self.nodes_evaluated += 1
        pos_key = board.get_position_key()
        alpha_orig = alpha

        # Transposition table lookup
        tt_entry = self.transposition_table.get(pos_key)
        tt_move = None
        if tt_entry is not None:
            tt_depth, tt_score, tt_flag, tt_move = tt_entry
            if not is_root and tt_depth >= depth:
                if tt_flag == EXACT:
                    return tt_score, tt_move
                elif tt_flag == LOWERBOUND:
                    alpha = max(alpha, tt_score)
                elif tt_flag == UPPERBOUND:
                    beta = min(beta, tt_score)
                if alpha >= beta:
                    return tt_score, tt_move

        # Check game over conditions
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            if board.is_in_check(board.turn):
                # Checkmate: favor shorter mate paths
                return -(CHECKMATE_SCORE + depth), None
            else:
                # Stalemate: draw
                return 0, None

        if board.is_threefold_repetition() or board.is_insufficient_material() or board.is_fifty_move_rule():
            return 0, None

        # Leaf node reached: evaluate quiescence or static eval
        if depth == 0:
            if self.difficulty == "raske":
                q_score = self.quiescence(board, alpha, beta, max_q_depth=3)
                return q_score, None
            else:
                eval_score = self.evaluate(board) if board.turn == WHITE else -self.evaluate(board)
                return eval_score, None

        ordered_moves = self.order_moves(board, legal_moves, tt_move)
        best_move = ordered_moves[0]
        best_score = -float('inf')

        for move in ordered_moves:
            board.make_move(move)
            score, _ = self.minimax(board, depth - 1, -beta, -alpha, is_root=False)
            score = -score
            board.undo_move()

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)
            if alpha >= beta:
                break  # Beta cutoff

        # Store in transposition table
        tt_flag = EXACT
        if best_score <= alpha_orig:
            tt_flag = UPPERBOUND
        elif best_score >= beta:
            tt_flag = LOWERBOUND

        self.transposition_table[pos_key] = (depth, int(best_score), tt_flag, best_move)
        return int(best_score), best_move

    def get_best_move(self, board: Board) -> Optional[Move]:
        """
        Determines the best move for the current player on the board.
        Applies difficulty tuning (randomness on easy, full depth on hard).
        """
        legal_moves = board.get_legal_moves()
        if not legal_moves:
            return None

        # If only 1 legal move, take it immediately
        if len(legal_moves) == 1:
            return legal_moves[0]

        depth = self.get_search_depth()
        self.nodes_evaluated = 0
        start_time = time.perf_counter()

        # On 'lihtne' (Easy), evaluate all moves at depth 1-2 and pick among top 3
        if self.difficulty == "lihtne":
            scored_moves = []
            for move in legal_moves:
                board.make_move(move)
                score, _ = self.minimax(board, depth - 1, -float('inf'), float('inf'))
                score = -score
                board.undo_move()
                scored_moves.append((score, move))

            scored_moves.sort(key=lambda x: x[0], reverse=True)
            # Pick from top 2 or 3 moves with 70% probability for best move
            top_candidates = scored_moves[:min(3, len(scored_moves))]
            weights = [0.65, 0.25, 0.10][:len(top_candidates)]
            norm_weights = [w / sum(weights) for w in weights]
            chosen = random.choices(top_candidates, weights=norm_weights, k=1)[0][1]
            return chosen

        # Medium or Hard: Run Negamax with Alpha-Beta
        score, best_move = self.minimax(board, depth, -float('inf'), float('inf'), is_root=True)

        elapsed = time.perf_counter() - start_time
        # print(f"AI searched {self.nodes_evaluated} nodes in {elapsed:.3f}s, eval={score}, move={best_move}")

        return best_move if best_move is not None else random.choice(legal_moves)
