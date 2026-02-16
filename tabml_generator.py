"""
QK80 .tabml LED Matrix Animation Generator

Usage:
    python tabml_generator.py

Generates a .tabml file for QK80 7x7 LED dot matrix.
Edit the CONFIG section at the bottom to customize your animation.
"""

import struct
import os

# ── 5x5 Font (centered in 7x7 grid) ──
FONT_5x5 = {
    "A": [
        ".###.",
        "#...#",
        "#####",
        "#...#",
        "#...#",
    ],
    "B": [
        "####.",
        "#...#",
        "####.",
        "#...#",
        "####.",
    ],
    "C": [
        ".####",
        "#....",
        "#....",
        "#....",
        ".####",
    ],
    "D": [
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ],
    "E": [
        "#####",
        "#....",
        "###..",
        "#....",
        "#####",
    ],
    "F": [
        "#####",
        "#....",
        "###..",
        "#....",
        "#....",
    ],
    "G": [
        ".###.",
        "#....",
        "#.###",
        "#...#",
        ".###.",
    ],
    "H": [
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
    ],
    "I": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ],
    "J": [
        "#####",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ],
    "K": [
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
    ],
    "L": [
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ],
    "M": [
        "#...#",
        "##.##",
        "#.#.#",
        "#...#",
        "#...#",
    ],
    "N": [
        "#...#",
        "##..#",
        "#.#.#",
        "#..##",
        "#...#",
    ],
    "O": [
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ],
    "P": [
        "####.",
        "#...#",
        "####.",
        "#....",
        "#....",
    ],
    "Q": [
        ".###.",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ],
    "R": [
        "####.",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
    ],
    "S": [
        ".####",
        "#....",
        ".###.",
        "....#",
        "####.",
    ],
    "T": [
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ],
    "U": [
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ],
    "V": [
        "#...#",
        "#...#",
        ".#.#.",
        ".#.#.",
        "..#..",
    ],
    "W": [
        "#...#",
        "#...#",
        "#.#.#",
        "##.##",
        "#...#",
    ],
    "X": [
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
    ],
    "Y": [
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
    ],
    "Z": [
        "#####",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ],
    "0": [
        ".###.",
        "#..##",
        "#.#.#",
        "##..#",
        ".###.",
    ],
    "1": [
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        ".###.",
    ],
    "2": [
        ".###.",
        "#...#",
        "..##.",
        ".#...",
        "#####",
    ],
    "3": [
        ".###.",
        "#...#",
        "..##.",
        "#...#",
        ".###.",
    ],
    "4": [
        "#..#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ],
    "5": [
        "#####",
        "#....",
        "####.",
        "....#",
        "####.",
    ],
    "6": [
        ".###.",
        "#....",
        "####.",
        "#...#",
        ".###.",
    ],
    "7": [
        "#####",
        "....#",
        "...#.",
        "..#..",
        "..#..",
    ],
    "8": [
        ".###.",
        "#...#",
        ".###.",
        "#...#",
        ".###.",
    ],
    "9": [
        ".###.",
        "#...#",
        ".####",
        "....#",
        ".###.",
    ],
    "!": [
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ],
    "?": [
        ".###.",
        "#...#",
        "..##.",
        ".....",
        "..#..",
    ],
    " ": [
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ],
    ".": [
        ".....",
        ".....",
        ".....",
        ".....",
        "..#..",
    ],
    "-": [
        ".....",
        ".....",
        "#####",
        ".....",
        ".....",
    ],
    "+": [
        ".....",
        "..#..",
        "#####",
        "..#..",
        ".....",
    ],
    "<3": [  # heart
        ".....",
        ".#.#.",
        "#####",
        ".###.",
        "..#..",
    ],
    "*": [  # star
        "..#..",
        ".###.",
        "#####",
        ".###.",
        "..#..",
    ],
    "^": [  # arrow up
        "..#..",
        ".###.",
        "#.#.#",
        "..#..",
        "..#..",
    ],
    ":)": [  # smiley
        ".....",
        ".#.#.",
        ".....",
        "#...#",
        ".###.",
    ],
}


def char_to_grid(char: str) -> list[list[int]]:
    """Convert a character to a 7x7 grid (5x5 font centered with 1px border)."""
    pattern = FONT_5x5.get(char.upper())
    if pattern is None:
        pattern = FONT_5x5["?"]

    grid = [[0] * 7 for _ in range(7)]
    for r, row_str in enumerate(pattern):
        for c, ch in enumerate(row_str):
            grid[r + 1][c + 1] = 1 if ch == "#" else 0
    return grid


