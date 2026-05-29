# Box Drawing Characters Reference

Unicode characters for creating borders, tables, and structured layouts in terminal.

## Single Line (Light)

| Char | Code | Description |
|------|------|-------------|
| ─ | U+2500 | Horizontal light |
| │ | U+2502 | Vertical light |
| ┌ | U+250C | Down and right |
| ┐ | U+2510 | Down and left |
| └ | U+2514 | Up and right |
| ┘ | U+2518 | Up and left |
| ├ | U+251C | Vertical and right |
| ┤ | U+2524 | Vertical and left |
| ┬ | U+252C | Horizontal and down |
| ┴ | U+2534 | Horizontal and up |
| ┼ | U+253C | Cross |

## Double Line

| Char | Code | Description |
|------|------|-------------|
| ═ | U+2550 | Horizontal double |
| ║ | U+2551 | Vertical double |
| ╔ | U+2554 | Down and right |
| ╗ | U+2557 | Down and left |
| ╚ | U+255A | Up and right |
| ╝ | U+255D | Up and left |
| ╠ | U+2560 | Vertical and right |
| ╣ | U+2563 | Vertical and left |
| ╦ | U+2566 | Horizontal and down |
| ╩ | U+2569 | Horizontal and up |
| ╬ | U+256C | Cross double |

## Heavy Line

| Char | Code | Description |
|------|------|-------------|
| ━ | U+2501 | Horizontal heavy |
| ┃ | U+2503 | Vertical heavy |
| ┏ | U+250F | Down and right heavy |
| ┓ | U+2513 | Down and left heavy |
| ┗ | U+251B | Up and right heavy |
| ┛ | U+251F | Up and left heavy |

## Rounded Corners (Soft)

| Char | Code | Description |
|------|------|-------------|
| ╭ | U+256D | Rounded corner down-right |
| ╮ | U+256E | Rounded corner down-left |
| ╯ | U+256F | Rounded corner up-left |
| ╰ | U+2570 | Rounded corner up-right |

## Block Elements (Solid)

| Char | Code | Description |
|------|------|-------------|
| ▀ | U+2580 | Upper half block |
| ▄ | U+2584 | Lower half block |
| █ | U+2588 | Full block |
| ▌ | U+258C | Left half block |
| ▐ | U+2590 | Right half block |
| ░ | U+2591 | Light shade (25%) |
| ▒ | U+2592 | Medium shade (50%) |
| ▓ | U+2593 | Dark shade (75%) |

## Usage Examples

```bash
# Simple box
echo "┌──────────────┐"
echo "│   Hello    │"
echo "└──────────────┘"

# Table with borders
echo "┌─────┬─────┬─────┐"
echo "│ Col1│ Col2│ Col3│"
echo "├─────┼─────┼─────┤"
echo "│ Val │ Val │ Val │"
echo "└─────┴─────┴─────┘"
```

```go
// In Go
const (
    BoxTopLeft     = "\u250C"
    BoxTopRight    = "\u2510"
    BoxBottomLeft = "\u2514"
    BoxBottomRight = "\u2518"
    BoxHorizontal = "\u2500"
    BoxVertical   = "\u2502"
)
```

## Quick Copy Reference

```
Single:    ┌─┐│└─┘├┤┬┴┼
Double:    ╔═╗║╚╝╠╣╦╩
Rounded:   ╭─╮│╰╯
Blocks:    █░▒▓▀▄▌▐
```
