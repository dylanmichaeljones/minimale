"""
Pygame graphical user interface for 5x5 Mini-Chess.
Features interactive board, piece drag-and-drop / click-to-move,
visual move highlights, captured pieces, move history, AI difficulty, and side toggling.
"""
import queue
import threading
from typing import Optional, Tuple, List
import pygame

from board import Board, Move, Piece
from ai import ChessAI
from pieces_svg import get_piece_surface
from constants import (
    BOARD_SIZE, WHITE, BLACK, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING,
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    BOARD_MARGIN_LEFT, BOARD_MARGIN_TOP, SQUARE_SIZE,
    COLOR_BG, COLOR_PANEL_BG, COLOR_PANEL_BORDER,
    COLOR_SQUARE_LIGHT, COLOR_SQUARE_DARK,
    COLOR_SELECTED, COLOR_LAST_MOVE, COLOR_LEGAL_DOT, COLOR_LEGAL_CAPTURE, COLOR_CHECK,
    COLOR_TEXT_LIGHT, COLOR_TEXT_MUTED, COLOR_TEXT_DARK,
    COLOR_BTN_NORMAL, COLOR_BTN_HOVER, COLOR_BTN_ACTIVE, COLOR_BTN_ACCENT,
    FILES, RANKS, COLOR_NAMES_ET, PIECE_NAMES_ET, PIECE_VALUES
)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font,
                 callback, bg_color=COLOR_BTN_NORMAL, hover_color=COLOR_BTN_HOVER,
                 active_color=COLOR_BTN_ACTIVE, text_color=COLOR_TEXT_LIGHT):
        self.rect = rect
        self.text = text
        self.font = font
        self.callback = callback
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.text_color = text_color
        self.is_hovered = False
        self.is_active = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_active = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_active:
                self.is_active = False
                if self.rect.collidepoint(event.pos):
                    self.callback()
                    return True
        return False

    def draw(self, surface: pygame.Surface):
        color = self.active_color if self.is_active else (self.hover_color if self.is_hovered else self.bg_color)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.rect, width=1, border_radius=6)

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)


class PromotionDialog:
    """Popup modal dialog for choosing pawn promotion piece."""
    def __init__(self, color: int, square_size: int, callback):
        self.color = color
        self.square_size = square_size
        self.callback = callback
        self.pieces = [QUEEN, ROOK, BISHOP, KNIGHT]
        self.visible = True
        self.rect = pygame.Rect(0, 0, 360, 140)
        self.piece_rects: List[Tuple[str, pygame.Rect]] = []

    def center_on(self, center_pos: Tuple[int, int]):
        self.rect.center = center_pos
        self.piece_rects.clear()
        start_x = self.rect.x + 20
        y = self.rect.y + 45
        size = 70
        gap = 15
        for i, p_type in enumerate(self.pieces):
            r = pygame.Rect(start_x + i * (size + gap), y, size, size)
            self.piece_rects.append((p_type, r))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for p_type, r in self.piece_rects:
                if r.collidepoint(event.pos):
                    self.callback(p_type)
                    return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font):
        # Dim background
        dim_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim_surf.fill((0, 0, 0, 150))
        surface.blit(dim_surf, (0, 0))

        # Dialog box
        pygame.draw.rect(surface, COLOR_PANEL_BG, self.rect, border_radius=12)
        pygame.draw.rect(surface, COLOR_BTN_ACCENT, self.rect, width=2, border_radius=12)

        title_surf = font.render("Vali etturi asendus:", True, COLOR_TEXT_LIGHT)
        title_rect = title_surf.get_rect(center=(self.rect.centerx, self.rect.y + 24))
        surface.blit(title_surf, title_rect)

        mouse_pos = pygame.mouse.get_pos()
        for p_type, r in self.piece_rects:
            is_hover = r.collidepoint(mouse_pos)
            bg_col = COLOR_BTN_HOVER if is_hover else COLOR_BTN_NORMAL
            pygame.draw.rect(surface, bg_col, r, border_radius=8)
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, r, width=1, border_radius=8)

            piece_surf = get_piece_surface(p_type, self.color, r.width - 10)
            p_rect = piece_surf.get_rect(center=r.center)
            surface.blit(piece_surf, p_rect)


