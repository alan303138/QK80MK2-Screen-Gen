# QK80MK2 Screen Gen

QK80 MK2 鍵盤 7x7 LED 點陣螢幕動畫產生器。
產生 `.tabml` 檔後，到 [QK80 MK2 Configurator](https://cfg.qwertykeys.com/) 匯入即可使用。

## Quick Start

```bash
python tabml_generator.py
```

互動模式會依序詢問文字、動畫模式、FPS、輸出檔名。

## CLI 用法

```bash
python tabml_generator.py <文字> -m <模式> [選項]
```

### 參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `text` | 要顯示的文字 | (互動輸入) |
| `-m, --mode` | 動畫模式 (見下方) | (互動選擇) |
| `-f, --fps` | 每秒幀數 | static: 5, scroll: 10 |
| `-c, --color` | LED 顏色 (hex) | `#00FFFF` |
| `-g, --gap` | 字母間距 (px) | 1 |
| `-o, --output` | 輸出檔名 | `output.tabml` |

### 動畫模式

| 模式 | 說明 |
|------|------|
| `static` | 原地切換（每字一幀） |
| `scroll_left` | ← 文字從右往左滾動 |
| `scroll_right` | → 文字從左往右滾動 |
| `scroll_up` | ↑ 文字從下往上滾動 |
| `scroll_down` | ↓ 文字從上往下滾動 |

### 範例

```bash
# 原地切換顯示 ALAN
python tabml_generator.py "ALAN" -m static -f 5 -o alan.tabml

# HELLO 從右往左跑馬燈
python tabml_generator.py "HELLO" -m scroll_left -f 10 -o hello.tabml

# 紅色、間距 2 的右滾
python tabml_generator.py "QK80" -m scroll_right -f 8 -c "#FF0000" -g 2 -o qk80.tabml

# 上滾
python tabml_generator.py "HI" -m scroll_up -f 8 -o hi.tabml
```

## 可用字元

```
A-Z  0-9  !  ?  .  -  +  (空格)
<3 (愛心)  * (星星)  :) (笑臉)  ^ (箭頭)
```

## Python API

也可以在 Python 中 import 使用：

```python
from tabml_generator import *

# 文字轉幀
generate_tabml(frames=text_to_frames("ALAN"), fps=5, output="alan.tabml")

# 捲動動畫
generate_tabml(frames=scroll_left("ALAN"), fps=10, output="scroll.tabml")

# 自訂 7x7 圖案
generate_tabml(
    frames=[
        custom_grid([
            "..###..",
            ".#...#.",
            "#.....#",
            "#.....#",
            "#.....#",
            ".#...#.",
            "..###..",
        ]),
    ],
    fps=5,
    color="#00FF00",
    output="circle.tabml",
)

# 位移
shift_grid(char_to_grid("A"), up=1, left=1)
```

## 預覽工具

```bash
python visualize.py
```

用 tkinter 視覺化播放 `via_lighting_7_7.tabml` 的動畫內容。

## .tabml 檔案格式

| 偏移 | 大小 | 說明 |
|------|------|------|
| 0x00 | 5 bytes | Magic `tabml` |
| 0x05 | 1 byte | Frame 數量 |
| 0x06 | 1 byte | FPS |
| 0x07 | 1 byte | Rows (7) |
| 0x08 | 1 byte | Cols (7) |
| 0x09 | 23 bytes | Reserved (0x00) |
| 0x20 | N bytes | Pixel data: frames x 7 x 7 x 3 (RGB) |

每個 pixel 3 bytes (R, G, B)，亮 = 指定顏色，滅 = `000000`。
