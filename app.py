"""
Cờ Vua vs Stockfish – Hugging Face Spaces (Gradio)
Chơi cờ vua với AI Stockfish bằng cách click vào quân cờ.
Nếu chơi quân đen, bàn cờ sẽ được xoay ngược.
"""

import os
import chess
import chess.engine
import gradio as gr

# ── Unicode chess pieces ───────────────────────────────────────────────────────
PIECES: dict[tuple[int, bool], str] = {
    (chess.KING,   chess.WHITE): "♔",
    (chess.QUEEN,  chess.WHITE): "♕",
    (chess.ROOK,   chess.WHITE): "♖",
    (chess.BISHOP, chess.WHITE): "♗",
    (chess.KNIGHT, chess.WHITE): "♘",
    (chess.PAWN,   chess.WHITE): "♙",
    (chess.KING,   chess.BLACK): "♚",
    (chess.QUEEN,  chess.BLACK): "♛",
    (chess.ROOK,   chess.BLACK): "♜",
    (chess.BISHOP, chess.BLACK): "♝",
    (chess.KNIGHT, chess.BLACK): "♞",
    (chess.PAWN,   chess.BLACK): "♟",
}

# ── Stockfish helper ───────────────────────────────────────────────────────────
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


# ── Board HTML renderer ────────────────────────────────────────────────────────
_CSS = """
<style>
#chess-app{font-family:Arial,sans-serif;display:flex;flex-direction:column;
  align-items:center;padding:12px;user-select:none}
.st{font-size:20px;font-weight:700;margin:6px 0 10px;min-height:28px;
  text-align:center;color:#222}
.bw{display:flex;align-items:flex-start}
.rls{display:flex;flex-direction:column;margin-right:4px}
.rl{width:22px;height:68px;display:flex;align-items:center;
  justify-content:center;font-size:13px;color:#666}
.fl{width:68px;height:22px;display:flex;align-items:center;
  justify-content:center;font-size:13px;color:#666}
.fls{display:flex;margin-top:2px;margin-left:26px}
.board{display:grid;grid-template-columns:repeat(8,68px);
  grid-template-rows:repeat(8,68px);
  border:3px solid #444;box-shadow:4px 6px 18px rgba(0,0,0,.45)}
.sq{width:68px;height:68px;display:flex;align-items:center;
  justify-content:center;cursor:pointer;position:relative;
  transition:filter .08s}
.sq:hover{filter:brightness(.88)}
.lt{background:#f0d9b5}.dk{background:#b58863}
.sel{background:#7fc97f!important}
.edsel{background:#f6c445!important;box-shadow:inset 0 0 0 4px #8a5a00}
.mv::after{content:'';position:absolute;width:24px;height:24px;
  background:rgba(0,0,0,.22);border-radius:50%;pointer-events:none;z-index:2}
.cap::after{content:'';position:absolute;width:62px;height:62px;
  background:transparent;border:5px solid rgba(0,0,0,.22);
  border-radius:50%;pointer-events:none;z-index:2}
.last{background:#cdd26a!important}
.wp{font-size:50px;line-height:1;color:#fff;
  -webkit-text-stroke:1.8px #111;
  text-shadow:0 2px 2px rgba(0,0,0,.75),0 0 5px rgba(0,0,0,.65)}
.bp{font-size:50px;line-height:1;color:#080808;
  -webkit-text-stroke:1.5px #fff;
  text-shadow:0 2px 2px rgba(255,255,255,.55),0 0 5px rgba(255,255,255,.45)}
</style>
"""

_JS = """
<script>
function sqClick(sq){
  var ts = sq+'_'+Date.now();
  // Try both textarea (Gradio 3) and input (Gradio 4)
  var inp = document.querySelector('#sq-input textarea') ||
            document.querySelector('#sq-input input[type="text"]') ||
            document.querySelector('#sq-input input');
  if(!inp){
    var w=document.getElementById('sq-input');
    if(w) inp=w.querySelector('textarea,input');
  }
  if(!inp) return;
  try{
    var proto = inp.tagName==='TEXTAREA'
      ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
    var setter = Object.getOwnPropertyDescriptor(proto,'value');
    if(setter && setter.set) setter.set.call(inp, ts);
    else inp.value=ts;
  } catch(e){ inp.value=ts; }
  inp.dispatchEvent(new InputEvent('input',{bubbles:true,cancelable:true}));
  inp.dispatchEvent(new Event('change',{bubbles:true}));
}
</script>
"""


