import gradio as gr
import html as html_lib

# ─────────────────────────────────────────────
#  PARSING
# ─────────────────────────────────────────────


def parse_playlist(text):
    """Convert multi-line input into list of song dicts."""
    if not text.strip():
        return []
    songs = []
    for i, line in enumerate(text.strip().split("\n"), 1):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 4:
            raise ValueError(
                f"Line {i} needs exactly 4 values: title, artist, energy, duration.\n"
                f"Got: {line!r}"
            )
        title, artist, energy_s, duration_s = parts
        try:
            energy = int(energy_s)
            duration = float(duration_s)
        except ValueError:
            raise ValueError(
                f"Line {i}: energy must be a whole number (0-100) and duration a number in minutes."
            )
        if not (0 <= energy <= 100):
            raise ValueError(
                f"Line {i}: energy must be between 0 and 100, got {energy}.")
        if duration <= 0:
            raise ValueError(
                f"Line {i}: duration must be a positive number, got {duration}.")
        songs.append({
            "title": title,
            "artist": artist,
            "energy": energy,
            "duration": duration,
            "_id": i - 1   # stable identity for visualisation
        })
    return songs


# ─────────────────────────────────────────────
#  MERGE SORT  (records every comparison step)
# ─────────────────────────────────────────────

def merge_sort_record(songs, key):
    """
    Run merge sort and return (sorted_list, steps).

    Each step is a dict:
      arr            – snapshot of the full array at that moment
      left_range     – (lo, hi) indices of left sub-array (or None)
      right_range    – (lo, hi) indices of right sub-array (or None)
      comparing_ids  – set of _id values currently being compared (or None)
      merged_range   – (lo, hi) of a freshly merged region (or None)
      label          – human-readable description
    """
    arr = [dict(s) for s in songs]
    steps = []

    def snap(arr_state, lr, rr, comparing_ids, merged_range, label):
        steps.append({
            "arr": [dict(s) for s in arr_state],
            "left_range": lr,
            "right_range": rr,
            "comparing_ids": comparing_ids,
            "merged_range": merged_range,
            "label": label,
        })

    def _merge(arr, lo, mid, hi):
        L = [dict(s) for s in arr[lo: mid + 1]]
        R = [dict(s) for s in arr[mid + 1: hi + 1]]

        snap(arr, (lo, mid), (mid + 1, hi), None, None,
             f"📂  Merge  ·  left [{lo}‥{mid}]  |  right [{mid+1}‥{hi}]")

        i = j = 0
        k = lo
        while i < len(L) and j < len(R):
            snap(arr, (lo, mid), (mid + 1, hi),
                 {L[i]["_id"], R[j]["_id"]}, None,
                 f"🔍  Compare  \"{L[i]['title']}\" ({L[i][key]})  vs  \"{R[j]['title']}\" ({R[j][key]})")
            if L[i][key] <= R[j][key]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1
        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1
        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

        snap(arr, None, None, None, (lo, hi),
             f"✅  Merged!  Positions [{lo}‥{hi}] are now sorted  ·  {key} ↑")

    def _sort(arr, lo, hi):
        if lo >= hi:
            return
        mid = (lo + hi) // 2
        snap(arr, (lo, mid), (mid + 1, hi), None, None,
             f"✂️  Split  [{lo}‥{hi}]  →  [{lo}‥{mid}]  &  [{mid+1}‥{hi}]")
        _sort(arr, lo, mid)
        _sort(arr, mid + 1, hi)
        _merge(arr, lo, mid, hi)

    snap(arr, None, None, None, None,
         f"🎵  Start  ·  {len(arr)} songs  ·  sorting by  {key}")
    _sort(arr, 0, len(arr) - 1)
    snap(arr, None, None, None, (0, len(arr) - 1),
         "🎉  Done!  Your playlist is sorted.")
    return arr, steps


# ─────────────────────────────────────────────
#  HTML RENDERERS
# ─────────────────────────────────────────────

_PALETTE = {
    "bg":        "#080e1a",
    "panel":     "#0d1625",
    "border":    "#1a3a5c",
    "unsorted":  "#263354",
    "left":      "#1e6fd9",
    "right":     "#9b4dca",
    "comparing": "#f05a28",
    "merged":    "#27ae60",
    "text":      "#c8d8ea",
    "accent":    "#e94560",
    "dim":       "#556070",
}