class MiniChessGUI:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("5x5 Mini-Male | Minimax AI")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_title = pygame.font.SysFont(['segoe ui', 'arial', 'sans-serif'], 24, bold=True)
        self.font_sub = pygame.font.SysFont(['segoe ui', 'arial', 'sans-serif'], 16, bold=True)
        self.font_regular = pygame.font.SysFont(['segoe ui', 'arial', 'sans-serif'], 14)
        self.font_small = pygame.font.SysFont(['segoe ui', 'arial', 'sans-serif'], 12)
        self.font_coord = pygame.font.SysFont(['segoe ui', 'arial', 'sans-serif'], 14, bold=True)

        # Game state
        self.board = Board()
        self.ai = ChessAI(difficulty="keskmine")
        self.human_color = WHITE
        self.flipped = False  # True if Black is at the bottom

        # Selection and interaction
        self.selected_sq: Optional[Tuple[int, int]] = None
        self.legal_moves_for_selected: List[Move] = []
        self.dragging = False
        self.drag_piece: Optional[Piece] = None
        self.drag_from_sq: Optional[Tuple[int, int]] = None

        # Promotion modal state
        self.pending_promotion_move: Optional[Tuple[Tuple[int, int], Tuple[int, int], Piece, Optional[Piece]]] = None
        self.promotion_dialog: Optional[PromotionDialog] = None

        # AI threading state
        self.ai_queue: queue.Queue = queue.Queue()
        self.ai_thinking = False
        self.ai_thread: Optional[threading.Thread] = None
        self.thinking_dots = 0
        self.thinking_timer = 0

        # UI Layout
        self.board_rect = pygame.Rect(
            BOARD_MARGIN_LEFT, BOARD_MARGIN_TOP,
            BOARD_SIZE * SQUARE_SIZE, BOARD_SIZE * SQUARE_SIZE
        )
        self.panel_rect = pygame.Rect(
            BOARD_MARGIN_LEFT + BOARD_SIZE * SQUARE_SIZE + 35,
            BOARD_MARGIN_TOP - 15,
            WINDOW_WIDTH - (BOARD_MARGIN_LEFT + BOARD_SIZE * SQUARE_SIZE + 60),
            BOARD_SIZE * SQUARE_SIZE + 30
        )

        self.history_scroll_offset = 0

        # Build Sidebar Buttons
        self.buttons: List[Button] = []
        self.build_buttons()

    def build_buttons(self):
        self.buttons.clear()
        bx = self.panel_rect.x + 15
        bw = self.panel_rect.width - 30
        h = 36
        gap = 10
        cur_y = self.panel_rect.bottom - 175

        # Difficulty cycle button
        def toggle_diff():
            diffs = ["lihtne", "keskmine", "raske"]
            nxt = diffs[(diffs.index(self.ai.difficulty) + 1) % len(diffs)]
            self.ai.set_difficulty(nxt)
            self.build_buttons()

        diff_label = f"Raskusaste: {self.ai.difficulty.capitalize()}"
        self.btn_diff = Button(pygame.Rect(bx, cur_y, bw, h), diff_label, self.font_regular, toggle_diff)
        self.buttons.append(self.btn_diff)
        cur_y += h + gap

        # Side toggle button
        def toggle_side():
            if self.ai_thinking:
                return
            self.human_color = -self.human_color
            self.flipped = (self.human_color == BLACK)
            self.start_new_game()

        side_str = "Mängija: Valge" if self.human_color == WHITE else "Mängija: Must"
        self.btn_side = Button(pygame.Rect(bx, cur_y, bw // 2 - 5, h), side_str, self.font_small, toggle_side)
        self.buttons.append(self.btn_side)

        # Flip board view button
        def toggle_flip():
            self.flipped = not self.flipped

        self.btn_flip = Button(pygame.Rect(bx + bw // 2 + 5, cur_y, bw // 2 - 5, h), "Pööra laud", self.font_small, toggle_flip)
        self.buttons.append(self.btn_flip)
        cur_y += h + gap

        # Undo button
        def undo_action():
            if self.ai_thinking or len(self.board.move_history) == 0:
                return
            # If human made move and computer hasn't moved yet or already moved
            # Undo twice if possible so human gets to replay move
            self.board.undo_move()
            if self.board.turn != self.human_color and len(self.board.move_history) > 0:
                self.board.undo_move()
            self.selected_sq = None
            self.legal_moves_for_selected.clear()

        self.btn_undo = Button(pygame.Rect(bx, cur_y, bw // 2 - 5, h), "Võta tagasi", self.font_regular, undo_action)
        self.buttons.append(self.btn_undo)

        # New game button
        def new_game_action():
            if self.ai_thinking:
                return
            self.start_new_game()

        self.btn_new = Button(pygame.Rect(bx + bw // 2 + 5, cur_y, bw // 2 - 5, h), "Uus mäng", self.font_regular,
                              new_game_action, bg_color=COLOR_BTN_ACCENT)
        self.buttons.append(self.btn_new)

    def start_new_game(self):
        self.board.setup_initial_board()
        self.selected_sq = None
        self.legal_moves_for_selected.clear()
        self.dragging = False
        self.drag_piece = None
        self.pending_promotion_move = None
        self.promotion_dialog = None
        self.history_scroll_offset = 0
        self.build_buttons()

        # If computer plays first (Human is Black)
        if self.board.turn != self.human_color:
            self.trigger_ai_move()

    def square_to_screen(self, row: int, col: int) -> Tuple[int, int]:
        """Maps board (row, col) to screen pixel coordinates (top-left of square)."""
        disp_r = (BOARD_SIZE - 1 - row) if self.flipped else row
        disp_c = (BOARD_SIZE - 1 - col) if self.flipped else col
        x = self.board_rect.x + disp_c * SQUARE_SIZE
        y = self.board_rect.y + disp_r * SQUARE_SIZE
        return x, y

    def screen_to_square(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Maps screen pixel coordinates to board (row, col)."""
        if not self.board_rect.collidepoint(x, y):
            return None
        disp_c = (x - self.board_rect.x) // SQUARE_SIZE
        disp_r = (y - self.board_rect.y) // SQUARE_SIZE
        row = (BOARD_SIZE - 1 - disp_r) if self.flipped else disp_r
        col = (BOARD_SIZE - 1 - disp_c) if self.flipped else disp_c
        if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
            return (row, col)
        return None

    def trigger_ai_move(self):
        """Launches AI search on a background thread so UI stays 100% fluid."""
        if self.ai_thinking:
            return
        is_over, _, _ = self.board.get_game_status()
        if is_over:
            return

        self.ai_thinking = True
        board_copy = self.board.clone()

        def worker():
            try:
                best_move = self.ai.get_best_move(board_copy)
                self.ai_queue.put(best_move)
            except Exception as e:
                import traceback
                traceback.print_exc()
                self.ai_queue.put(None)

        self.ai_thread = threading.Thread(target=worker, daemon=True)
        self.ai_thread.start()

    def check_ai_result(self):
        """Polls the queue for AI calculation result."""
        try:
            move = self.ai_queue.get_nowait()
            if move is not None and not self.board.get_game_status()[0]:
                self.board.make_move(move)
                self.board.record_move_san(move)
            self.ai_thinking = False
        except queue.Empty:
            pass

    def on_human_move_requested(self, from_sq: Tuple[int, int], to_sq: Tuple[int, int]):
        """Validates and applies a move initiated by the player."""
        piece = self.board.get_piece(*from_sq)
        if piece is None or piece.color != self.board.turn:
            return

        # Check if this move requires pawn promotion
        promo_row = 0 if self.human_color == WHITE else 4
        is_promotion = (piece.type == PAWN and to_sq[0] == promo_row)

        if is_promotion:
            # Check if any legal move matches this from_sq and to_sq
            legal_moves = [
                m for m in self.board.get_legal_moves()
                if m.from_pos == from_sq and m.to_pos == to_sq
            ]
            if legal_moves:
                captured = self.board.get_piece(*to_sq)
                self.pending_promotion_move = (from_sq, to_sq, piece, captured)
                self.promotion_dialog = PromotionDialog(
                    self.human_color, SQUARE_SIZE, self.on_promotion_selected
                )
                self.promotion_dialog.center_on(self.board_rect.center)
            return

        # Regular move
        matching_moves = [
            m for m in self.board.get_legal_moves()
            if m.from_pos == from_sq and m.to_pos == to_sq
        ]
        if matching_moves:
            move = matching_moves[0]
            self.board.make_move(move)
            self.board.record_move_san(move)
            self.selected_sq = None
            self.legal_moves_for_selected.clear()
            self.dragging = False
            self.drag_piece = None
            self.drag_from_sq = None

            # Trigger AI response if it's computer's turn
            if not self.board.get_game_status()[0] and self.board.turn != self.human_color:
                self.trigger_ai_move()

    def on_promotion_selected(self, chosen_piece_type: str):
        """Called when player selects a piece from the promotion modal."""
        if self.pending_promotion_move:
            from_sq, to_sq, piece, captured = self.pending_promotion_move
            move = Move(from_sq, to_sq, piece, captured, chosen_piece_type)
            self.board.make_move(move)
            self.board.record_move_san(move)
            self.pending_promotion_move = None
            self.promotion_dialog = None
            self.selected_sq = None
            self.legal_moves_for_selected.clear()
            self.dragging = False
            self.drag_piece = None
            self.drag_from_sq = None

            if not self.board.get_game_status()[0] and self.board.turn != self.human_color:
                self.trigger_ai_move()

    def handle_events(self) -> bool:
        """Processes Pygame window events. Returns False on quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # If promotion modal is active, it intercepts clicks
            if self.promotion_dialog is not None:
                if self.promotion_dialog.handle_event(event):
                    return True
                continue

            # Check sidebar buttons
            btn_clicked = False
            for btn in self.buttons:
                if btn.handle_event(event):
                    btn_clicked = True
                    break
            if btn_clicked:
                continue

            # Keyboard shortcuts
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u or (event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL)):
                    self.btn_undo.callback()
                elif event.key == pygame.K_n:
                    self.btn_new.callback()
                elif event.key == pygame.K_f:
                    self.btn_flip.callback()
                elif event.key == pygame.K_ESCAPE:
                    self.selected_sq = None
                    self.legal_moves_for_selected.clear()
                    self.dragging = False

            # Mouse wheel for move history scrolling
            if event.type == pygame.MOUSEWHEEL:
                if self.panel_rect.collidepoint(pygame.mouse.get_pos()):
                    self.history_scroll_offset = max(0, self.history_scroll_offset - event.y)

            # Ignore board interaction if AI is thinking or game is over
            if self.ai_thinking or self.board.get_game_status()[0]:
                continue

            # Only allow moves if it's the human's turn
            if self.board.turn != self.human_color:
                continue

            # Mouse Button Down
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                sq = self.screen_to_square(*event.pos)
                if sq is not None:
                    piece = self.board.get_piece(*sq)
                    if self.selected_sq is not None:
                        # Target clicked: try to make move
                        if sq in [m.to_pos for m in self.legal_moves_for_selected]:
                            from_sq = self.selected_sq
                            self.selected_sq = None
                            self.legal_moves_for_selected.clear()
                            self.dragging = False
                            self.drag_piece = None
                            self.drag_from_sq = None
                            self.on_human_move_requested(from_sq, sq)
                            continue
                        elif piece is not None and piece.color == self.human_color:
                            # Switch selection
                            self.selected_sq = sq
                            self.legal_moves_for_selected = [
                                m for m in self.board.get_legal_moves() if m.from_pos == sq
                            ]
                            self.dragging = True
                            self.drag_piece = piece
                            self.drag_from_sq = sq
                        else:
                            self.selected_sq = None
                            self.legal_moves_for_selected.clear()
                            self.dragging = False
                            self.drag_piece = None
                            self.drag_from_sq = None
                    else:
                        if piece is not None and piece.color == self.human_color:
                            self.selected_sq = sq
                            self.legal_moves_for_selected = [
                                m for m in self.board.get_legal_moves() if m.from_pos == sq
                            ]
                            self.dragging = True
                            self.drag_piece = piece
                            self.drag_from_sq = sq
                else:
                    self.selected_sq = None
                    self.legal_moves_for_selected.clear()
                    self.dragging = False
                    self.drag_piece = None
                    self.drag_from_sq = None

            # Mouse Button Up (Drag & Drop)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.dragging and self.drag_from_sq is not None:
                    to_sq = self.screen_to_square(*event.pos)
                    if to_sq is not None and to_sq != self.drag_from_sq:
                        if to_sq in [m.to_pos for m in self.legal_moves_for_selected]:
                            from_sq = self.drag_from_sq
                            self.dragging = False
                            self.drag_piece = None
                            self.drag_from_sq = None
                            self.on_human_move_requested(from_sq, to_sq)
                self.dragging = False
                self.drag_piece = None
                self.drag_from_sq = None

        return True

    def draw_board(self):
        """Draws the 5x5 board tiles, coordinates, piece highlights, and pieces."""
        # Board background border
        border_rect = self.board_rect.inflate(10, 10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, border_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, border_rect, width=2, border_radius=8)

        # Draw coordinate labels
        for i in range(BOARD_SIZE):
            file_char = FILES[BOARD_SIZE - 1 - i] if self.flipped else FILES[i]
            rank_char = RANKS[i] if self.flipped else RANKS[BOARD_SIZE - 1 - i]

            # File letters (bottom & top)
            col_x = self.board_rect.x + i * SQUARE_SIZE + SQUARE_SIZE // 2
            lbl_bot = self.font_coord.render(file_char, True, COLOR_TEXT_MUTED)
            self.screen.blit(lbl_bot, lbl_bot.get_rect(center=(col_x, self.board_rect.bottom + 16)))
            lbl_top = self.font_coord.render(file_char, True, COLOR_TEXT_MUTED)
            self.screen.blit(lbl_top, lbl_top.get_rect(center=(col_x, self.board_rect.top - 16)))

            # Rank numbers (left & right)
            row_y = self.board_rect.y + i * SQUARE_SIZE + SQUARE_SIZE // 2
            lbl_left = self.font_coord.render(rank_char, True, COLOR_TEXT_MUTED)
            self.screen.blit(lbl_left, lbl_left.get_rect(center=(self.board_rect.left - 18, row_y)))
            lbl_right = self.font_coord.render(rank_char, True, COLOR_TEXT_MUTED)
            self.screen.blit(lbl_right, lbl_right.get_rect(center=(self.board_rect.right + 18, row_y)))

        # Last move highlight squares
        last_move = self.board.move_history[-1] if self.board.move_history else None

        # King in check highlight
        in_check_color = None
        if self.board.is_in_check(WHITE):
            in_check_color = WHITE
        elif self.board.is_in_check(BLACK):
            in_check_color = BLACK

        # Draw squares
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = self.square_to_screen(r, c)
                sq_rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)

                # Base tile color
                is_light = (r + c) % 2 == 0
                tile_col = COLOR_SQUARE_LIGHT if is_light else COLOR_SQUARE_DARK
                pygame.draw.rect(self.screen, tile_col, sq_rect)

                # Last move highlight
                if last_move and ((r, c) == last_move.from_pos or (r, c) == last_move.to_pos):
                    hl_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    hl_surf.fill(COLOR_LAST_MOVE)
                    self.screen.blit(hl_surf, (x, y))

                # King in check radial indicator
                if in_check_color is not None:
                    k_pos = self.board.white_king_pos if in_check_color == WHITE else self.board.black_king_pos
                    if (r, c) == k_pos:
                        check_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                        pygame.draw.circle(check_surf, COLOR_CHECK, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 4)
                        self.screen.blit(check_surf, (x, y))

                # Selected square highlight
                if self.selected_sq == (r, c):
                    sel_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                    sel_surf.fill(COLOR_SELECTED)
                    self.screen.blit(sel_surf, (x, y))
                    pygame.draw.rect(self.screen, (100, 200, 80), sq_rect, width=3)

        # Draw legal move indicators
        for move in self.legal_moves_for_selected:
            tr, tc = move.to_pos
            tx, ty = self.square_to_screen(tr, tc)
            target_piece = self.board.get_piece(tr, tc)
            dot_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)

            if target_piece is None:
                # Green central circle
                pygame.draw.circle(dot_surf, COLOR_LEGAL_DOT, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), 12)
            else:
                # Capture ring around enemy square
                pygame.draw.circle(dot_surf, COLOR_LEGAL_CAPTURE, (SQUARE_SIZE // 2, SQUARE_SIZE // 2), SQUARE_SIZE // 2 - 5, width=4)

            self.screen.blit(dot_surf, (tx, ty))

        # Draw pieces on the board
        mouse_pos = pygame.mouse.get_pos()
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                # If currently dragging this piece, draw it later attached to cursor
                if self.dragging and self.drag_from_sq == (r, c):
                    continue

                piece = self.board.get_piece(r, c)
                if piece is not None:
                    x, y = self.square_to_screen(r, c)
                    surf = get_piece_surface(piece.type, piece.color, SQUARE_SIZE - 12)
                    rect = surf.get_rect(center=(x + SQUARE_SIZE // 2, y + SQUARE_SIZE // 2))
                    self.screen.blit(surf, rect)

        # Draw dragged piece following mouse cursor
        if self.dragging and self.drag_piece is not None:
            drag_surf = get_piece_surface(self.drag_piece.type, self.drag_piece.color, SQUARE_SIZE)
            drag_rect = drag_surf.get_rect(center=mouse_pos)
            self.screen.blit(drag_surf, drag_rect)

    def draw_sidebar(self):
        """Draws right control sidebar: title, status, captured pieces, move history, buttons."""
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, self.panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, self.panel_rect, width=2, border_radius=12)

        # Header Title
        title_surf = self.font_title.render("5x5 MINI-MALE", True, COLOR_TEXT_LIGHT)
        self.screen.blit(title_surf, (self.panel_rect.x + 18, self.panel_rect.y + 16))

        # Game status badge
        is_over, status_msg, winner = self.board.get_game_status()
        badge_rect = pygame.Rect(self.panel_rect.x + 15, self.panel_rect.y + 52, self.panel_rect.width - 30, 42)

        if is_over:
            badge_bg = (120, 40, 40) if winner is not None else (70, 75, 85)
        elif self.board.is_in_check(self.board.turn):
            badge_bg = (150, 60, 30)
        elif self.ai_thinking:
            badge_bg = (40, 70, 110)
        else:
            badge_bg = (45, 52, 65)

        pygame.draw.rect(self.screen, badge_bg, badge_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, badge_rect, width=1, border_radius=8)

        # Thinking animation dots
        if self.ai_thinking:
            status_text = f"Arvuti mõtleb{'.' * (self.thinking_dots + 1)}"
        else:
            status_text = status_msg

        msg_surf = self.font_sub.render(status_text, True, COLOR_TEXT_LIGHT)
        msg_r = msg_surf.get_rect(center=badge_rect.center)
        self.screen.blit(msg_surf, msg_r)

        # Captured pieces and material score
        cur_y = badge_rect.bottom + 12
        cap_rect = pygame.Rect(self.panel_rect.x + 15, cur_y, self.panel_rect.width - 30, 60)
        pygame.draw.rect(self.screen, (30, 35, 45), cap_rect, border_radius=6)

        # Captured by White (Black pieces taken)
        w_cap = self.board.captured_pieces[WHITE]
        # Captured by Black (White pieces taken)
        b_cap = self.board.captured_pieces[BLACK]

        # White captures row
        w_lbl = self.font_small.render("Valge võttis:", True, COLOR_TEXT_MUTED)
        self.screen.blit(w_lbl, (cap_rect.x + 8, cap_rect.y + 6))
        for idx, p in enumerate(w_cap[-8:]):
            p_surf = get_piece_surface(p.type, BLACK, 22)
            self.screen.blit(p_surf, (cap_rect.x + 85 + idx * 18, cap_rect.y + 4))

        # Black captures row
        b_lbl = self.font_small.render("Must võttis:", True, COLOR_TEXT_MUTED)
        self.screen.blit(b_lbl, (cap_rect.x + 8, cap_rect.y + 32))
        for idx, p in enumerate(b_cap[-8:]):
            p_surf = get_piece_surface(p.type, WHITE, 22)
            self.screen.blit(p_surf, (cap_rect.x + 85 + idx * 18, cap_rect.y + 30))

        # Material balance indicator
        mat_bal = self.board.get_material_balance()
        if mat_bal != 0:
            score_prefix = "+" if mat_bal > 0 else ""
            mat_str = f"{score_prefix}{mat_bal // 100}"
            mat_surf = self.font_small.render(mat_str, True, COLOR_TEXT_LIGHT)
            self.screen.blit(mat_surf, (cap_rect.right - 25, cap_rect.centery - 6))

        # Move History Section
        cur_y = cap_rect.bottom + 12
        hist_title = self.font_sub.render("Käikude ajalugu", True, COLOR_TEXT_LIGHT)
        self.screen.blit(hist_title, (self.panel_rect.x + 18, cur_y))

        hist_box = pygame.Rect(self.panel_rect.x + 15, cur_y + 24, self.panel_rect.width - 30, 130)
        pygame.draw.rect(self.screen, (28, 32, 40), hist_box, border_radius=6)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, hist_box, width=1, border_radius=6)

        # Render algebraic moves
        moves = self.board.move_history
        move_pairs = []
        for i in range(0, len(moves), 2):
            w_m = self.board.format_move_algebraic(moves[i])
            b_m = self.board.format_move_algebraic(moves[i + 1]) if i + 1 < len(moves) else ""
            move_pairs.append((i // 2 + 1, w_m, b_m))

        max_visible_rows = 5
        total_rows = len(move_pairs)
        # Auto-scroll to latest moves
        start_row = max(0, total_rows - max_visible_rows)
        row_y = hist_box.y + 6
        for move_num, w_str, b_str in move_pairs[start_row:]:
            line_str = f"{move_num}. {w_str:<10} {b_str}"
            line_surf = self.font_regular.render(line_str, True, COLOR_TEXT_LIGHT)
            self.screen.blit(line_surf, (hist_box.x + 12, row_y))
            row_y += 22

        # Draw buttons
        for btn in self.buttons:
            btn.draw(self.screen)

    def draw_game_over_banner(self):
        """Displays end game overlay if checkmate or stalemate occurred."""
        is_over, status_msg, winner = self.board.get_game_status()
        if not is_over:
            return

        banner_w = 400
        banner_h = 100
        banner_rect = pygame.Rect(0, 0, banner_w, banner_h)
        banner_rect.center = self.board_rect.center

        # Drop shadow & panel
        shadow_rect = banner_rect.inflate(8, 8)
        pygame.draw.rect(self.screen, (10, 12, 16), shadow_rect, border_radius=12)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, banner_rect, border_radius=12)
        border_col = (200, 70, 70) if winner is not None else COLOR_PANEL_BORDER
        pygame.draw.rect(self.screen, border_col, banner_rect, width=2, border_radius=12)

        # Message
        t_surf = self.font_title.render(status_msg, True, COLOR_TEXT_LIGHT)
        t_r = t_surf.get_rect(center=(banner_rect.centerx, banner_rect.y + 36))
        self.screen.blit(t_surf, t_r)

        hint_surf = self.font_small.render("Klõpsa 'Uus mäng' nupule uuesti alustamiseks", True, COLOR_TEXT_MUTED)
        hint_r = hint_surf.get_rect(center=(banner_rect.centerx, banner_rect.y + 70))
        self.screen.blit(hint_surf, hint_r)

    def run(self):
        """Main game loop."""
        running = True
        while running:
            # AI thinking animation ticker
            self.thinking_timer += 1
            if self.thinking_timer % 15 == 0:
                self.thinking_dots = (self.thinking_dots + 1) % 3

            # Check if AI background thread finished
            self.check_ai_result()

            # Handle user events
            running = self.handle_events()

            # Render frame
            self.screen.fill(COLOR_BG)
            self.draw_board()
            self.draw_sidebar()
            self.draw_game_over_banner()

            # Draw promotion dialog modal if open
            if self.promotion_dialog is not None:
                self.promotion_dialog.draw(self.screen, self.font_sub)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