def _make_board_html(
    board: chess.Board,
    selected: int | None = None,
    valid_targets: list[int] | None = None,
    flipped: bool = False,
    status: str = "",
    editor_mode: bool = False,
    editor_square: int | None = None,
) -> str:
    vt = set(valid_targets or [])
    last_sqs: set[int] = set()
    if board.move_stack:
        lm = board.peek()
        last_sqs = {lm.from_square, lm.to_square}

    rows = range(7, -1, -1) if not flipped else range(8)
    cols = range(8) if not flipped else range(7, -1, -1)

    cells: list[str] = []
    for rank in rows:
        for file in cols:
            sq = chess.square(file, rank)
            piece = board.piece_at(sq)

            is_light = (rank + file) % 2 == 1
            cls = ["sq", "lt" if is_light else "dk"]

            if editor_mode and sq == editor_square:
                cls.append("edsel")
            elif sq == selected:
                cls.append("sel")
            elif sq in vt:
                cls.append("cap" if piece else "mv")
            if sq in last_sqs and sq != selected:
                cls.append("last")

            inner = ""
            if piece:
                sym = PIECES.get((piece.piece_type, piece.color), "?")
                pc = "wp" if piece.color == chess.WHITE else "bp"
                inner = f'<span class="{pc}">{sym}</span>'

            cells.append(
                f'<div class="{" ".join(cls)}" onclick="sqClick({sq})">{inner}</div>'
            )

    rank_labels = "".join(
        f'<div class="rl">{r + 1}</div>'
        for r in (range(7, -1, -1) if not flipped else range(8))
    )
    file_str = "abcdefgh" if not flipped else "hgfedcba"
    file_labels = "".join(f'<div class="fl">{c}</div>' for c in file_str)

    board_grid = "".join(cells)
    return (
        f"{_CSS}"
        f'<div id="chess-app">'
        f'  <div class="st">{status}</div>'
        f'  <div class="bw">'
        f'    <div class="rls">{rank_labels}</div>'
        f'    <div>'
        f'      <div class="board">{board_grid}</div>'
        f'      <div class="fls">{file_labels}</div>'
        f'    </div>'
        f'  </div>'
        f"</div>"
        f"{_JS}"
    )



# ── Default state ──────────────────────────────────────────────────────────────
def _default_state() -> dict:
    return {
        "fen": chess.STARTING_FEN,
        "history": [chess.STARTING_FEN],
        "selected": None,
        "valid_targets": [],
        "human_white": True,
        "flipped": False,
        "game_over": False,
        "editor_mode": False,
        "editor_square": None,
    }


# ── Event handlers ─────────────────────────────────────────────────────────────
def _render(board: chess.Board, state: dict, status: str = "") -> str:
    return _make_board_html(
        board,
        selected=state.get("selected"),
        valid_targets=state.get("valid_targets", []),
        flipped=state.get("flipped", False),
        status=status,
        editor_mode=state.get("editor_mode", False),
        editor_square=state.get("editor_square"),
    )


def start_game(color_choice: str, _state: dict):
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
    status = "Lượt của bạn 🟢" if not board.is_game_over() else "🏁 Ván kết thúc!"
    return _render(board, state, status), state, "🛠️ Chế độ xếp cờ", gr.update(), ""


def _outcome_status(board: chess.Board, human_white: bool) -> str:
    outcome = board.outcome()
    if outcome is None:
        return f"🏁 Kết thúc: {board.result()}"
    if outcome.winner is None:
        return f"🤝 Hòa! ({outcome.termination.name})"
    human_color = chess.WHITE if human_white else chess.BLACK
    if outcome.winner == human_color:
        return "🏆 Bạn thắng!"
    return "😢 Stockfish thắng!"