LEGEND_ITEMS = [
    (_PALETTE["unsorted"],  "Idle"),
    (_PALETTE["left"],      "Left half"),
    (_PALETTE["right"],     "Right half"),
    (_PALETTE["comparing"], "Comparing"),
    (_PALETTE["merged"],    "Merged ✓"),
]


def _bar_color(i, song, step):
    lr, rr = step["left_range"], step["right_range"]
    mr = step["merged_range"]
    cids = step["comparing_ids"] or set()
    sid = song["_id"]

    if sid in cids:
        return _PALETTE["comparing"], "0 0 14px #f05a28"
    if mr and mr[0] <= i <= mr[1]:
        return _PALETTE["merged"],    "0 0 10px #27ae60"
    if lr and lr[0] <= i <= lr[1]:
        return _PALETTE["left"],      ""
    if rr and rr[0] <= i <= rr[1]:
        return _PALETTE["right"],     ""
    return _PALETTE["unsorted"],      ""


def render_step_html(step, key, total, idx):
    arr = step["arr"]
    if not arr:
        return ""

    max_val = max(s[key] for s in arr) or 1
    progress_pct = int(idx / max(total - 1, 1) * 100)

    # ── bars ──────────────────────────────────
    bars_html = ""
    for i, song in enumerate(arr):
        val = song[key]
        height = max(28, int(val / max_val * 160))
        color, glow = _bar_color(i, song, step)
        glow_css = f"box-shadow:{glow};" if glow else ""
        short = html_lib.escape(
            song["title"][:8] + ("…" if len(song["title"]) > 8 else ""))

        bars_html += f"""
        <div style="
            display:inline-flex;flex-direction:column;align-items:center;
            margin:0 4px;min-width:52px;
        ">
          <span style="font-size:11px;color:{color};font-weight:700;
                       margin-bottom:4px;letter-spacing:0.5px;">{val}</span>
          <div style="
              width:44px;height:{height}px;
              background:{color};{glow_css}
              border-radius:6px 6px 2px 2px;
              transition:height .25s ease,background .2s ease,box-shadow .2s ease;
              position:relative;
          "></div>
          <span style="
              font-size:9px;color:{color};opacity:.8;
              margin-top:5px;text-align:center;
              width:54px;overflow:hidden;white-space:nowrap;
              font-family:'Courier New',monospace;
          ">{short}</span>
        </div>"""

    # ── legend ────────────────────────────────
    legend_html = " &nbsp;&nbsp; ".join(
        f'<span style="color:{c}">◼</span> <span style="color:#9ab">{lbl}</span>'
        for c, lbl in LEGEND_ITEMS
    )

    # ── full card ─────────────────────────────
    return f"""
    <div style="
        background:{_PALETTE['panel']};
        border:1px solid {_PALETTE['border']};
        border-radius:14px;padding:20px;
        font-family:'Courier New',monospace;
    ">
      <!-- header row -->
      <div style="display:flex;justify-content:space-between;
                  align-items:center;margin-bottom:14px;">
        <span style="color:{_PALETTE['accent']};font-size:14px;
                     font-weight:bold;letter-spacing:.5px;">
          {html_lib.escape(step['label'])}
        </span>
        <span style="color:{_PALETTE['dim']};font-size:11px;">
          step {idx + 1} / {total}
        </span>
      </div>

      <!-- progress bar -->
      <div style="background:#111c2e;border-radius:4px;height:5px;margin-bottom:18px;">
        <div style="
            background:linear-gradient(90deg,{_PALETTE['accent']},{_PALETTE['left']});
            height:5px;border-radius:4px;
            width:{progress_pct}%;transition:width .3s ease;
        "></div>
      </div>

      <!-- bars -->
      <div style="
          display:flex;align-items:flex-end;
          height:210px;padding-bottom:6px;
          overflow-x:auto;gap:2px;
      ">
        {bars_html}
      </div>

      <!-- legend -->
      <div style="margin-top:12px;font-size:10px;letter-spacing:.4px;">
        {legend_html}
      </div>
    </div>"""


