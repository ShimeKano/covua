"""Self-contained Staunton-inspired SVG chess-piece icons."""

import chess

# Simplified original silhouettes, designed to read clearly at board-cell size.
_SHAPES = {
    chess.KING: '<path d="M46 5h8v10h10v7H54v9h-8v-9H36v-7h10z M34 35h32l-4 8H38z M38 43h24l7 12H31z M29 56h42l7 10H22z M22 67h56l8 12H14z M12 80h76l7 11H5z"/>',
    chess.QUEEN: '<path d="M22 16l8 15 12-17 8 17 12-17 8 17 8-15-8 31H30z M32 48h36l-5 9H37z M28 58h44l7 11H21z M18 70h64l8 11H10z M7 82h86l5 9H2z"/><circle cx="22" cy="13" r="5"/><circle cx="42" cy="10" r="5"/><circle cx="58" cy="10" r="5"/><circle cx="78" cy="13" r="5"/>',
    chess.ROOK: '<path d="M19 13h13v12h8V13h20v12h8V13h13v24l-7 7v14H27V44l-8-7z M28 59h44l6 10H22z M19 70h62l8 11H11z M7 82h86l5 9H2z"/>',
    chess.BISHOP: '<path d="M50 7C40 18 35 25 38 34c2 7 7 11 12 14 5-3 10-7 12-14 3-9-2-16-12-27z M47 18l8 13 M39 46h22l-3 10H42z M33 57h34l8 12H25z M21 70h58l8 11H13z M7 82h86l5 9H2z"/>',
    chess.KNIGHT: '<path d="M25 78h52l9 13H14z M26 77l3-15-10-10 7-14 18-18 18 5 12 15-4 12-12 7-4 11 12 7H34l4-15-9-7 4-9-9 7 8 12-1 12z"/><path d="M43 30l7 5-6 6-7-5z" fill="#fffdf7" stroke="none"/>',
    chess.PAWN: '<circle cx="50" cy="25" r="15"/><path d="M39 42c4-5 18-5 22 0l-3 11 10 12H32l10-12z M30 66h40l7 11H23z M17 78h66l8 12H9z M5 91h90v4H5z"/>',
}


def piece_svg(piece_type: int, white: bool) -> str:
    """Return a self-contained, accessible SVG icon for a chess piece."""
    body = _SHAPES.get(piece_type, _SHAPES[chess.PAWN])
    fill = "#fffdf7" if white else "#171717"
    stroke = "#171717" if white else "#fffdf7"
    label = f'{"White" if white else "Black"} {chess.piece_name(piece_type)}'
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        f'role="img" aria-label="{label}" focusable="false">'
        f'<g fill="{fill}" stroke="{stroke}" stroke-width="3.2" '
        f'stroke-linejoin="round" stroke-linecap="round">{body}</g></svg>'
    )