def handle_click(sq_str: str, state: dict):
    """Handle a board click in either normal play mode or editor mode."""
    state = dict(state)
    if not sq_str:
        return gr.update(), state, gr.update(), gr.update(), gr.update()

    try:
        sq = int(sq_str.split("_")[0])
    except ValueError:
        return gr.update(), state, gr.update(), gr.update(), gr.update()

    board = chess.Board(state["fen"])

    # ── Editor mode: clicking the main board only selects the square. ─────────
    if state.get("editor_mode"):
        state["editor_square"] = sq
        square_name = chess.square_name(sq)
        return (
            _render(board, state, f"🛠️ Đang chỉnh **{square_name}** — chọn quân bên dưới."),
            state,
            square_name,
            board.fen(),
            f"📍 Ô đang chọn: **{square_name}**",
        )

    if state.get("game_over"):
        return (
            _render(board, state, _outcome_status(board, state["human_white"])),
            state,
            gr.update(),
            gr.update(),
            gr.update(),
        )

    human_white = state["human_white"]
    flipped = state["flipped"]
    human_color = chess.WHITE if human_white else chess.BLACK

    if board.turn != human_color:
        return _render(board, state, "⏳ Đang chờ Stockfish..."), state, gr.update(), gr.update(), gr.update()

    selected = state.get("selected")

    if selected is None:
        piece = board.piece_at(sq)
        if piece and piece.color == human_color:
            legal_from = [m for m in board.legal_moves if m.from_square == sq]
            state["selected"] = sq
            state["valid_targets"] = [m.to_square for m in legal_from]
            return _render(board, state, "Chọn ô đến 🎯"), state, gr.update(), gr.update(), gr.update()

        return _render(board, state, "Lượt của bạn 🟢"), state, gr.update(), gr.update(), gr.update()

    if sq == selected:
        state["selected"] = None
        state["valid_targets"] = []
        return _render(board, state, "Lượt của bạn 🟢"), state, gr.update(), gr.update(), gr.update()

    own_piece = board.piece_at(sq)
    if own_piece and own_piece.color == human_color:
        legal_from = [m for m in board.legal_moves if m.from_square == sq]
        state["selected"] = sq
        state["valid_targets"] = [m.to_square for m in legal_from]
        return _render(board, state, "Chọn ô đến 🎯"), state, gr.update(), gr.update(), gr.update()

    candidates = [
        m for m in board.legal_moves
        if m.from_square == selected and m.to_square == sq
    ]
    if not candidates:
        return _render(board, state, "❌ Nước đi không hợp lệ!"), state, gr.update(), gr.update(), gr.update()

    move = next((m for m in candidates if m.promotion == chess.QUEEN), candidates[0])
    board.push(move)
    state["selected"] = None
    state["valid_targets"] = []
    state["fen"] = board.fen()

    if board.is_game_over():
        state["game_over"] = True
        return _render(board, state, _outcome_status(board, human_white)), state, gr.update(), gr.update(), gr.update()

    engine_mv = _engine_move(board)
    if engine_mv:
        board.push(engine_mv)
        state["fen"] = board.fen()

    history = list(state.get("history", []))
    history.append(board.fen())
    state["history"] = history

    if board.is_game_over():
        state["game_over"] = True
        status = _outcome_status(board, human_white)
    else:
        status = "Lượt của bạn 🟢"

    return _render(board, state, status), state, gr.update(), gr.update(), gr.update()