def render_playlist_table(songs, key):
    if not songs:
        return ""
    rows = "".join(
        f"""<tr style="border-bottom:1px solid #1a3a5c;">
          <td style="padding:8px 14px;color:{_PALETTE['dim']}">{i}</td>
          <td style="padding:8px 14px;color:#ddeeff;font-weight:bold">
              {html_lib.escape(s['title'])}</td>
          <td style="padding:8px 14px;color:{_PALETTE['dim']}">
              {html_lib.escape(s['artist'])}</td>
          <td style="padding:8px 14px;color:{_PALETTE['left']};font-weight:bold">
              {s['energy']}</td>
          <td style="padding:8px 14px;color:{_PALETTE['right']}">
              {s['duration']:.1f} min</td>
        </tr>"""
        for i, s in enumerate(songs, 1)
    )
    return f"""
    <div style="margin-top:18px;">
      <div style="color:{_PALETTE['accent']};font-size:13px;
                  font-weight:bold;margin-bottom:10px;letter-spacing:.5px;">
        🏆  Sorted Playlist  ·  by {key}
      </div>
      <div style="overflow-x:auto;">
        <table style="width:100%;border-collapse:collapse;
                      font-family:'Courier New',monospace;font-size:12px;">
          <thead>
            <tr style="background:#111c2e;color:{_PALETTE['accent']};">
              <th style="padding:10px 14px;text-align:left">#</th>
              <th style="padding:10px 14px;text-align:left">Title</th>
              <th style="padding:10px 14px;text-align:left">Artist</th>
              <th style="padding:10px 14px;text-align:left">Energy</th>
              <th style="padding:10px 14px;text-align:left">Duration</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
    </div>"""


# ─────────────────────────────────────────────
#  PLACEHOLDER HTML
# ─────────────────────────────────────────────

PLACEHOLDER = f"""
<div style="
    background:{_PALETTE['panel']};border:1px solid {_PALETTE['border']};
    border-radius:14px;padding:40px;text-align:center;
    font-family:'Courier New',monospace;
">
  <div style="font-size:40px;margin-bottom:12px;">🎵</div>
  <div style="color:{_PALETTE['dim']};font-size:13px;line-height:1.8;">
    Enter your playlist and press<br>
    <span style="color:{_PALETTE['accent']};font-weight:bold;">▶ Sort Playlist</span>
    to start the step-by-step visualisation.
  </div>
</div>"""


# ─────────────────────────────────────────────
#  GRADIO CALLBACKS
# ─────────────────────────────────────────────

def do_sort(text, key):
    try:
        songs = parse_playlist(text)
        if len(songs) < 2:
            return (
                [], 0, key,
                f"<span style='color:{_PALETTE['accent']}'>⚠ Please enter at least 2 songs.</span>",
                PLACEHOLDER, "",
            )
        sorted_songs, steps = merge_sort_record(songs, key)
        first_vis = render_step_html(steps[0], key, len(steps), 0)
        final_html = render_playlist_table(sorted_songs, key)
        return steps, 0, key, "", first_vis, final_html
    except Exception as exc:
        return (
            [], 0, key,
            f"<span style='color:{_PALETTE['accent']}'>❌ {html_lib.escape(str(exc))}</span>",
            PLACEHOLDER, "",
        )


def go_prev(steps, idx, key):
    if not steps:
        return idx, PLACEHOLDER
    new_idx = max(0, idx - 1)
    return new_idx, render_step_html(steps[new_idx], key, len(steps), new_idx)


def go_next(steps, idx, key):
    if not steps:
        return idx, PLACEHOLDER
    new_idx = min(len(steps) - 1, idx + 1)
    return new_idx, render_step_html(steps[new_idx], key, len(steps), new_idx)


# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────

EXAMPLE_INPUT = """\
Blinding Lights, The Weeknd, 85, 3.2
Someone Like You, Adele, 40, 4.5
Levitating, Dua Lipa, 78, 3.4
Drivers License, Olivia Rodrigo, 35, 4.0
Stay, The Kid LAROI, 90, 2.4
Peaches, Justin Bieber, 62, 3.1
Good 4 U, Olivia Rodrigo, 88, 2.9
Watermelon Sugar, Harry Styles, 55, 2.8"""

