"""
Board representation, piece movement, move validation, and game state management for 5x5 Mini-Chess.
"""
from dataclasses import dataclass
from typing import Optional, List, Tuple, Dict
from constants import (
    BOARD_SIZE, WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    INITIAL_LAYOUT, pos_to_coord, PIECE_SYMBOLS_ET, COLOR_NAMES_ET
)


@dataclass(frozen=True)
class Piece:
    type: str  # 'P', 'N', 'B', 'R', 'Q', 'K'
    color: int  # WHITE (1) or BLACK (-1)

    def __repr__(self) -> str:
        s = self.type.upper() if self.color == WHITE else self.type.lower()
        return s


@dataclass
class Move:
    from_pos: Tuple[int, int]  # (row, col)
    to_pos: Tuple[int, int]    # (row, col)
    piece_moved: Piece
    piece_captured: Optional[Piece] = None
    promotion: Optional[str] = None  # 'Q', 'R', 'B', 'N'
    san: Optional[str] = None

    def __repr__(self) -> str:
        f = pos_to_coord(*self.from_pos)
        t = pos_to_coord(*self.to_pos)
        promo = f"={self.promotion}" if self.promotion else ""
        return f"{self.piece_moved.type}{f}->{t}{promo}"


class Board:
    def __init__(self, setup_initial: bool = True):
        self.grid: List[List[Optional[Piece]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn: int = WHITE
        self.move_history: List[Move] = []
        self.position_history: List[str] = []
        self.white_king_pos: Tuple[int, int] = (4, 4)
        self.black_king_pos: Tuple[int, int] = (0, 4)
        self.halfmove_clock: int = 0
        self.halfmove_history: List[int] = []
        self.captured_pieces: Dict[int, List[Piece]] = {WHITE: [], BLACK: []}

        if setup_initial:
            self.setup_initial_board()

    def setup_initial_board(self):
        """Initializes the standard 5x5 Gardner minichess layout."""
        self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = WHITE
        self.move_history.clear()
        self.position_history.clear()
        self.halfmove_clock = 0
        self.halfmove_history.clear()
        self.captured_pieces = {WHITE: [], BLACK: []}

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                item = INITIAL_LAYOUT[r][c]
                if item is not None:
                    p_type, p_color = item
                    piece = Piece(p_type, p_color)
                    self.grid[r][c] = piece
                    if p_type == KING:
                        if p_color == WHITE:
                            self.white_king_pos = (r, c)
                        else:
                            self.black_king_pos = (r, c)

        self.position_history.append(self.get_position_key())

    def clone(self) -> 'Board':
        """Creates an independent copy of the board state for fast AI search."""
        b = Board(setup_initial=False)
        b.grid = [[self.grid[r][c] for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]
        b.turn = self.turn
        b.white_king_pos = self.white_king_pos
        b.black_king_pos = self.black_king_pos
        b.halfmove_clock = self.halfmove_clock
        b.position_history = list(self.position_history)
        b.captured_pieces = {
            WHITE: list(self.captured_pieces[WHITE]),
            BLACK: list(self.captured_pieces[BLACK])
        }
        return b

    @staticmethod
    def is_valid_square(row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        if not self.is_valid_square(row, col):
            return None
        return self.grid[row][col]

    def get_position_key(self) -> str:
        """Compact string key representing current board layout and side to move."""
        rows = []
        for r in range(BOARD_SIZE):
            row_str = []
            empty_count = 0
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is None:
                    empty_count += 1
                else:
                    if empty_count > 0:
                        row_str.append(str(empty_count))
                        empty_count = 0
                    row_str.append(repr(p))
            if empty_count > 0:
                row_str.append(str(empty_count))
            rows.append("".join(row_str))
        turn_str = 'w' if self.turn == WHITE else 'b'
        return "/".join(rows) + f" {turn_str}"

    def is_square_attacked(self, row: int, col: int, attacker_color: int) -> bool:
        """Ultra-fast reverse attack detection: is (row, col) attacked by attacker_color?"""
        # 1. Pawn attacks:
        # A white pawn attacks upward (row - 1), so attacker white pawn is at row + 1.
        # A black pawn attacks downward (row + 1), so attacker black pawn is at row - 1.
        pawn_attacker_row = row + 1 if attacker_color == WHITE else row - 1
        for pawn_attacker_col in (col - 1, col + 1):
            if self.is_valid_square(pawn_attacker_row, pawn_attacker_col):
                p = self.grid[pawn_attacker_row][pawn_attacker_col]
                if p is not None and p.color == attacker_color and p.type == PAWN:
                    return True

        # 2. Knight attacks:
        knight_offsets = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        for dr, dc in knight_offsets:
            r, c = row + dr, col + dc
            if self.is_valid_square(r, c):
                p = self.grid[r][c]
                if p is not None and p.color == attacker_color and p.type == KNIGHT:
                    return True

        # 3. King attacks (adjacent):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                r, c = row + dr, col + dc
                if self.is_valid_square(r, c):
                    p = self.grid[r][c]
                    if p is not None and p.color == attacker_color and p.type == KING:
                        return True

        # 4. Orthogonal ray attacks (Rook or Queen):
        ortho_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in ortho_dirs:
            r, c = row + dr, col + dc
            while self.is_valid_square(r, c):
                p = self.grid[r][c]
                if p is not None:
                    if p.color == attacker_color and p.type in (ROOK, QUEEN):
                        return True
                    break
                r += dr
                c += dc

        # 5. Diagonal ray attacks (Bishop or Queen):
        diag_dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dr, dc in diag_dirs:
            r, c = row + dr, col + dc
            while self.is_valid_square(r, c):
                p = self.grid[r][c]
                if p is not None:
                    if p.color == attacker_color and p.type in (BISHOP, QUEEN):
                        return True
                    break
                r += dr
                c += dc

        return False

    def is_in_check(self, color: int) -> bool:
        """Determines if the king of the given color is in check."""
        king_pos = self.white_king_pos if color == WHITE else self.black_king_pos
        return self.is_square_attacked(king_pos[0], king_pos[1], -color)

    def get_pseudo_legal_moves(self, color: Optional[int] = None) -> List[Move]:
        """Generates all pseudo-legal moves for pieces of the given color."""
        if color is None:
            color = self.turn

        moves: List[Move] = []
        pawn_dir = -1 if color == WHITE else 1
        promo_row = 0 if color == WHITE else 4

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is None or p.color != color:
                    continue

                p_type = p.type

                if p_type == PAWN:
                    # 1 step forward (empty)
                    fwd_r = r + pawn_dir
                    if self.is_valid_square(fwd_r, c) and self.grid[fwd_r][c] is None:
                        if fwd_r == promo_row:
                            for promo in (QUEEN, KNIGHT, ROOK, BISHOP):
                                moves.append(Move((r, c), (fwd_r, c), p, None, promo))
                        else:
                            moves.append(Move((r, c), (fwd_r, c), p, None, None))

                    # Diagonal captures
                    for dc in (-1, 1):
                        cap_c = c + dc
                        if self.is_valid_square(fwd_r, cap_c):
                            target = self.grid[fwd_r][cap_c]
                            if target is not None and target.color != color:
                                if fwd_r == promo_row:
                                    for promo in (QUEEN, KNIGHT, ROOK, BISHOP):
                                        moves.append(Move((r, c), (fwd_r, cap_c), p, target, promo))
                                else:
                                    moves.append(Move((r, c), (fwd_r, cap_c), p, target, None))

                elif p_type == KNIGHT:
                    for dr, dc in [
                        (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                        (1, -2), (1, 2), (2, -1), (2, 1)
                    ]:
                        nr, nc = r + dr, c + dc
                        if self.is_valid_square(nr, nc):
                            target = self.grid[nr][nc]
                            if target is None or target.color != color:
                                moves.append(Move((r, c), (nr, nc), p, target, None))

                elif p_type in (BISHOP, ROOK, QUEEN):
                    rays = []
                    if p_type in (BISHOP, QUEEN):
                        rays.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
                    if p_type in (ROOK, QUEEN):
                        rays.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])

                    for dr, dc in rays:
                        nr, nc = r + dr, c + dc
                        while self.is_valid_square(nr, nc):
                            target = self.grid[nr][nc]
                            if target is None:
                                moves.append(Move((r, c), (nr, nc), p, None, None))
                            elif target.color != color:
                                moves.append(Move((r, c), (nr, nc), p, target, None))
                                break
                            else:
                                break
                            nr += dr
                            nc += dc

                elif p_type == KING:
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if self.is_valid_square(nr, nc):
                                target = self.grid[nr][nc]
                                if target is None or target.color != color:
                                    moves.append(Move((r, c), (nr, nc), p, target, None))

        return moves

    def make_move(self, move: Move) -> None:
        """Executes a move on the board."""
        fr, fc = move.from_pos
        tr, tc = move.to_pos

        self.grid[fr][fc] = None

        if move.promotion:
            placed_piece = Piece(move.promotion, move.piece_moved.color)
        else:
            placed_piece = move.piece_moved

        self.grid[tr][tc] = placed_piece

        if move.piece_moved.type == KING:
            if move.piece_moved.color == WHITE:
                self.white_king_pos = (tr, tc)
            else:
                self.black_king_pos = (tr, tc)

        if move.piece_captured:
            self.captured_pieces[move.piece_moved.color].append(move.piece_captured)

        self.halfmove_history.append(self.halfmove_clock)
        if move.piece_moved.type == PAWN or move.piece_captured is not None:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        self.move_history.append(move)
        self.turn = -self.turn
        self.position_history.append(self.get_position_key())

    def undo_move(self) -> Optional[Move]:
        """Undoes the most recent move and restores previous state."""
        if not self.move_history:
            return None

        move = self.move_history.pop()
        self.position_history.pop()
        self.halfmove_clock = self.halfmove_history.pop()
        self.turn = -self.turn

        fr, fc = move.from_pos
        tr, tc = move.to_pos

        self.grid[fr][fc] = move.piece_moved
        self.grid[tr][tc] = move.piece_captured

        if move.piece_moved.type == KING:
            if move.piece_moved.color == WHITE:
                self.white_king_pos = (fr, fc)
            else:
                self.black_king_pos = (fr, fc)

        if move.piece_captured:
            self.captured_pieces[move.piece_moved.color].pop()

        return move

    def get_legal_moves(self, color: Optional[int] = None) -> List[Move]:
        """Returns all fully legal moves for the given color (does not leave king in check)."""
        if color is None:
            color = self.turn

        pseudo_moves = self.get_pseudo_legal_moves(color)
        legal_moves: List[Move] = []

        for move in pseudo_moves:
            self.make_move(move)
            # The player who just moved is -self.turn
            if not self.is_in_check(-self.turn):
                legal_moves.append(move)
            self.undo_move()

        return legal_moves

    def is_checkmate(self) -> bool:
        """Returns True if the current player is in checkmate."""
        return self.is_in_check(self.turn) and len(self.get_legal_moves()) == 0

    def is_stalemate(self) -> bool:
        """Returns True if the current player is stalemated (no legal moves, not in check)."""
        return not self.is_in_check(self.turn) and len(self.get_legal_moves()) == 0

    def is_threefold_repetition(self) -> bool:
        """Checks if current position has appeared 3 times in history."""
        curr_key = self.position_history[-1] if self.position_history else ""
        return self.position_history.count(curr_key) >= 3

    def is_insufficient_material(self) -> bool:
        """Checks if both sides lack sufficient material to checkmate."""
        pieces = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None:
                    pieces.append(p)

        # King vs King
        if len(pieces) == 2:
            return True

        # King + Minor vs King
        if len(pieces) == 3:
            types = {p.type for p in pieces}
            if KNIGHT in types or BISHOP in types:
                return True

        return False

    def is_fifty_move_rule(self) -> bool:
        """Checks 50-move rule (50 halfmoves without capture or pawn push)."""
        return self.halfmove_clock >= 50

    def get_game_status(self) -> Tuple[bool, str, Optional[int]]:
        """
        Returns (is_game_over, status_message_in_estonian, winner_color)
        """
        if self.is_checkmate():
            winner = -self.turn
            winner_name = COLOR_NAMES_ET[winner]
            return True, f"Matt! {winner_name} võitis!", winner

        if self.is_stalemate():
            return True, "Patt! Mäng on viigis.", None

        if self.is_threefold_repetition():
            return True, "Viik kolmekordse käigukorduse tõttu!", None

        if self.is_insufficient_material():
            return True, "Viik (ebapiisav materjal matiks)!", None

        if self.is_fifty_move_rule():
            return True, "Viik 50 käigu reegli tõttu!", None

        if self.is_in_check(self.turn):
            curr_name = COLOR_NAMES_ET[self.turn]
            return False, f"Šahh! {curr_name} on tule all.", None

        curr_name = COLOR_NAMES_ET[self.turn]
        return False, f"{curr_name} käik", None

    def record_move_san(self, move: Move) -> str:
        """Computes and caches Estonian algebraic notation without mutating board."""
        symbol = PIECE_SYMBOLS_ET[move.piece_moved.type]
        sep = "x" if move.piece_captured is not None else "-"
        from_str = pos_to_coord(*move.from_pos).lower()
        to_str = pos_to_coord(*move.to_pos).lower()
        promo_str = f"={PIECE_SYMBOLS_ET.get(move.promotion, move.promotion)}" if move.promotion else ""

        check_suffix = ""
        if self.is_checkmate():
            check_suffix = "#"
        elif self.is_in_check(self.turn):
            check_suffix = "+"

        san = f"{symbol}{from_str}{sep}{to_str}{promo_str}{check_suffix}"
        move.san = san
        return san

    def format_move_algebraic(self, move: Move) -> str:
        """Formats a move into Estonian algebraic notation safely without mutating board."""
        if hasattr(move, 'san') and move.san:
            return move.san
        return self.record_move_san(move)

    def get_material_balance(self) -> int:
        """Returns material count: positive = White advantage, negative = Black advantage."""
        from constants import PIECE_VALUES
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                p = self.grid[r][c]
                if p is not None and p.type != KING:
                    val = PIECE_VALUES[p.type]
                    score += val if p.color == WHITE else -val
        return score