def undo_move(state: dict):
    state = dict(state)
    if state.get("editor_mode"):
        board = chess.Board(state["fen"])
        return _render(board, state, "🛠️ Đang ở chế độ xếp cờ."), state, gr.update(), gr.update(), gr.update()

    history = list(state.get("history", []))
    if len(history) <= 1:
        board = chess.Board(state["fen"])
        return _render(board, state, "⚠️ Không có nước nào để đi lại!"), state, gr.update(), gr.update(), gr.update()

    history.pop()
    prev_fen = history[-1]
    state["fen"] = prev_fen
    state["history"] = history
    state["selected"] = None
    state["valid_targets"] = []
    state["game_over"] = False

    board = chess.Board(prev_fen)
    return _render(board, state, "⏪ Đã đi lại. Lượt của bạn 🟢"), state, gr.update(), gr.update(), gr.update()


# ── Main-board editor ──────────────────────────────────────────────────────────
PIECE_CHOICES = {
    "Trống": None,
    "Trắng ♔ Vua": chess.Piece(chess.KING, chess.WHITE),
    "Trắng ♕ Hậu": chess.Piece(chess.QUEEN, chess.WHITE),
    "Trắng ♖ Xe": chess.Piece(chess.ROOK, chess.WHITE),
    "Trắng ♗ Tượng": chess.Piece(chess.BISHOP, chess.WHITE),
    "Trắng ♘ Mã": chess.Piece(chess.KNIGHT, chess.WHITE),
    "Trắng ♙ Tốt": chess.Piece(chess.PAWN, chess.WHITE),
    "Đen ♚ Vua": chess.Piece(chess.KING, chess.BLACK),
    "Đen ♛ Hậu": chess.Piece(chess.QUEEN, chess.BLACK),
    "Đen ♜ Xe": chess.Piece(chess.ROOK, chess.BLACK),
    "Đen ♝ Tượng": chess.Piece(chess.BISHOP, chess.BLACK),
    "Đen ♞ Mã": chess.Piece(chess.KNIGHT, chess.BLACK),
    "Đen ♟ Tốt": chess.Piece(chess.PAWN, chess.BLACK),
}


def _safe_board(fen: str) -> chess.Board:
    return chess.Board(fen.strip())


def toggle_editor(state: dict):
    state = dict(state)
    board = chess.Board(state["fen"])
    entering = not state.get("editor_mode", False)

    state["editor_mode"] = entering
    state["selected"] = None
    state["valid_targets"] = []
    state["game_over"] = False

    if entering:
        state["editor_square"] = None
        return (
            _render(board, state, "🛠️ Chế độ xếp cờ: click một ô trên bàn cờ để chọn vị trí."),
            state,
            "↩️ Thoát xếp cờ",
            board.fen(),
            "🛠️ Đang chỉnh bàn cờ chính.",
        )

    state["editor_square"] = None
    status = "Lượt của bạn 🟢" if board.turn == (chess.WHITE if state["human_white"] else chess.BLACK) else "⏳ Đang chờ Stockfish..."
    return _render(board, state, status), state, "🛠️ Chế độ xếp cờ", board.fen(), ""


def edit_square(state: dict, piece_name: str):
    state = dict(state)
    if not state.get("editor_mode"):
        return gr.update(), state, gr.update(), "⚠️ Hãy bật chế độ xếp cờ trước."

    sq = state.get("editor_square")
    if sq is None:
        return gr.update(), state, gr.update(), "⚠️ Hãy click một ô trên bàn cờ trước."

    try:
        board = _safe_board(state["fen"])
        board.set_piece_at(sq, PIECE_CHOICES.get(piece_name))
        board.clear_stack()
        state["fen"] = board.fen()
        square_name = chess.square_name(sq)
        return _render(board, state, f"✏️ Đã đặt/thay **{piece_name}** tại **{square_name}**."), state, board.fen(), f"✏️ Đã cập nhật **{square_name}**."
    except Exception as exc:
        return gr.update(), state, gr.update(), f"❌ Không thể chỉnh bàn cờ: {exc}"


