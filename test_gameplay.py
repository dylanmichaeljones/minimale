"""
Headless simulation and integration tests for 5x5 Mini-Chess.
Tests AI vs AI full match, GUI frame rendering, and move consistency.
"""
import os
import pygame
from board import Board
from ai import ChessAI
from constants import WHITE, BLACK


def test_ai_vs_ai_game():
    """Runs a simulated game between two AI instances to ensure 0 crashes or illegal moves."""
    board = Board()
    ai_white = ChessAI(difficulty="keskmine")
    ai_black = ChessAI(difficulty="keskmine")

    print("\n--- Simuleerime AI vs AI partiid (max 30 poolkäiku) ---")
    move_count = 0
    max_moves = 30

    while move_count < max_moves:
        is_over, status_msg, winner = board.get_game_status()
        if is_over:
            print(f"Mäng lõppes käigul {move_count // 2 + 1}: {status_msg}")
            break

        current_ai = ai_white if board.turn == WHITE else ai_black
        move = current_ai.get_best_move(board)
        assert move is not None, f"AI returned None move when game is not over!"
        assert move in board.get_legal_moves(), f"AI produced illegal move: {move}"

        alg = board.format_move_algebraic(move)
        turn_str = "Valge" if board.turn == WHITE else "Must"
        print(f"Käik {move_count // 2 + 1} ({turn_str}): {alg}")

        board.make_move(move)
        move_count += 1

    print(f"AI vs AI simulatsioon edukalt läbitud ({move_count} käiku ilma vigadeta)!")


def test_gui_headless_render():
    """Verifies that Pygame surfaces and GUI frame render without error in headless mode."""
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    import time
    from gui import MiniChessGUI
    from constants import PAWN

    gui = MiniChessGUI()
    # Simulate 5 frames
    for _ in range(5):
        gui.draw_board()
        gui.draw_sidebar()
        gui.draw_game_over_banner()

    # Test move execution: move White pawn at C2 (3, 2) to C3 (2, 2)
    gui.on_human_move_requested((3, 2), (2, 2))
    assert gui.board.grid[3][2] is None, "Piece was not cleared from source square!"
    assert gui.board.grid[2][2] is not None and gui.board.grid[2][2].type == PAWN
    
    # Wait for AI response
    timeout = 2.0
    start = time.time()
    while gui.ai_thinking and time.time() - start < timeout:
        gui.check_ai_result()
        time.sleep(0.01)

    assert not gui.ai_thinking, "AI did not respond in time!"
    assert len(gui.board.move_history) == 2, f"Expected 2 moves in history, got {len(gui.board.move_history)}"
    assert gui.board.move_history[1].piece_moved.color == BLACK, "Opponent did not make move!"

    # Render frame after move
    gui.draw_board()
    gui.draw_sidebar()
    assert gui.board.grid[3][2] is None, "Render corrupted grid!"

    pygame.quit()
    print("test_gui_headless_render and human/AI interaction passed!")


if __name__ == "__main__":
    test_ai_vs_ai_game()
    test_gui_headless_render()
    print("\nKõik integratsiooni- ja mängusimulatsiooni testid läbitud!")
