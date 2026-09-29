"""
Vector SVG definitions for chess pieces (Cburnett style).
Provides scalable, anti-aliased surfaces for Pygame.
"""
import io
import pygame

# Standard Cburnett SVG piece definitions (Public Domain / CC BY-SA 3.0)
SVG_TEMPLATES = {
    # White pieces
    ('P', 1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <path d="m 22.5,9 c -2.21,0 -4,1.79 -4,4 0,0.89 0.29,1.71 0.78,2.38 C 17.33,16.5 16,18.59 16,21 c 0,2.03 0.94,3.84 2.41,5.03 C 15.41,27.09 11,31.58 11,39.5 l 23,0 c 0,-7.92 -4.41,-12.41 -7.41,-13.47 1.47,-1.19 2.41,-3 2.41,-5.03 0,-2.41 -1.33,-4.5 -3.28,-5.62 c 0.49,-0.67 0.78,-1.49 0.78,-2.38 0,-2.21 -1.79,-4 -4,-4 z"
        fill="#FFFFFF" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>''',

    ('N', 1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <path d="M 22,10 C 32.5,11 38.5,18 38,39 L 15,39 C 15,30 25,32.5 23,18"
        fill="#FFFFFF" stroke="#222222" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M 24,18 C 24.38,20.91 18.45,25.37 16,27 C 13,29 13.18,31.34 11,31 C 9.958,30.06 12.41,27.96 11,28 C 10,28 11.19,29.23 10,30 C 9,30 5.997,31 6,26 C 6,24 12,14 12,14 C 12,14 13.89,12.1 14,10.5 C 13.27,7.4 17.06,5.06 20,5 C 20,5 20.13,8.21 22,10 z"
        fill="#FFFFFF" stroke="#222222" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="15.5" cy="11.5" r="1.5" fill="#222222"/>
</svg>''',

    ('B', 1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="none" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36 C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5 C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5 C 7.646,38.99 6.677,38.97 6,38 C 7.354,36.54 9,36 9,36 z" fill="#FFFFFF"/>
    <path d="M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30 C 30,27.5 27.5,26 27.5,26 C 33,24.5 33.5,14.5 22.5,10.5 C 11.5,14.5 12,24.5 17.5,26 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z" fill="#FFFFFF"/>
    <path d="M 25 8 A 2.5 2.5 0 1 1 20,8 A 2.5 2.5 0 1 1 25 8 z" fill="#FFFFFF"/>
    <path d="M 17.5,26 L 27.5,26 M 15,30 L 30,30 M 22.5,15.5 L 22.5,20.5 M 20,18 L 25,18"/>
  </g>
</svg>''',

    ('R', 1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="#FFFFFF" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 9,39 L 36,39 L 36,36 L 9,36 L 9,39 z"/>
    <path d="M 12,36 L 12,32 L 33,32 L 33,36 L 12,36 z"/>
    <path d="M 11,14 L 11,9 L 15,9 L 15,11 L 20,11 L 20,9 L 25,9 L 25,11 L 30,11 L 30,9 L 34,9 L 34,14"/>
    <path d="M 34,14 L 31,17 L 14,17 L 11,14"/>
    <path d="M 31,17 L 31,29.5 L 14,29.5 L 14,17"/>
    <path d="M 11,32 L 34,32 L 31,29.5 L 14,29.5 L 11,32"/>
  </g>
</svg>''',

    ('Q', 1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="#FFFFFF" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 9,26 C 17.5,24.5 30,24.5 36,26 L 38.5,13.5 L 31,25 L 22.5,10 L 14,25 L 6.5,13.5 L 9,26 z"/>
    <path d="M 9,26 C 9,28 10.5,28 11.5,30 C 12.5,31.5 12.5,31 12,33.5 C 10.5,34.5 10.5,36 10.5,36 C 9,37.5 11,38.5 11,38.5 L 34,38.5 C 34,38.5 36,37.5 34.5,36 C 34.5,36 34.5,34.5 33,33.5 C 32.5,31 32.5,31.5 33.5,30 C 34.5,28 36,28 36,26"/>
    <path d="M 11.5,30 C 15,29 30,29 33.5,30 M 12,33.5 C 18,32.5 27,32.5 33,33.5"/>
    <circle cx="6" cy="12" r="2" fill="#FFFFFF"/>
    <circle cx="14" cy="9" r="2" fill="#FFFFFF"/>
    <circle cx="22.5" cy="8" r="2" fill="#FFFFFF"/>
    <circle cx="31" cy="9" r="2" fill="#FFFFFF"/>
    <circle cx="39" cy="12" r="2" fill="#FFFFFF"/>
  </g>
</svg>''',

    ('K', 1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="none" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 22.5,11.63 L 22.5,6 M 20,8 L 25,8"/>
    <path d="M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 24,11.5 21,11.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25" fill="#FFFFFF"/>
    <path d="M 11.5,37 C 17,40.5 28,40.5 33.5,37 C 36.5,31 34.5,26.5 32,23 C 27,27 18,27 13,23 C 10.5,26.5 8.5,31 11.5,37 z" fill="#FFFFFF"/>
    <path d="M 11.5,30 C 17,27 28,27 33.5,30 M 11.5,33.5 C 17,30.5 28,30.5 33.5,33.5"/>
  </g>
</svg>''',

    # Black pieces
    ('P', -1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <path d="m 22.5,9 c -2.21,0 -4,1.79 -4,4 0,0.89 0.29,1.71 0.78,2.38 C 17.33,16.5 16,18.59 16,21 c 0,2.03 0.94,3.84 2.41,5.03 C 15.41,27.09 11,31.58 11,39.5 l 23,0 c 0,-7.92 -4.41,-12.41 -7.41,-13.47 1.47,-1.19 2.41,-3 2.41,-5.03 0,-2.41 -1.33,-4.5 -3.28,-5.62 c 0.49,-0.67 0.78,-1.49 0.78,-2.38 0,-2.21 -1.79,-4 -4,-4 z"
        fill="#262626" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>''',

    ('N', -1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <path d="M 22,10 C 32.5,11 38.5,18 38,39 L 15,39 C 15,30 25,32.5 23,18"
        fill="#262626" stroke="#222222" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M 24,18 C 24.38,20.91 18.45,25.37 16,27 C 13,29 13.18,31.34 11,31 C 9.958,30.06 12.41,27.96 11,28 C 10,28 11.19,29.23 10,30 C 9,30 5.997,31 6,26 C 6,24 12,14 12,14 C 12,14 13.89,12.1 14,10.5 C 13.27,7.4 17.06,5.06 20,5 C 20,5 20.13,8.21 22,10 z"
        fill="#262626" stroke="#222222" stroke-width="1.5" stroke-linejoin="round"/>
  <circle cx="15.5" cy="11.5" r="1.5" fill="#E6E6E6"/>
</svg>''',

    ('B', -1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="none" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 9,36 C 12.39,35.03 19.11,36.43 22.5,34 C 25.89,36.43 32.61,35.03 36,36 C 36,36 37.65,36.54 39,38 C 38.32,38.97 37.35,38.99 36,38.5 C 32.61,37.53 25.89,38.96 22.5,37.5 C 19.11,38.96 12.39,37.53 9,38.5 C 7.646,38.99 6.677,38.97 6,38 C 7.354,36.54 9,36 9,36 z" fill="#262626"/>
    <path d="M 15,32 C 17.5,34.5 27.5,34.5 30,32 C 30.5,30.5 30,30 30,30 C 30,27.5 27.5,26 27.5,26 C 33,24.5 33.5,14.5 22.5,10.5 C 11.5,14.5 12,24.5 17.5,26 C 17.5,26 15,27.5 15,30 C 15,30 14.5,30.5 15,32 z" fill="#262626"/>
    <path d="M 25 8 A 2.5 2.5 0 1 1 20,8 A 2.5 2.5 0 1 1 25 8 z" fill="#262626"/>
    <path d="M 17.5,26 L 27.5,26 M 15,30 L 30,30 M 22.5,15.5 L 22.5,20.5 M 20,18 L 25,18" stroke="#E6E6E6"/>
  </g>
</svg>''',

    ('R', -1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="#262626" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 9,39 L 36,39 L 36,36 L 9,36 L 9,39 z"/>
    <path d="M 12,36 L 12,32 L 33,32 L 33,36 L 12,36 z"/>
    <path d="M 11,14 L 11,9 L 15,9 L 15,11 L 20,11 L 20,9 L 25,9 L 25,11 L 30,11 L 30,9 L 34,9 L 34,14"/>
    <path d="M 34,14 L 31,17 L 14,17 L 11,14"/>
    <path d="M 31,17 L 31,29.5 L 14,29.5 L 14,17"/>
    <path d="M 11,32 L 34,32 L 31,29.5 L 14,29.5 L 11,32"/>
  </g>
</svg>''',

    ('Q', -1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="#262626" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 9,26 C 17.5,24.5 30,24.5 36,26 L 38.5,13.5 L 31,25 L 22.5,10 L 14,25 L 6.5,13.5 L 9,26 z"/>
    <path d="M 9,26 C 9,28 10.5,28 11.5,30 C 12.5,31.5 12.5,31 12,33.5 C 10.5,34.5 10.5,36 10.5,36 C 9,37.5 11,38.5 11,38.5 L 34,38.5 C 34,38.5 36,37.5 34.5,36 C 34.5,36 34.5,34.5 33,33.5 C 32.5,31 32.5,31.5 33.5,30 C 34.5,28 36,28 36,26"/>
    <path d="M 11.5,30 C 15,29 30,29 33.5,30 M 12,33.5 C 18,32.5 27,32.5 33,33.5" stroke="#E6E6E6"/>
    <circle cx="6" cy="12" r="2" fill="#262626"/>
    <circle cx="14" cy="9" r="2" fill="#262626"/>
    <circle cx="22.5" cy="8" r="2" fill="#262626"/>
    <circle cx="31" cy="9" r="2" fill="#262626"/>
    <circle cx="39" cy="12" r="2" fill="#262626"/>
  </g>
</svg>''',

    ('K', -1): '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 45 45" width="{size}" height="{size}">
  <g fill="none" fill-rule="evenodd" stroke="#222222" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M 22.5,11.63 L 22.5,6 M 20,8 L 25,8" stroke="#E6E6E6"/>
    <path d="M 22.5,25 C 22.5,25 27,17.5 25.5,14.5 C 24,11.5 21,11.5 19.5,14.5 C 18,17.5 22.5,25 22.5,25" fill="#262626"/>
    <path d="M 11.5,37 C 17,40.5 28,40.5 33.5,37 C 36.5,31 34.5,26.5 32,23 C 27,27 18,27 13,23 C 10.5,26.5 8.5,31 11.5,37 z" fill="#262626"/>
    <path d="M 11.5,30 C 17,27 28,27 33.5,30 M 11.5,33.5 C 17,30.5 28,30.5 33.5,33.5" stroke="#E6E6E6"/>
  </g>
</svg>''',
}

_surface_cache = {}

def get_piece_surface(piece_symbol: str, color: int, size: int = 80) -> pygame.Surface:
    """
    Returns a rendered Pygame Surface for the given piece and size.
    piece_symbol: 'P', 'N', 'B', 'R', 'Q', 'K'
    color: 1 for White, -1 for Black
    size: pixel width/height (square)
    """
    key = (piece_symbol.upper(), color, size)
    if key in _surface_cache:
        return _surface_cache[key]
    
    template = SVG_TEMPLATES.get((piece_symbol.upper(), color))
    if not template:
        raise ValueError(f"Unknown piece: {piece_symbol}, color: {color}")
    
    svg_str = template.format(size=size)
    surf = pygame.image.load(io.BytesIO(svg_str.encode('utf-8')), "piece.svg").convert_alpha()
    _surface_cache[key] = surf
    return surf