def clear_square(state: dict):
    state = dict(state)
    if not state.get("editor_mode"):
        return gr.update(), state, gr.update(), "⚠️ Hãy bật chế độ xếp cờ trước."

    sq = state.get("editor_square")
    if sq is None:
        return gr.update(), state, gr.update(), "⚠️ Hãy click một ô trên bàn cờ trước."

    board = _safe_board(state["fen"])
    board.remove_piece_at(sq)
    board.clear_stack()
    state["fen"] = board.fen()
    square_name = chess.square_name(sq)
    return _render(board, state, f"🗑️ Đã xóa quân tại **{square_name}**."), state, board.fen(), f"🗑️ Đã xóa **{square_name}**."


def clear_custom_board(state: dict):
    state = dict(state)
    board = chess.Board.empty()
    state["fen"] = board.fen()
    state["selected"] = None
    state["valid_targets"] = []
    state["editor_square"] = None
    return _render(board, state, "🧹 Đã xóa toàn bộ quân. Hãy đặt đủ hai vua trước khi chơi."), state, board.fen(), "🧹 Đã xóa toàn bộ quân."


def reset_custom_board(state: dict):
    state = dict(state)
    board = chess.Board()
    state["fen"] = board.fen()
    state["selected"] = None
    state["valid_targets"] = []
    state["editor_square"] = None
    return _render(board, state, "♟️ Đã khôi phục vị trí ban đầu."), state, board.fen(), "♟️ Đã khôi phục vị trí ban đầu."


def validate_fen(fen: str) -> str:
    try:
        board = _safe_board(fen)
        if not board.is_valid():
            return "⚠️ FEN đọc được nhưng vị trí chưa hợp lệ theo luật cờ vua. Bạn vẫn có thể tiếp tục chỉnh sửa."
        return "✅ FEN hợp lệ."
    except Exception as exc:
        return f"❌ FEN không hợp lệ: {exc}"


def apply_fen(fen: str, state: dict):
    state = dict(state)
    try:
        board = _safe_board(fen)
    except Exception as exc:
        return gr.update(), state, gr.update(), f"❌ FEN không hợp lệ: {exc}"

    if not board.is_valid():
        return _render(board, state, "⚠️ Vị trí chưa hợp lệ: cần đúng 2 vua và trạng thái cờ hợp lệ."), state, board.fen(), "⚠️ Hãy sửa FEN trước khi áp dụng."

    state["fen"] = board.fen()
    state["selected"] = None
    state["valid_targets"] = []
    state["editor_square"] = None
    return _render(board, state, "🛠️ Đã áp dụng FEN lên bàn cờ chính."), state, board.fen(), "✅ Đã áp dụng FEN."


def start_custom_game(color_choice: str, fen: str, _state: dict):
    state = dict(_state)
    try:
        board = _safe_board(fen)
    except Exception as exc:
        return gr.update(), state, gr.update(), gr.update(), f"❌ FEN không hợp lệ: {exc}"

    if not board.is_valid():
        return (
            _render(board, state, "❌ Vị trí chưa hợp lệ. Cần đủ 2 vua và trạng thái cờ hợp lệ."),
            state,
            gr.update(),
            board.fen(),
            "❌ Chưa thể bắt đầu từ vị trí này.",
        )

    human_white = color_choice.startswith("Trắng")
    human_color = chess.WHITE if human_white else chess.BLACK
    flipped = not human_white

    state = _default_state()
    state["human_white"] = human_white
    state["flipped"] = flipped
    state["fen"] = board.fen()
    state["history"] = [board.fen()]

    if board.turn != human_color and not board.is_game_over():
        move = _engine_move(board)
        if move:
            board.push(move)
            state["fen"] = board.fen()
            state["history"] = [board.fen()]

    state["game_over"] = board.is_game_over()
    status = _outcome_status(board, human_white) if board.is_game_over() else "Lượt của bạn 🟢"
    return _render(board, state, status), state, "🛠️ Chế độ xếp cờ", board.fen(), "▶️ Đã bắt đầu chơi từ vị trí này."


# ── Gradio UI ──────────────────────────────────────────────────────────────────
_INITIAL_STATE = _default_state()
_initial_board = _make_board_html(
    chess.Board(),
    flipped=False,
    status="Chọn màu quân rồi bấm '🎮 Ván mới' để bắt đầu!",
)

