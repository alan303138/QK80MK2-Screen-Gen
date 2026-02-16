import tkinter as tk
import struct

# ── Parse tabml file ──
with open("via_lighting_7_7.tabml", "rb") as f:
    raw = f.read()

magic = raw[:5].decode()
num_frames = raw[5]
fps = raw[6]
rows = raw[7]
cols = raw[8]
payload = raw[32:]  # 32-byte header

frames = []
frame_bytes = rows * cols * 3
for i in range(num_frames):
    chunk = payload[i * frame_bytes : (i + 1) * frame_bytes]
    grid = []
    for p in range(0, len(chunk), 3):
        r, g, b = chunk[p], chunk[p + 1], chunk[p + 2]
        grid.append(g == 0xFF and b == 0xFF)  # RGB: 00 FF FF = on
    frames.append(grid)

# ── GUI ──
CELL = 64          # pixel size per LED
GAP = 6            # gap between LEDs
RADIUS = 10        # corner radius
PAD = 40           # canvas padding

COLOR_ON = "#00FFFF"
COLOR_ON_GLOW = "#005F6F"
COLOR_OFF = "#1a1a1a"
COLOR_BG = "#0d0d0d"

canvas_w = PAD * 2 + cols * CELL + (cols - 1) * GAP
canvas_h = PAD * 2 + rows * CELL + (rows - 1) * GAP

root = tk.Tk()
root.title("QK80 LED Matrix — tabml viewer")
root.configure(bg="#000000")
root.resizable(False, False)

# Info label
info = tk.Label(
    root,
    text=f"{magic}  |  {cols}×{rows}  |  {num_frames} frames  |  {fps} fps  |  #{COLOR_ON.strip('#').upper()}",
    font=("Consolas", 11),
    fg="#666666",
    bg="#000000",
)
info.pack(pady=(10, 0))

canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg=COLOR_BG, highlightthickness=0)
canvas.pack(padx=16, pady=8)

# Frame / letter indicator
letter_label = tk.Label(
    root,
    text="",
    font=("Consolas", 28, "bold"),
    fg=COLOR_ON,
    bg="#000000",
)
letter_label.pack()

frame_label = tk.Label(
    root,
    text="",
    font=("Consolas", 10),
    fg="#444444",
    bg="#000000",
)
frame_label.pack(pady=(0, 12))


def round_rect(cv, x1, y1, x2, y2, r, **kwargs):
    """Draw a rounded rectangle on the canvas."""
    cv.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_rectangle(x1 + r, y1, x2 - r, y2, outline="", **kwargs)
    cv.create_rectangle(x1, y1 + r, x2, y2 - r, outline="", **kwargs)


LETTERS = {0: "A", 1: "L", 2: "A", 3: "N"}
current_frame = [0]


def draw_frame(idx):
    canvas.delete("all")
    grid = frames[idx]
    for r in range(rows):
        for c in range(cols):
            x = PAD + c * (CELL + GAP)
            y = PAD + r * (CELL + GAP)
            on = grid[r * cols + c]
            if on:
                # glow effect
                round_rect(canvas, x - 4, y - 4, x + CELL + 4, y + CELL + 4, RADIUS + 2, fill=COLOR_ON_GLOW)
                round_rect(canvas, x, y, x + CELL, y + CELL, RADIUS, fill=COLOR_ON)
            else:
                round_rect(canvas, x, y, x + CELL, y + CELL, RADIUS, fill=COLOR_OFF)

    letter_label.config(text=LETTERS.get(idx, "?"))
    frame_label.config(text=f"Frame {idx + 1} / {num_frames}")


def animate():
    draw_frame(current_frame[0])
    current_frame[0] = (current_frame[0] + 1) % num_frames
    root.after(1000 // fps, animate)


animate()
root.mainloop()
