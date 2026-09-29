"""
Game constants, styling, board geometry, and Estonian notations for 5x5 Mini-Chess.
"""

BOARD_SIZE = 5

# Board Files (columns) and Ranks (rows)
FILES = ['A', 'B', 'C', 'D', 'E']
RANKS = ['1', '2', '3', '4', '5']

# Players / Colors
WHITE = 1
BLACK = -1

COLOR_NAMES_ET = {
    WHITE: "Valge",
    BLACK: "Must"
}

# Piece types
PAWN = 'P'
KNIGHT = 'N'
BISHOP = 'B'
ROOK = 'R'
QUEEN = 'Q'
KING = 'K'

PIECE_TYPES = [PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING]

# Estonian names and algebraic symbols
PIECE_NAMES_ET = {
    PAWN: "Ettur",
    KNIGHT: "Ratsu",
    BISHOP: "Oda",
    ROOK: "Vanker",
    QUEEN: "Lipp",
    KING: "Kuningas"
}

# In Estonian algebraic notation:
# V = Vanker (Rook), R = Ratsu (Knight), O = Oda (Bishop), L = Lipp (Queen), K = Kuningas (King)
# Pawns have no letter prefix in move notation.
PIECE_SYMBOLS_ET = {
    PAWN: "",
    KNIGHT: "R",
    BISHOP: "O",
    ROOK: "V",
    QUEEN: "L",
    KING: "K"
}

# Base piece values for heuristic evaluation
PIECE_VALUES = {
    PAWN: 100,
    KNIGHT: 320,
    BISHOP: 330,
    ROOK: 500,
    QUEEN: 950,
    KING: 20000
}

# Initial board configuration (5x5):
# Row 0 = Rank 5 (Black pieces: R, N, B, Q, K)
# Row 1 = Rank 4 (Black pawns)
# Row 2 = Rank 3 (Empty)
# Row 3 = Rank 2 (White pawns)
# Row 4 = Rank 1 (White pieces: R, N, B, Q, K)
INITIAL_LAYOUT = [
    [(ROOK, BLACK), (KNIGHT, BLACK), (BISHOP, BLACK), (QUEEN, BLACK), (KING, BLACK)],
    [(PAWN, BLACK), (PAWN, BLACK),   (PAWN, BLACK),   (PAWN, BLACK),  (PAWN, BLACK)],
    [None,          None,            None,            None,           None],
    [(PAWN, WHITE), (PAWN, WHITE),   (PAWN, WHITE),   (PAWN, WHITE),  (PAWN, WHITE)],
    [(ROOK, WHITE), (KNIGHT, WHITE), (BISHOP, WHITE), (QUEEN, WHITE), (KING, WHITE)]
]

# Coordinate transformation helpers
def col_to_file(col: int) -> str:
    return FILES[col]

def file_to_col(file_char: str) -> int:
    return FILES.index(file_char.upper())

def row_to_rank(row: int) -> str:
    return str(5 - row)

def rank_to_row(rank_char: str) -> int:
    return 5 - int(rank_char)

def pos_to_coord(row: int, col: int) -> str:
    return f"{col_to_file(col)}{row_to_rank(row)}"

def coord_to_pos(coord: str) -> tuple[int, int]:
    col = file_to_col(coord[0])
    row = rank_to_row(coord[1])
    return (row, col)

# GUI / Visual configuration
WINDOW_WIDTH = 920
WINDOW_HEIGHT = 650
FPS = 60

BOARD_MARGIN_LEFT = 50
BOARD_MARGIN_TOP = 65
SQUARE_SIZE = 100  # 5 * 100 = 500px board
BOARD_PIXEL_SIZE = BOARD_SIZE * SQUARE_SIZE

# Color palette
COLOR_BG = (26, 30, 38)            # Dark modern background
COLOR_PANEL_BG = (35, 41, 52)      # Sidebar card background
COLOR_PANEL_BORDER = (52, 60, 76)  # Subtle panel borders
COLOR_ACCENT = (70, 130, 180)      # Steel blue accent
COLOR_GOLD = (230, 180, 50)        # Warm gold highlight

# Board square colors (warm wooden tone)
COLOR_SQUARE_LIGHT = (240, 217, 181)
COLOR_SQUARE_DARK = (181, 136, 99)

# Overlay colors
COLOR_SELECTED = (130, 195, 80, 160)     # Semi-transparent lime-green
COLOR_LAST_MOVE = (245, 230, 110, 130)   # Soft gold glow
COLOR_LEGAL_DOT = (40, 140, 60, 200)     # Forest green dot for empty target
COLOR_LEGAL_CAPTURE = (220, 50, 50, 200) # Red marker for capture
COLOR_CHECK = (235, 60, 60, 180)         # Red pulse on king

# UI Text colors
COLOR_TEXT_LIGHT = (240, 243, 246)
COLOR_TEXT_MUTED = (160, 168, 182)
COLOR_TEXT_DARK = (30, 33, 40)

# Button styling
COLOR_BTN_NORMAL = (55, 65, 82)
COLOR_BTN_HOVER = (75, 88, 110)
COLOR_BTN_ACTIVE = (45, 54, 68)
COLOR_BTN_ACCENT = (46, 125, 50)
