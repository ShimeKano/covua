"""
Cờ Vua vs Stockfish – Hugging Face Spaces (Gradio)
Chơi cờ vua với AI Stockfish bằng cách click vào quân cờ.
Nếu chơi quân đen, bàn cờ sẽ được xoay ngược.
"""

import os
from typing import Tuple

import chess
import chess.engine
import gradio as gr
from PIL import Image, ImageDraw, ImageFont

# ── Unicode chess pieces ───────────────────────────────────────────────────────
PIECES: dict[tuple[int, bool], str] = {
    (chess.KING, chess.WHITE): "♔",
    (chess.QUEEN, chess.WHITE): "♕",
    (chess.ROOK, chess.WHITE): "♖",
    (chess.BISHOP, chess.WHITE): "♗",
    (chess.KNIGHT, chess.WHITE): "♘",
    (chess.PAWN, chess.WHITE): "♙",
    (chess.KING, chess.BLACK): "♚",
    (chess.QUEEN, chess.BLACK): "♛",
    (chess.ROOK, chess.BLACK): "♜",
    (chess.BISHOP, chess.BLACK): "♝",
    (chess.KNIGHT, chess.BLACK): "♞",
    (chess.PAWN, chess.BLACK): "♟",
}

# ── Stockfish helper ──────────────────────────────────────────────────────────
_SF_CANDIDATES = [
    "/usr/games/stockfish",
    "/usr/bin/stockfish",
    "stockfish",
]


def _find_stockfish() -> str:
    for p in _SF_CANDIDATES:
        if os.path.isfile(p):
            return p
    return "stockfish"  # hope it is on PATH


def _engine_move(board: chess.Board) -> chess.Move | None:
    """Ask Stockfish for one move; fall back to first legal move on error."""
    try:
        with chess.engine.SimpleEngine.popen_uci(_find_stockfish()) as eng:
            result = eng.play(board, chess.engine.Limit(time=1.0))
            return result.move
    except Exception:
        legal = list(board.legal_moves)
        return legal[0] if legal else None


# ── Board rendering ───────────────────────────────────────────────────────────
_SQ_SIZE = 80
_BOARD_SIZE = _SQ_SIZE * 8
_LIGHT = (240, 217, 181)
_DARK = (181, 136, 99)
_SELECTED = (127, 201, 127)
_LAST = (205, 210, 106)


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


_FONT = _load_font(48)


def _display_to_square(row: int, col: int, flipped: bool) -> int:
    if flipped:
        rank = row
        file = 7 - col
    else:
        rank = 7 - row
        file = col
    return chess.square(file, rank)


def _square_to_display(square: int, flipped: bool) -> Tuple[int, int]:
    file = chess.square_file(square)
    rank = chess.square_rank(square)
    if flipped:
        return rank, 7 - file
    return 7 - rank, file


