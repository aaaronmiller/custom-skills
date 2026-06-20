# ANSI Escape Codes Reference

Complete reference for terminal color and control codes.

## Color Codes

### Standard 16 Colors (0-15)

| Code | Color | RGB | Hex |
|------|-------|-----|-----|
| 0 | Black | 0,0,0 | #000000 |
| 1 | Red | 204,0,0 | #CC0000 |
| 2 | Green | 0,204,0 | #00CC00 |
| 3 | Yellow | 204,204,0 | #CCCC00 |
| 4 | Blue | 0,0,204 | #0000CC |
| 5 | Magenta | 204,0,204 | #CC00CC |
| 6 | Cyan | 0,204,204 | #00CCCC |
| 7 | White | 204,204,204 | #CCCCCC |
| 8 | Bright Black | 128,128,128 | #808080 |
| 9 | Bright Red | 255,0,0 | #FF0000 |
| 10 | Bright Green | 0,255,0 | #00FF00 |
| 11 | Bright Yellow | 255,255,0 | #FFFF00 |
| 12 | Bright Blue | 0,0,255 | #0000FF |
| 13 | Bright Magenta | 255,0,255 | #FF00FF |
| 14 | Bright Cyan | 0,255,255 | #00FFFF |
| 15 | Bright White | 255,255,255 | #FFFFFF |

### 256-Color Mode

```bash
# Syntax: \033[38;5;Nm (foreground) or \033[48;5;Nm (background)
# Where N is 0-255

# 256-color palette ranges:
# 0-15:   Standard colors
# 16-231: 6x6x6 color cube (216 colors)
# 232-255: Grayscale (24 levels)
```

### Truecolor (24-bit)

```bash
# Syntax: \033[38;2;R;G;Bm (foreground)
#         \033[48;2;R;G;Bm (background)

# Example: Bright red
echo -e "\033[38;2;255;0;0mRed\033[0m"
```

## Text Formatting

| Code | Effect |
|------|--------|
| 0 | Reset |
| 1 | Bold |
| 2 | Dim |
| 3 | Italic |
| 4 | Underline |
| 5 | Slow blink |
| 7 | Reverse |
| 8 | Hidden |
| 9 | Strikethrough |

### Combined Formatting
```bash
# Bold + Underline + Red
echo -e "\033[1;4;31mBold Red Underlined\033[0m"
```

## Cursor Control

| Code | Action |
|------|--------|
| \033[nA | Move up n lines |
| \033[nB | Move down n lines |
| \033[nC | Move forward n cols |
| \033[nD | Move backward n cols |
| \033[H | Move to home (0,0) |
| \033[y;xH | Move to y,x |

## Screen Clearing

| Code | Action |
|------|--------|
| \033[2J | Clear screen |
| \033[H | Move to home after clear |
| \033[K | Clear line |
| \033[0K | Clear to end of line |
| \033[1K | Clear to beginning |
| \033[2K | Clear entire line |

## Common Combinations

```bash
# Progress indicator
echo -ne "\033[100C Working...\033[0m"

# Colored output
echo -e "\033[32mSuccess\033[0m \033[31mFailed\033[0m"

# Progress bar
echo -ne "\r\033[KProgress: [#####     ] 50%"

# Clear and redraw
echo -ne "\033[2J\033[H"
```

## Language Implementation

### Go
```go
const (
    Reset   = "\033[0m"
    Red     = "\033[31m"
    Green   = "\033[32m"
    Yellow  = "\033[33m"
    Blue    = "\033[34m"
    Purple  = "\033[35m"
    Cyan    = "\033[36m"
    Gray    = "\033[37m"
    Bold    = "\033[1m"
    Dim     = "\033[2m"
    Underline = "\033[4m"
)
```

### Node.js
```javascript
const reset = '\x1b[0m';
const red = '\x1b[31m';
const green = '\x1b[32m';
const bold = '\x1b[1m';
```

### Python
```python
RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
BOLD = '\033[1m'
```

## Best Practices

1. Always end with reset code
2. Check terminal capabilities before truecolor
3. Provide fallback for 8-color terminals
4. Use variables for repeated codes
5. Consider lipgloss/chalk for abstraction
