"""
Tests for AI search, checkmate finding, and evaluation.
"""
import time
from board import Board, Piece, Move
from ai import ChessAI
from constants import (
    WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING
)


def test_ai_initial_move():
    board = Board()
    ai = ChessAI(difficulty="keskmine")
    t0 = time.perf_counter()
    best_move = ai.get_best_move(board)
    dt = time.perf_counter() - t0
    assert best_move is not None
    assert best_move in board.get_legal_moves()
    print(f"test_ai_initial_move passed! Move: {best_move}, time: {dt:.3f}s, nodes: {ai.nodes_evaluated}")


def test_ai_finds_checkmate_in_one():
    # Setup position where White can deliver checkmate in 1 move
    board = Board(setup_initial=False)
    # Black king on (0, 4)
    board.grid[0][4] = Piece(KING, BLACK)
    board.black_king_pos = (0, 4)

    # White king on (2, 4)
    board.grid[2][4] = Piece(KING, WHITE)
    board.white_king_pos = (2, 4)

    # White queen at (1, 0) [A4]
    # Queen can move to (1, 4) [E4] for checkmate!
    board.grid[1][0] = Piece(QUEEN, WHITE)
    board.turn = WHITE

    ai = ChessAI(difficulty="raske")
    best_move = ai.get_best_move(board)
    assert best_move is not None
    board.make_move(best_move)
    assert board.is_checkmate(), f"Move {best_move} did not deliver checkmate!"
    print("test_ai_finds_checkmate_in_one passed!")


def test_ai_defends_against_checkmate():
    # Setup position where Black is threatened with mate, but can block or capture
    board = Board(setup_initial=False)
    # White queen at (1, 2)
    board.grid[1][2] = Piece(QUEEN, WHITE)
    board.grid[4][4] = Piece(KING, WHITE)
    board.white_king_pos = (4, 4)

    # Black king at (0, 4)
    board.grid[0][4] = Piece(KING, BLACK)
    board.black_king_pos = (0, 4)

    # Black rook at (0, 0)
    board.grid[0][0] = Piece(ROOK, BLACK)
    board.turn = BLACK

    ai = ChessAI(difficulty="keskmine")
    best_move = ai.get_best_move(board)
    assert best_move is not None
    board.make_move(best_move)
    # Ensure black didn't allow instant mate
    assert not board.is_checkmate()
    print("test_ai_defends_against_checkmate passed!")


def test_ai_difficulties():
    board = Board()
    for diff in ["lihtne", "keskmine", "raske"]:
        ai = ChessAI(difficulty=diff)
        t0 = time.perf_counter()
        move = ai.get_best_move(board)
        dt = time.perf_counter() - t0
        assert move in board.get_legal_moves()
        print(f"Difficulty '{diff}': move={move}, nodes={ai.nodes_evaluated}, time={dt:.3f}s")
    print("test_ai_difficulties passed!")


if __name__ == "__main__":
    test_ai_initial_move()
    test_ai_finds_checkmate_in_one()
    test_ai_defends_against_checkmate()
    test_ai_difficulties()
    print("\nAll AI tests passed successfully!")
