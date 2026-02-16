import tkinter as tk
import argparse
import sys
import os

# ── CLI ──
parser = argparse.ArgumentParser(description="QK80 .tabml LED Matrix Viewer")
parser.add_argument("file", nargs="?", help=".tabml 檔案路徑")
args = parser.parse_args()

if args.file is None:
    # Find .tabml files in current directory
    tabml_files = sorted(f for f in os.listdir(".") if f.endswith(".tabml"))
    if not tabml_files:
        print("找不到 .tabml 檔案")
        sys.exit(1)
    if len(tabml_files) == 1:
        args.file = tabml_files[0]
    else:
        print("可用的 .tabml 檔案:")
        for i, f in enumerate(tabml_files, 1):
            print(f"  {i}. {f}")
        choice = input(f"選擇 (1-{len(tabml_files)}): ").strip()
        try:
            args.file = tabml_files[int(choice) - 1]
        except (ValueError, IndexError):
            print("無效選擇")
            sys.exit(1)

print(f"Opening: {args.file}")

# ── Parse tabml file ──
with open(args.file, "rb") as f:
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
        grid.append(g == 0xFF and b == 0xFF)
    frames.append(grid)

# Detect LED color from first ON pixel
COLOR_ON = "#00FFFF"
for i in range(num_frames):
    chunk = payload[i * frame_bytes : (i + 1) * frame_bytes]
    for p in range(0, len(chunk), 3):
        r, g, b = chunk[p], chunk[p + 1], chunk[p + 2]
        if r or g or b:
            COLOR_ON = f"#{r:02X}{g:02X}{b:02X}"
            break
    else:
        continue
    break

# ── GUI ──
CELL = 64
GAP = 6
RADIUS = 10
PAD = 40

# Derive glow color (dim version of LED color)
cr = int(COLOR_ON[1:3], 16)
cg = int(COLOR_ON[3:5], 16)
cb = int(COLOR_ON[5:7], 16)
COLOR_ON_GLOW = f"#{cr//4:02X}{cg//4:02X}{cb//4:02X}"
COLOR_OFF = "#1a1a1a"
COLOR_BG = "#0d0d0d"

canvas_w = PAD * 2 + cols * CELL + (cols - 1) * GAP
canvas_h = PAD * 2 + rows * CELL + (rows - 1) * GAP

root = tk.Tk()
root.title(f"QK80 LED Matrix — {os.path.basename(args.file)}")
root.configure(bg="#000000")
root.resizable(False, False)

info = tk.Label(
    root,
    text=f"{os.path.basename(args.file)}  |  {cols}x{rows}  |  {num_frames} frames  |  {fps} fps  |  {COLOR_ON}",
    font=("Consolas", 11),
    fg="#666666",
    bg="#000000",
)
info.pack(pady=(10, 0))

canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg=COLOR_BG, highlightthickness=0)
canvas.pack(padx=16, pady=8)

frame_label = tk.Label(
    root,
    text="",
    font=("Consolas", 10),
    fg="#444444",
    bg="#000000",
)
frame_label.pack(pady=(0, 12))


def round_rect(cv, x1, y1, x2, y2, r, **kwargs):
    cv.create_arc(x1, y1, x1 + 2 * r, y1 + 2 * r, start=90, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_arc(x2 - 2 * r, y1, x2, y1 + 2 * r, start=0, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_arc(x2 - 2 * r, y2 - 2 * r, x2, y2, start=270, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_arc(x1, y2 - 2 * r, x1 + 2 * r, y2, start=180, extent=90, style="pieslice", outline="", **kwargs)
    cv.create_rectangle(x1 + r, y1, x2 - r, y2, outline="", **kwargs)
    cv.create_rectangle(x1, y1 + r, x2, y2 - r, outline="", **kwargs)


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
                round_rect(canvas, x - 4, y - 4, x + CELL + 4, y + CELL + 4, RADIUS + 2, fill=COLOR_ON_GLOW)
                round_rect(canvas, x, y, x + CELL, y + CELL, RADIUS, fill=COLOR_ON)
            else:
                round_rect(canvas, x, y, x + CELL, y + CELL, RADIUS, fill=COLOR_OFF)

    frame_label.config(text=f"Frame {idx + 1} / {num_frames}")


def animate():
    draw_frame(current_frame[0])
    current_frame[0] = (current_frame[0] + 1) % num_frames
    root.after(1000 // fps, animate)


animate()
root.mainloop()
