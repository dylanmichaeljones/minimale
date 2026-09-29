"""
Unit tests for 5x5 board mechanics, move validation, check/mate, and undo.
"""
from board import Board, Piece, Move
from constants import (
    WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    pos_to_coord, coord_to_pos
)


def test_initial_layout():
    b = Board()
    assert b.turn == WHITE
    assert b.white_king_pos == (4, 4)
    assert b.black_king_pos == (0, 4)

    # Check rank 1 (row 4): R, N, B, Q, K
    expected_row4 = [ROOK, KNIGHT, BISHOP, QUEEN, KING]
    for c in range(5):
        p = b.grid[4][c]
        assert p is not None
        assert p.color == WHITE
        assert p.type == expected_row4[c]

    # Check rank 2 (row 3): 5 White pawns
    for c in range(5):
        p = b.grid[3][c]
        assert p is not None
        assert p.color == WHITE
        assert p.type == PAWN

    # Check rank 3 (row 2): Empty
    for c in range(5):
        assert b.grid[2][c] is None

    # Check rank 4 (row 1): 5 Black pawns
    for c in range(5):
        p = b.grid[1][c]
        assert p is not None
        assert p.color == BLACK
        assert p.type == PAWN

    # Check rank 5 (row 0): r, n, b, q, k
    expected_row0 = [ROOK, KNIGHT, BISHOP, QUEEN, KING]
    for c in range(5):
        p = b.grid[0][c]
        assert p is not None
        assert p.color == BLACK
        assert p.type == expected_row0[c]

    print("test_initial_layout passed!")


def test_initial_legal_moves():
    b = Board()
    moves = b.get_legal_moves()
    # In initial state:
    # 5 pawns can each move 1 step forward (5 moves: a2-a3, b2-b3, c2-c3, d2-d3, e2-e3)
    # Knight at b1 (4, 1): jumps to a3 (2, 0) and c3 (2, 2) (2 moves)
    # Total initial legal moves for White = 7 moves.
    assert len(moves) == 7, f"Expected 7 moves, got {len(moves)}"
    print(f"test_initial_legal_moves passed! White has {len(moves)} initial moves.")


def test_make_undo_move():
    b = Board()
    initial_key = b.get_position_key()
    moves = b.get_legal_moves()
    for m in moves:
        b.make_move(m)
        assert b.turn == BLACK
        b.undo_move()
        assert b.turn == WHITE
        assert b.get_position_key() == initial_key
    print("test_make_undo_move passed!")


def test_pawn_promotion():
    b = Board(setup_initial=False)
    # Place white king at (4, 0), black king at (4, 4)
    b.grid[4][0] = Piece(KING, WHITE)
    b.white_king_pos = (4, 0)
    b.grid[4][4] = Piece(KING, BLACK)
    b.black_king_pos = (4, 4)

    # Place white pawn at row 1 (Rank 4), column 2
    b.grid[1][2] = Piece(PAWN, WHITE)
    b.turn = WHITE

    legal_moves = b.get_legal_moves()
    # Pawn can promote to row 0, col 2 into Q, R, B, N
    promo_moves = [m for m in legal_moves if m.promotion is not None]
    assert len(promo_moves) == 4, f"Expected 4 promotion moves, got {len(promo_moves)}"
    
    # Test executing a Queen promotion
    q_move = [m for m in promo_moves if m.promotion == QUEEN][0]
    b.make_move(q_move)
    promoted_piece = b.grid[0][2]
    assert promoted_piece is not None
    assert promoted_piece.type == QUEEN
    assert promoted_piece.color == WHITE
    
    b.undo_move()
    restored_piece = b.grid[1][2]
    assert restored_piece is not None
    assert restored_piece.type == PAWN
    assert restored_piece.color == WHITE
    assert b.grid[0][2] is None
    print("test_pawn_promotion passed!")


def test_check_and_checkmate():
    b = Board(setup_initial=False)
    # Fool's mate / quick scholar checkmate scenario on 5x5:
    # Place black king at (0, 4) [E5]
    b.grid[0][4] = Piece(KING, BLACK)
    b.black_king_pos = (0, 4)

    # Place white king at (4, 4) [E1]
    b.grid[4][4] = Piece(KING, WHITE)
    b.white_king_pos = (4, 4)

    # Place white Queen at (1, 4) [E4] defended by white rook at (4, 0) [A1] or bishop
    b.grid[1][4] = Piece(QUEEN, WHITE)
    # Defend Queen with White Rook at (1, 0) [A4]
    b.grid[1][0] = Piece(ROOK, WHITE)

    b.turn = BLACK
    assert b.is_in_check(BLACK)
    assert b.is_checkmate()
    is_over, msg, winner = b.get_game_status()
    assert is_over
    assert winner == WHITE
    assert msg == "Matt! Valge võitis!", f"Expected 'Matt! Valge võitis!', got '{msg}'"
    print("test_check_and_checkmate passed!")


def test_stalemate():
    b = Board(setup_initial=False)
    # Black king at (0, 0) [A5]
    b.grid[0][0] = Piece(KING, BLACK)
    b.black_king_pos = (0, 0)

    # White king at (2, 1) [B3]
    b.grid[2][1] = Piece(KING, WHITE)
    b.white_king_pos = (2, 1)

    # White queen at (1, 2) [C4]
    # Covers: (0, 1) [B5], (0, 2) [C5], (1, 0) [A4], (1, 1) [B4]
    # Black king at (0, 0) is not under direct attack by Queen (since 0!=1 and 0!=2 and abs(0-1)!=abs(0-2))
    # Let's verify:
    b.grid[1][2] = Piece(QUEEN, WHITE)
    b.turn = BLACK

    assert not b.is_in_check(BLACK)
    legal = b.get_legal_moves()
    assert len(legal) == 0, f"Expected 0 legal moves, got {legal}"
    assert b.is_stalemate()
    is_over, msg, winner = b.get_game_status()
    assert is_over
    assert winner is None
    print("test_stalemate passed!")


if __name__ == "__main__":
    test_initial_layout()
    test_initial_legal_moves()
    test_make_undo_move()
    test_pawn_promotion()
    test_check_and_checkmate()
    test_stalemate()
    print("\nAll board mechanics tests passed successfully!")
