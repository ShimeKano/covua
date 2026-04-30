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


# ── Board HTML renderer ───────────────────────────────────────────────────────
_CSS = """
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
.mv::after{content:'';position:absolute;width:24px;height:24px;
  background:rgba(0,0,0,.22);border-radius:50%;pointer-events:none;z-index:2}
.cap::after{content:'';position:absolute;width:62px;height:62px;
  background:transparent;border:5px solid rgba(0,0,0,.22);
  border-radius:50%;pointer-events:none;z-index:2}
.last{background:#cdd26a!important}
.wp{font-size:48px;line-height:1;color:#fff;
  text-shadow:0 0 2px #000,0 0 4px #000,1px 1px 0 #444}
.bp{font-size:48px;line-height:1;color:#111;
  text-shadow:0 0 1px #888,1px 1px 0 #eee}
"""

_JS = """
function sqClick(sq){
  var ts = sq + '_' + Date.now();
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
window.sqClick = sqClick;
"""


def _make_board_html(
    board: chess.Board,
    selected: int | None = None,
    valid_targets: list[int] | None = None,
    flipped: bool = False,
    status: str = "",
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

            if sq == selected:
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
                f'<div class="{" ".join(cls)}" onclick="window.sqClick({sq})">{inner}</div>'
            )

    rank_labels = "".join(
        f'<div class="rl">{r + 1}</div>'
        for r in (range(7, -1, -1) if not flipped else range(8))
    )
    file_str = "abcdefgh" if not flipped else "hgfedcba"
    file_labels = "".join(f'<div class="fl">{c}</div>' for c in file_str)

    board_grid = "".join(cells)
    return (
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
    )


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


# ── Event handlers ────────────────────────────────────────────────────────────
def start_game(color_choice: str, _state: dict) -> tuple[str, dict]:
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
    status = "Lượt của bạn 🟢" if not board.is_game_over() else "🏁 Ván kết thúc!"
    return _make_board_html(board, flipped=flipped, status=status), state


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


def handle_click(sq_str: str, state: dict) -> tuple[str, dict]:
    """Process a square click: select piece or execute move."""
    state = dict(state)  # work on a copy so callers are not mutated
    if not sq_str:
        return gr.update(), state

    # sq_str is "square_timestamp" to ensure every click triggers change
    try:
        sq = int(sq_str.split("_")[0])
    except ValueError:
        return gr.update(), state

    if state.get("game_over"):
        board = chess.Board(state["fen"])
        return (
            _make_board_html(
                board,
                flipped=state["flipped"],
                status=_outcome_status(board, state["human_white"]),
            ),
            state,
        )

    board = chess.Board(state["fen"])
    human_white: bool = state["human_white"]
    flipped: bool = state["flipped"]
    human_color = chess.WHITE if human_white else chess.BLACK

    # Ignore clicks when it's not the human's turn
    if board.turn != human_color:
        return gr.update(), state

    selected: int | None = state.get("selected")

    # ── No piece selected yet ──────────────────────────────────────────────────
    if selected is None:
        piece = board.piece_at(sq)
        if piece and piece.color == human_color:
            legal_from = [m for m in board.legal_moves if m.from_square == sq]
            state["selected"] = sq
            state["valid_targets"] = [m.to_square for m in legal_from]
            html = _make_board_html(
                board,
                selected=sq,
                valid_targets=state["valid_targets"],
                flipped=flipped,
                status="Chọn ô đến 🎯",
            )
        else:
            html = _make_board_html(board, flipped=flipped, status="Lượt của bạn 🟢")
        return html, state

    # ── A piece is already selected ────────────────────────────────────────────
    if sq == selected:
        # Deselect
        state["selected"] = None
        state["valid_targets"] = []
        html = _make_board_html(board, flipped=flipped, status="Lượt của bạn 🟢")
        return html, state

    own_piece = board.piece_at(sq)
    if own_piece and own_piece.color == human_color:
        # Re-select a different own piece
        legal_from = [m for m in board.legal_moves if m.from_square == sq]
        state["selected"] = sq
        state["valid_targets"] = [m.to_square for m in legal_from]
        html = _make_board_html(
            board,
            selected=sq,
            valid_targets=state["valid_targets"],
            flipped=flipped,
            status="Chọn ô đến 🎯",
        )
        return html, state

    # Attempt to move selected → sq
    candidates = [
        m for m in board.legal_moves if m.from_square == selected and m.to_square == sq
    ]
    if not candidates:
        # Invalid destination – keep selection
        html = _make_board_html(
            board,
            selected=selected,
            valid_targets=state["valid_targets"],
            flipped=flipped,
            status="❌ Nước đi không hợp lệ!",
        )
        return html, state

    # Auto-promote to queen
    move = next((m for m in candidates if m.promotion == chess.QUEEN), candidates[0])
    board.push(move)
    state["selected"] = None
    state["valid_targets"] = []
    state["fen"] = board.fen()

    if board.is_game_over():
        state["game_over"] = True
        status = _outcome_status(board, human_white)
        html = _make_board_html(board, flipped=flipped, status=status)
        return html, state

    # Engine reply
    engine_mv = _engine_move(board)
    if engine_mv:
        board.push(engine_mv)
        state["fen"] = board.fen()

    # Save position to history for undo (after human + engine have both moved)
    history = list(state.get("history", []))
    history.append(board.fen())
    state["history"] = history

    if board.is_game_over():
        state["game_over"] = True
        status = _outcome_status(board, human_white)
    else:
        status = "Lượt của bạn 🟢"

    html = _make_board_html(board, flipped=flipped, status=status)
    return html, state


def undo_move(state: dict) -> tuple[str, dict]:
    """Undo the last human + engine move pair using the history stack."""
    state = dict(state)  # work on a copy
    flipped = state["flipped"]
    history: list[str] = list(state.get("history", []))

    if len(history) <= 1:
        board = chess.Board(state["fen"])
        html = _make_board_html(
            board, flipped=flipped, status="⚠️ Không có nước nào để đi lại!"
        )
        return html, state

    # Pop the most recent position to go one full turn back
    history.pop()
    prev_fen = history[-1]

    state["fen"] = prev_fen
    state["history"] = history
    state["selected"] = None
    state["valid_targets"] = []
    state["game_over"] = False

    board = chess.Board(prev_fen)
    html = _make_board_html(
        board, flipped=flipped, status="⏪ Đã đi lại. Lượt của bạn 🟢"
    )
    return html, state


# ── Gradio UI ─────────────────────────────────────────────────────────────────
_INITIAL_STATE = _default_state()
_initial_board = _make_board_html(
    chess.Board(),
    flipped=False,
    status="Chọn màu quân rồi bấm '🎮 Ván mới' để bắt đầu!",
)

with gr.Blocks(title="Cờ Vua vs Stockfish", theme=gr.themes.Soft(), css=_CSS, js=_JS) as demo:
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

    board_html = gr.HTML(value=_initial_board, sanitize=False)

    # Hidden textbox – receives square index from JavaScript onclick handlers.
    # elem_id="sq-input" lets the JS in _JS locate it in the DOM.
    sq_input = gr.Textbox(
        value="",
        visible=False,
        elem_id="sq-input",
        label="square",
    )

    # Wire events
    new_game_btn.click(
        fn=start_game,
        inputs=[color_radio, state],
        outputs=[board_html, state],
    )

    sq_input.input(
        fn=handle_click,
        inputs=[sq_input, state],
        outputs=[board_html, state],
    )

    undo_btn.click(
        fn=undo_move,
        inputs=[state],
        outputs=[board_html, state],
    )

if __name__ == "__main__":
    demo.launch()