def _render_board(
    board: chess.Board,
    selected: int | None = None,
    valid_targets: list[int] | None = None,
    flipped: bool = False,
) -> Image.Image:
    image = Image.new("RGB", (_BOARD_SIZE, _BOARD_SIZE), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    vt = set(valid_targets or [])

    last_sqs: set[int] = set()
    if board.move_stack:
        lm = board.peek()
        last_sqs = {lm.from_square, lm.to_square}

    for row in range(8):
        for col in range(8):
            sq = _display_to_square(row, col, flipped)
            x0 = col * _SQ_SIZE
            y0 = row * _SQ_SIZE
            x1 = x0 + _SQ_SIZE
            y1 = y0 + _SQ_SIZE

            is_light = (row + col) % 2 == 1
            color = _LIGHT if is_light else _DARK
            if sq == selected:
                color = _SELECTED
            elif sq in last_sqs:
                color = _LAST
            draw.rectangle([x0, y0, x1, y1], fill=color)

            if sq in vt:
                if board.piece_at(sq):
                    draw.ellipse(
                        [x0 + 8, y0 + 8, x1 - 8, y1 - 8],
                        outline=(0, 0, 0),
                        width=4,
                    )
                else:
                    draw.ellipse(
                        [x0 + 28, y0 + 28, x1 - 28, y1 - 28],
                        fill=(0, 0, 0, 80),
                    )

            piece = board.piece_at(sq)
            if piece:
                symbol = PIECES.get((piece.piece_type, piece.color), "?")
                fill = (250, 250, 250) if piece.color == chess.WHITE else (15, 15, 15)
                draw.text(
                    (x0 + _SQ_SIZE / 2, y0 + _SQ_SIZE / 2),
                    symbol,
                    fill=fill,
                    font=_FONT,
                    anchor="mm",
                    stroke_width=2,
                    stroke_fill=(20, 20, 20) if piece.color == chess.WHITE else (220, 220, 220),
                )

    return image


def _pixel_to_square(x: int, y: int, flipped: bool) -> int | None:
    if x is None or y is None:
        return None
    if x < 0 or y < 0 or x >= _BOARD_SIZE or y >= _BOARD_SIZE:
        return None
    col = int(x // _SQ_SIZE)
    row = int(y // _SQ_SIZE)
    return _display_to_square(row, col, flipped)


# ── Default state ─────────────────────────────────────────────────────────────
def _default_state() -> dict:
    return {
        "fen": chess.STARTING_FEN,
        "history": [chess.STARTING_FEN],  # stack of FENs for undo
        "selected": None,
        "valid_targets": [],
        "human_white": True,
        "flipped": False,
        "game_over": False,
    }


def _status_text(board: chess.Board, human_white: bool) -> str:
    if board.is_game_over():
        outcome = board.outcome()
        if outcome and outcome.winner is None:
            return f"🤝 Hòa! ({outcome.termination.name})"
        if outcome and outcome.winner is not None:
            human_color = chess.WHITE if human_white else chess.BLACK
            return "🏆 Bạn thắng!" if outcome.winner == human_color else "😢 Stockfish thắng!"
        return f"🏁 Kết thúc: {board.result()}"
    return "Lượt của bạn 🟢"


# ── Event handlers ────────────────────────────────────────────────────────────
def start_game(color_choice: str, _state: dict) -> tuple[Image.Image, dict, str]:
    """Reset board and optionally let engine play first."""
    human_white = color_choice.startswith("Trắng")
    flipped = not human_white
    board = chess.Board()

    state = _default_state()
    state["human_white"] = human_white
    state["flipped"] = flipped

    if not human_white:
        move = _engine_move(board)
        if move:
            board.push(move)

    state["fen"] = board.fen()
    state["history"] = [board.fen()]
    return _render_board(board, flipped=flipped), state, _status_text(board, human_white)


def handle_click(state: dict, evt: gr.SelectData) -> tuple[Image.Image, dict, str]:
    """Process a square click: select piece or execute move."""
    state = dict(state)
    if evt is None:
        board = chess.Board(state["fen"])
        return _render_board(board, flipped=state["flipped"]), state, _status_text(
            board, state["human_white"]
        )

    board = chess.Board(state["fen"])
    human_white: bool = state["human_white"]
    flipped: bool = state["flipped"]
    human_color = chess.WHITE if human_white else chess.BLACK

    if state.get("game_over"):
        return _render_board(board, flipped=flipped), state, _status_text(board, human_white)

    sq = _pixel_to_square(evt.index[0], evt.index[1], flipped)
    if sq is None:
        return _render_board(board, flipped=flipped), state, _status_text(board, human_white)

    # Ignore clicks when it's not the human's turn
    if board.turn != human_color:
        return _render_board(board, flipped=flipped), state, _status_text(board, human_white)

    selected: int | None = state.get("selected")

    # ── No piece selected yet ──────────────────────────────────────────────────
    if selected is None:
        piece = board.piece_at(sq)
        if piece and piece.color == human_color:
            legal_from = [m for m in board.legal_moves if m.from_square == sq]
            state["selected"] = sq
            state["valid_targets"] = [m.to_square for m in legal_from]
            return (
                _render_board(
                    board,
                    selected=sq,
                    valid_targets=state["valid_targets"],
                    flipped=flipped,
                ),
                state,
                "Chọn ô đến 🎯",
            )
        return _render_board(board, flipped=flipped), state, _status_text(board, human_white)

    # ── A piece is already selected ────────────────────────────────────────────
    if sq == selected:
        state["selected"] = None
        state["valid_targets"] = []
        return _render_board(board, flipped=flipped), state, _status_text(board, human_white)

    own_piece = board.piece_at(sq)
    if own_piece and own_piece.color == human_color:
        legal_from = [m for m in board.legal_moves if m.from_square == sq]
        state["selected"] = sq
        state["valid_targets"] = [m.to_square for m in legal_from]
        return (
            _render_board(
                board,
                selected=sq,
                valid_targets=state["valid_targets"],
                flipped=flipped,
            ),
            state,
            "Chọn ô đến 🎯",
        )

    # Attempt to move selected → sq
    candidates = [
        m for m in board.legal_moves if m.from_square == selected and m.to_square == sq
    ]
    if not candidates:
        return (
            _render_board(
                board,
                selected=selected,
                valid_targets=state["valid_targets"],
                flipped=flipped,
            ),
            state,
            "❌ Nước đi không hợp lệ!",
        )

    move = next((m for m in candidates if m.promotion == chess.QUEEN), candidates[0])
    board.push(move)
    state["selected"] = None
    state["valid_targets"] = []
    state["fen"] = board.fen()

    if board.is_game_over():
        state["game_over"] = True
        return _render_board(board, flipped=flipped), state, _status_text(board, human_white)

    engine_mv = _engine_move(board)
    if engine_mv:
        board.push(engine_mv)
        state["fen"] = board.fen()

    history = list(state.get("history", []))
    history.append(board.fen())
    state["history"] = history

    if board.is_game_over():
        state["game_over"] = True
    return _render_board(board, flipped=flipped), state, _status_text(board, human_white)


def undo_move(state: dict) -> tuple[Image.Image, dict, str]:
    """Undo the last human + engine move pair using the history stack."""
    state = dict(state)
    flipped = state["flipped"]
    history: list[str] = list(state.get("history", []))

    if len(history) <= 1:
        board = chess.Board(state["fen"])
        return _render_board(board, flipped=flipped), state, "⚠️ Không có nước nào để đi lại!"

    history.pop()
    prev_fen = history[-1]

    state["fen"] = prev_fen
    state["history"] = history
    state["selected"] = None
    state["valid_targets"] = []
    state["game_over"] = False

    board = chess.Board(prev_fen)
    return _render_board(board, flipped=flipped), state, "⏪ Đã đi lại. Lượt của bạn 🟢"


# ── Gradio UI ─────────────────────────────────────────────────────────────────
_INITIAL_STATE = _default_state()
_initial_board = _render_board(chess.Board(), flipped=False)

with gr.Blocks(title="Cờ Vua vs Stockfish", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# ♟️ Cờ Vua – Chơi với Stockfish\n"
        "Click vào quân cờ để chọn, rồi click ô đến để di chuyển. "
        "Chơi quân đen → bàn cờ xoay ngược."
    )

    state = gr.State(_INITIAL_STATE)

    with gr.Row():
        color_radio = gr.Radio(
            choices=["Trắng ♔", "Đen ♚"],
            value="Trắng ♔",
            label="Màu quân của bạn",
            scale=2,
        )
        new_game_btn = gr.Button("🎮 Ván mới", variant="primary", scale=1)
        undo_btn = gr.Button("⏪ Đi lại", scale=1)

    status_md = gr.Markdown("Chọn màu quân rồi bấm '🎮 Ván mới' để bắt đầu!")
    board_img = gr.Image(value=_initial_board, type="pil", label="Bàn cờ")

    new_game_btn.click(
        fn=start_game,
        inputs=[color_radio, state],
        outputs=[board_img, state, status_md],
    )

    board_img.select(
        fn=handle_click,
        inputs=[state],
        outputs=[board_img, state, status_md],
    )

    undo_btn.click(
        fn=undo_move,
        inputs=[state],
        outputs=[board_img, state, status_md],
    )

if __name__ == "__main__":
    demo.launch()