def custom_grid(pattern: list[str]) -> list[list[int]]:
    """
    Convert a 7-line string pattern to a 7x7 grid.
    Use '#' for on, '.' or ' ' for off.

    Example:
        custom_grid([
            "..#.#..",
            ".#.#.#.",
            "#.#.#.#",
            ".#.#.#.",
            "#.#.#.#",
            ".#.#.#.",
            "..#.#..",
        ])
    """
    grid = [[0] * 7 for _ in range(7)]
    for r, row_str in enumerate(pattern[:7]):
        for c, ch in enumerate(row_str[:7]):
            grid[r][c] = 1 if ch == "#" else 0
    return grid


def shift_grid(
    grid: list[list[int]],
    up: int = 0,
    down: int = 0,
    left: int = 0,
    right: int = 0,
) -> list[list[int]]:
    """
    Shift a 7x7 grid in any direction. Out-of-bounds pixels are clipped.

    Args:
        up/down/left/right: shift distance in pixels

    Examples:
        shift_grid(char_to_grid("A"), up=1)
        shift_grid(char_to_grid("A"), down=1, left=1)
    """
    dy = down - up
    dx = right - left
    new = [[0] * 7 for _ in range(7)]
    for r in range(7):
        for c in range(7):
            sr, sc = r - dy, c - dx
            if 0 <= sr < 7 and 0 <= sc < 7:
                new[r][c] = grid[sr][sc]
    return new


def parse_color(color: str) -> tuple[int, int, int]:
    """Parse hex color string to (R, G, B) tuple."""
    color = color.lstrip("#")
    return (
        int(color[0:2], 16),
        int(color[2:4], 16),
        int(color[4:6], 16),
    )


def generate_tabml(
    frames: list[list[list[int]]],
    fps: int = 5,
    color: str = "#00FFFF",
    shift: tuple[int, int] = (0, 0),
    output: str = "output.tabml",
):
    """
    Generate a .tabml file.

    Args:
        frames: List of 7x7 grids (each grid is list of 7 rows of 7 ints, 0/1)
        fps:    Frames per second (1-255)
        color:  Hex color string for ON pixels (e.g. "#00FFFF")
        shift:  (row_offset, col_offset) applied to ALL frames.
                Positive = down/right, negative = up/left.
        output: Output file path
    """
    # Apply global shift
    dy, dx = shift
    if dy != 0 or dx != 0:
        shifted = []
        for grid in frames:
            shifted.append(shift_grid(
                grid,
                down=max(dy, 0), up=max(-dy, 0),
                right=max(dx, 0), left=max(-dx, 0),
            ))
        frames = shifted
    r, g, b = parse_color(color)
    num_frames = len(frames)

    # Build file
    buf = bytearray()

    # Header (32 bytes)
    buf.extend(b"tabml")           # magic (5 bytes)
    buf.append(num_frames & 0xFF)  # frame count
    buf.append(fps & 0xFF)         # fps
    buf.append(7)                  # rows
    buf.append(7)                  # cols
    buf.extend(b"\x00" * 23)       # reserved padding

    # Pixel data: each frame = 7x7 pixels x 3 bytes RGB
    for grid in frames:
        for row in range(7):
            for col in range(7):
                if grid[row][col]:
                    buf.extend(bytes([r, g, b]))
                else:
                    buf.extend(bytes([0, 0, 0]))

    with open(output, "wb") as f:
        f.write(buf)

    print(f"Generated: {output}")
    print(f"  Frames: {num_frames}")
    print(f"  FPS:    {fps}")
    print(f"  Color:  #{r:02X}{g:02X}{b:02X}")
    print(f"  Size:   {len(buf)} bytes")
    print()

    # Preview
    for i, grid in enumerate(frames):
        print(f"  Frame {i}:")
        for row in range(7):
            line = "  "
            for col in range(7):
                line += "##" if grid[row][col] else ".."
            print(line)
        print()


def text_to_frames(text: str) -> list[list[list[int]]]:
    """Convert a string to a list of frames (one frame per character)."""
    return [char_to_grid(ch) for ch in text]


def scroll_left(text: str, gap: int = 1) -> list[list[list[int]]]:
    """
    Generate scrolling-left frames (marquee effect, text enters from right).

    Args:
        text: String to scroll
        gap:  Blank columns between characters (default 1)

    Returns:
        List of 7x7 frames for the full scroll cycle.
    """
    # Build a wide strip: 7 rows x N columns
    # Each char is 5 cols wide, with `gap` blank cols between them
    char_patterns = []
    for ch in text:
        p = FONT_5x5.get(ch.upper(), FONT_5x5["?"])
        char_patterns.append(p)

    strip_width = len(char_patterns) * 5 + (len(char_patterns) - 1) * gap
    strip = [[0] * strip_width for _ in range(5)]

    x = 0
    for p in char_patterns:
        for r in range(5):
            for c in range(5):
                strip[r][x + c] = 1 if p[r][c] == "#" else 0
        x += 5 + gap

    # Slide a 5-wide window across the strip, centered in 7x7
    # Window goes from fully off-screen-right to fully off-screen-left
    frames = []
    for offset in range(-5, strip_width + 1):
        grid = [[0] * 7 for _ in range(7)]
        for r in range(5):
            for c in range(5):
                src_col = offset + c
                if 0 <= src_col < strip_width:
                    grid[r + 1][c + 1] = strip[r][src_col]
        frames.append(grid)

    return frames