with gr.Blocks(title="Cờ Vua vs Stockfish", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# ♟️ Cờ Vua – Chơi với Stockfish\n"
        "Click quân cờ để di chuyển. Bật **🛠️ Chế độ xếp cờ** để chỉnh trực tiếp trên chính bàn cờ. "
        "Ứng dụng chạy CPU, không cần GPU."
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
        editor_mode_btn = gr.Button("🛠️ Chế độ xếp cờ", scale=1)

    board_html = gr.HTML(value=_initial_board)

    with gr.Accordion("♟️ Công cụ xếp cờ", open=False):
        gr.Markdown(
            "Đây là **chính bàn cờ đang chơi**. Bật chế độ xếp cờ, click ô cần sửa, "
            "chọn quân rồi bấm **Đặt / thay quân**. Bạn có thể xóa từng ô hoặc toàn bộ bàn cờ."
        )

        with gr.Row():
            editor_piece = gr.Dropdown(
                choices=list(PIECE_CHOICES.keys()),
                value="Trắng ♙ Tốt",
                label="Quân muốn đặt / thay",
                scale=2,
            )
            place_piece_btn = gr.Button("♟️ Đặt / thay quân", variant="primary", scale=1)
            clear_selected_btn = gr.Button("🗑️ Xóa ô đang chọn", scale=1)
            clear_board_btn = gr.Button("🧹 Xóa hết", scale=1)
            reset_board_btn = gr.Button("♟️ Vị trí ban đầu", scale=1)

        custom_fen = gr.Textbox(
            value=chess.STARTING_FEN,
            label="FEN của vị trí hiện tại",
            lines=2,
        )

        with gr.Row():
            validate_fen_btn = gr.Button("🔎 Kiểm tra FEN")
            apply_fen_btn = gr.Button("📋 Áp dụng FEN", variant="secondary")
            use_custom_btn = gr.Button("▶️ Xếp cờ → Chơi", variant="primary")

        editor_status = gr.Markdown("Bật chế độ xếp cờ rồi click một ô trên bàn cờ.")

    sq_input = gr.Textbox(value="", visible=False, elem_id="sq-input", label="square")

    new_game_btn.click(
        fn=start_game,
        inputs=[color_radio, state],
        outputs=[board_html, state, editor_mode_btn, custom_fen, editor_status],
    )

    sq_input.input(
        fn=handle_click,
        inputs=[sq_input, state],
        outputs=[board_html, state, editor_mode_btn, custom_fen, editor_status],
    )

    undo_btn.click(
        fn=undo_move,
        inputs=[state],
        outputs=[board_html, state, gr.update(), custom_fen, editor_status],
    )

    editor_mode_btn.click(
        fn=toggle_editor,
        inputs=[state],
        outputs=[board_html, state, editor_mode_btn, custom_fen, editor_status],
    )

    place_piece_btn.click(
        fn=edit_square,
        inputs=[state, editor_piece],
        outputs=[board_html, state, custom_fen, editor_status],
    )

    clear_selected_btn.click(
        fn=clear_square,
        inputs=[state],
        outputs=[board_html, state, custom_fen, editor_status],
    )

    clear_board_btn.click(
        fn=clear_custom_board,
        inputs=[state],
        outputs=[board_html, state, custom_fen, editor_status],
    )

    reset_board_btn.click(
        fn=reset_custom_board,
        inputs=[state],
        outputs=[board_html, state, custom_fen, editor_status],
    )

    validate_fen_btn.click(
        fn=validate_fen,
        inputs=[custom_fen],
        outputs=[editor_status],
    )

    apply_fen_btn.click(
        fn=apply_fen,
        inputs=[custom_fen, state],
        outputs=[board_html, state, custom_fen, editor_status],
    )

    use_custom_btn.click(
        fn=start_custom_game,
        inputs=[color_radio, custom_fen, state],
        outputs=[board_html, state, editor_mode_btn, custom_fen, editor_status],
    )


if __name__ == "__main__":
    demo.launch()