CSS = f"""
* {{ box-sizing: border-box; }}
body, .gradio-container {{ background: {_PALETTE['bg']} !important; }}
.gradio-container {{ max-width: 1060px !important; margin: auto !important; }}
.gr-button-primary {{
    background: {_PALETTE['accent']} !important;
    border: none !important; font-weight: 700 !important; letter-spacing: .5px !important;
}}
.gr-button-secondary {{
    background: {_PALETTE['panel']} !important;
    border: 1px solid {_PALETTE['border']} !important;
    color: {_PALETTE['text']} !important; font-weight: 600 !important;
}}
label {{ color: {_PALETTE['dim']} !important; font-family: 'Courier New',monospace !important; }}
textarea, .gr-textbox, input, select {{
    background: {_PALETTE['panel']} !important;
    border: 1px solid {_PALETTE['border']} !important;
    color: {_PALETTE['text']} !important;
    font-family: 'Courier New',monospace !important;
}}
"""

with gr.Blocks(theme=gr.themes.Base(), css=CSS) as demo:

    # ── state ──────────────────────────────────
    steps_state = gr.State([])
    step_idx_state = gr.State(0)
    key_state = gr.State("energy")

    # ── header ─────────────────────────────────
    gr.HTML(f"""
    <div style="text-align:center;padding:28px 0 18px;
                font-family:'Courier New',monospace;">
      <div style="font-size:2.4em;font-weight:900;
                  color:{_PALETTE['accent']};letter-spacing:2px;">
        🎧  PLAYLIST VIBE BUILDER
      </div>
      <div style="color:{_PALETTE['left']};font-size:.9em;margin-top:6px;letter-spacing:1px;">
        MERGE SORT  ·  STEP-BY-STEP VISUALISATION  ·  CISC 121
      </div>
    </div>""")

    with gr.Row(equal_height=False):

        # ── left column: input ──────────────────
        with gr.Column(scale=1, min_width=280):
            gr.HTML(f"""<div style="color:{_PALETTE['dim']};font-size:11px;
                            font-family:'Courier New',monospace;margin-bottom:4px;">
              FORMAT: title, artist, energy (0-100), duration (min)
            </div>""")
            playlist_input = gr.Textbox(
                label="🎶 Playlist Input",
                lines=12,
                value=EXAMPLE_INPUT,
                placeholder="Blinding Lights, The Weeknd, 85, 3.2",
            )
            sort_key = gr.Dropdown(
                choices=["energy", "duration"],
                value="energy",
                label="🎛️  Sort By",
            )
            sort_btn = gr.Button("▶  Sort Playlist!", variant="primary")
            error_box = gr.HTML("")

            gr.HTML(f"""
            <div style="margin-top:14px;padding:12px;
                        background:{_PALETTE['panel']};
                        border:1px solid {_PALETTE['border']};
                        border-radius:10px;
                        font-family:'Courier New',monospace;font-size:11px;
                        color:{_PALETTE['dim']};line-height:1.8;">
              <div style="color:{_PALETTE['text']};font-weight:bold;margin-bottom:4px;">
                🗺️  How to read the chart
              </div>
              <span style="color:{_PALETTE['left']}">◼ Blue</span> = left sub-array<br>
              <span style="color:{_PALETTE['right']}">◼ Purple</span> = right sub-array<br>
              <span style="color:{_PALETTE['comparing']}">◼ Orange</span> = being compared<br>
              <span style="color:{_PALETTE['merged']}">◼ Green</span> = merged &amp; sorted<br>
              <span style="color:{_PALETTE['unsorted']}">◼ Dark</span> = not yet active
            </div>""")

        # ── right column: visualisation ─────────
        with gr.Column(scale=2):
            vis_display = gr.HTML(PLACEHOLDER)

            with gr.Row():
                prev_btn = gr.Button(
                    "◀  Prev Step", variant="secondary", size="sm")
                next_btn = gr.Button(
                    "Next Step  ▶", variant="secondary", size="sm")

            sorted_display = gr.HTML("")

    # ── wiring ─────────────────────────────────
    sort_btn.click(
        do_sort,
        inputs=[playlist_input, sort_key],
        outputs=[steps_state, step_idx_state, key_state,
                 error_box, vis_display, sorted_display],
    )
    prev_btn.click(
        go_prev,
        inputs=[steps_state, step_idx_state, key_state],
        outputs=[step_idx_state, vis_display],
    )
    next_btn.click(
        go_next,
        inputs=[steps_state, step_idx_state, key_state],
        outputs=[step_idx_state, vis_display],
    )

demo.launch()