def scroll_right(text: str, gap: int = 1) -> list[list[list[int]]]:
    """Generate scrolling-right frames (text enters from left)."""
    return list(reversed(scroll_left(text, gap)))


def scroll_up(text: str, gap: int = 1) -> list[list[list[int]]]:
    """
    Generate scrolling-up frames (text enters from bottom).

    Args:
        text: String to scroll
        gap:  Blank rows between characters (default 1)
    """
    char_patterns = []
    for ch in text:
        p = FONT_5x5.get(ch.upper(), FONT_5x5["?"])
        char_patterns.append(p)

    strip_height = len(char_patterns) * 5 + (len(char_patterns) - 1) * gap
    strip = [[0] * 5 for _ in range(strip_height)]

    y = 0
    for p in char_patterns:
        for r in range(5):
            for c in range(5):
                strip[y + r][c] = 1 if p[r][c] == "#" else 0
        y += 5 + gap

    frames = []
    for offset in range(-5, strip_height + 1):
        grid = [[0] * 7 for _ in range(7)]
        for r in range(5):
            for c in range(5):
                src_row = offset + r
                if 0 <= src_row < strip_height:
                    grid[r + 1][c + 1] = strip[src_row][c]
        frames.append(grid)

    return frames


def scroll_down(text: str, gap: int = 1) -> list[list[list[int]]]:
    """Generate scrolling-down frames (text enters from top)."""
    return list(reversed(scroll_up(text, gap)))


# ════════════════════════════════════════════════
#  CLI
# ════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    MODES = {
        "static":       "原地切換（每字一幀）",
        "scroll_left":  "← 從右往左滾動",
        "scroll_right": "→ 從左往右滾動",
        "scroll_up":    "↑ 從下往上滾動",
        "scroll_down":  "↓ 從上往下滾動",
    }

    parser = argparse.ArgumentParser(
        description="QK80 .tabml LED Matrix Animation Generator",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("text", nargs="?", help="要顯示的文字 (A-Z 0-9 ! ? . - +)")
    parser.add_argument("-m", "--mode", choices=MODES.keys(), help="動畫模式")
    parser.add_argument("-f", "--fps", type=int, help="每秒幀數 (預設: static=5, scroll=10)")
    parser.add_argument("-c", "--color", default="#00FFFF", help="LED 顏色 (預設: #00FFFF)")
    parser.add_argument("-g", "--gap", type=int, default=1, help="字母間距 (預設: 1)")
    parser.add_argument("-o", "--output", help="輸出檔名 (預設: output.tabml)")

    args = parser.parse_args()

    # Interactive mode if no arguments
    if args.text is None:
        print("╔══════════════════════════════════════╗")
        print("║  QK80 LED Matrix Animation Generator ║")
        print("╚══════════════════════════════════════╝")
        print()
        print("可用字元: A-Z 0-9 ! ? . - + <3(愛心) *(星星) :)(笑臉)")
        print()
        args.text = input("輸入文字: ").strip()
        if not args.text:
            print("未輸入文字，結束。")
            exit()

    if args.mode is None:
        print()
        print("動畫模式:")
        for i, (key, desc) in enumerate(MODES.items(), 1):
            print(f"  {i}. {key:14s} {desc}")
        print()
        choice = input("選擇模式 (1-5, 預設 1): ").strip()
        mode_keys = list(MODES.keys())
        if choice in ("", "1"):
            args.mode = "static"
        elif choice in ("2", "3", "4", "5"):
            args.mode = mode_keys[int(choice) - 1]
        else:
            args.mode = choice if choice in MODES else "static"

    if args.fps is None:
        default_fps = 5 if args.mode == "static" else 10
        fps_input = input(f"FPS (預設 {default_fps}): ").strip()
        args.fps = int(fps_input) if fps_input else default_fps

    if args.output is None:
        default_name = "output.tabml"
        out_input = input(f"輸出檔名 (預設 {default_name}): ").strip()
        args.output = out_input if out_input else default_name

    # Generate frames
    if args.mode == "static":
        frames = text_to_frames(args.text)
    elif args.mode == "scroll_left":
        frames = scroll_left(args.text, gap=args.gap)
    elif args.mode == "scroll_right":
        frames = scroll_right(args.text, gap=args.gap)
    elif args.mode == "scroll_up":
        frames = scroll_up(args.text, gap=args.gap)
    elif args.mode == "scroll_down":
        frames = scroll_down(args.text, gap=args.gap)

    generate_tabml(
        frames=frames,
        fps=args.fps,
        color=args.color,
        output=args.output,
    )
