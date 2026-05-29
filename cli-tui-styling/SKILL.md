---
name: cli-tui-styling
description: "Create visually stunning CLI and TUI applications. Use when: building command-line tools that POP visually, designing terminal user interfaces, adding icons/colors to CLI output, creating tables/borders in terminal, or making tools that don't look like a rainbow vomited on screen."
inputs:
  - name: application_code
    description: CLI/TUI application code to style
    pointer_type: parameter
outputs:
  - name: styled_code
    description: Visually enhanced CLI/TUI code
    pointer_type: output_file
---

# CLI/TUI Styling: Making Your Terminal Apps POP

This skill guides you through creating visually compelling CLI and TUI applications that look professional without being an eyesore.

## When to Use

- Building a new CLI tool from scratch
- Improving existing terminal application visuals
- Adding colors, icons, or animations to command output
- Creating tables, borders, or structured layouts
- Implementing dark/light theme support

---

## Core Principles

### 1. Like Colors = Like Functions

**Semantic Color Mapping:**
```
Errors        → Red (#FF5555, ANSI 196)
Warnings     → Yellow (#F1FA8C, ANSI 226)
Success       → Green (#50FA7B, ANSI 82)
Info/URLs     → Cyan (#8BE9FD, ANSI 87)
Headers       → Bold White (#F8F8F2)
Prompts       → Magenta (#FF79C6, ANSI 212)
```

**Rule:** The same type of information should always use the same color throughout your application.

### 2. Visual Hierarchy

- **Primary**: Bold colors for main actions/headings
- **Secondary**: Muted colors for context
- **Tertiary**: Dim colors for less important info

### 3. Don't Rainbow-Vomit

- Limit to 3-5 main colors
- Use color for meaning, not decoration
- When in doubt, use less color
- Gray is a valid color!

---

## Recommended Libraries

### Quick Framework Intro

| Language | Framework | Best For |
|----------|-----------|----------|
| Go | Bubble Tea | Full TUI apps |
| Go | Lipgloss | Just styling |
| Node | Chalk + Ora | CLI tools |
| Python | Textual | Full TUI apps |
| Rust | Ratatui | Full TUI apps |

### Go
- **Bubble Tea** (charmbracelet): Elm-architecture TUI framework
  - `bubbles` - UI components (spinner, textinput, etc.)
  - `lipgloss` - Declarative styling (like CSS for terminal)
  - `glow` - Terminal markdown renderer
- **bunti** - Progress bars

### Node.js
- **ora** - Elegant spinners
- **chalk** - String styling
- **cli-table3** - Table layouts
- **cli-progress** - Progress bars
- **gradient-string** - Gradient text

### Python
- **textual** - Rich TUI framework (like Bubble Tea for Python)
- **tqdm** - Progress bars
- **halo** - Spinners
- **rich** - Rich terminal output (tables, colors, markdown)
- **blessed** - Full-featured TUI library
- **ratatui** - Terminal user interface
- **yazi** - File manager (great design reference)
- **vivid** - LS_COLORS generator

---

## Fonts & Icons

### Nerd Fonts (Essential)
Download from [nerdfonts.com](https://nerdfonts.com):
- **Hack**, **JetBrains Mono**, **Fira Code** popular choices
- Includes: Font Awesome, Material Design Icons, Octicons
- Enables icons in terminal without emoji fallbacks

### Icon Sets by Category
```
Files        → 󰈔 󰈙 󰗹 󰤸 
Folders     → 󰉋 󰝰 󰝱
Git         → 󰊢 󰊥 󰊣 󰕷
Build       → 󰰹 󰴽 󰏊
Error       → 󰅖 󰷾 󰯻
Success     → 󰄘 󰄵 󰆸
Warning     → 󰀦 󰀪 󰯏
```

---

## Box Drawing Characters

Use Unicode box-drawing for borders and tables:

```
┌───────┐    Single rounded
├───────┤    Single with T
└───────┘    Single corner

╔═══════╗    Double rounded  
║       ║    Double box
╚═══════╝    Double corner

███████    Block elements
```

### Common Characters
```
Horizontal: ─ (U+2500), ═ (U+2550)
Vertical: │ (U+2502), ║ (U+2551)
Corners: ┌ ┐ └ ┘ ╔ ╗ ╚ ╝
T-junctions: ├ ┤ ┼ ╠ ╣ ╦
```

---

## Terminal Capability Detection

Always check terminal capabilities before using advanced features:

```bash
# Check color support
if [[ "$TERM" == *"256"* ]]; then
    # Use 256 colors
elif [[ "$TERM" == *"color"* ]]; then
    # Use 16 colors
else
    # Plain text only
fi

# Check truecolor support
if [[ "$COLORTERM" == *"truecolor"* ]] || [[ "$COLORTERM" == *"24bit"* ]]; then
    # Use RGB colors
fi
```

### Graceful Degradation Order
1. Truecolor (24-bit) - Best colors
2. 256 colors - Good fallback  
3. 16 colors - Standard
4. No colors - Plain text

---

## Color Implementation

### ANSI Escape Codes
```bash
# Basic colors (0-15)
echo -e "\033[31mRed\033[0m"
echo -e "\033[1;32mBold Green\033[0m"

# 256-color (16-231 foreground, 232-255 grayscale)
echo -e "\033[38;5;82mGreen\033[0m"
echo -e "\033[48;5;236mBackground\033[0m"

# Truecolor (24-bit)
echo -e "\033[38;2;255;0;0mmRed RGB\033[0m"
```

### Language-Specific
```go
// Go with lipgloss
style := lipgloss.NewStyle().
    Foreground(lipgloss.Color("212")).
    Bold(true)
```

```javascript
// Node.js with chalk
chalk.red.bold('Error')
chalk.hex('#FF5555')('Custom color')
```

```python
# Python with colorama
from colorama import Fore, Style
print(f"{Fore.RED}Error{Style.RESET_ALL}")
print(f"{Fore.GREEN}Success{Style.RESET_ALL}")

# Python with blessings
from blessings import Terminal
t = Terminal()
print(t.red("Error"))
print(t.green_bold("Success"))
```

```bash
# Shell scripts
echo -e "\033[31mError\033[0m"
```

---

## Progress Indicators

### Best Practices

1. **Spinners** - For unknown duration
2. **Progress Bars (X of Y)** - For known steps
3. **Percentage** - For file operations
4. **Multi-step** - Complex operations

### Libraries by Language
- Go: `bubbles/spinner`, `bunti`
- Node: `ora`, `cli-progress`
- Python: `tqdm`, `halo`

---

## Reference Resources

Load additional resources as needed (progressive disclosure):

- `resources/color-scheme.yaml` - Semantic color mapping template
- `resources/nerd-fonts-guide.md` - Icon reference with codes  
- `resources/box-characters.md` - Border character reference
- `resources/ansi-codes.md` - Complete ANSI code reference
- `resources/cli-design-guides.md` - External design guides

**Tip:** The agent automatically loads these when you mention specific needs like "color codes" or "icons".

---

## Anti-Patterns to Avoid

1. ❌ Every word a different color
2. ❌ Rainbow gradients on text
3. ❌ Blinking text
4. ❌ Too many animated elements
5. ❌ Low contrast text
6. ❌ Assuming all terminals support 256 colors
7. ❌ Ignoring light mode terminals
8. ❌ No screen reader consideration (accessibility)
9. ❌ Using color alone for meaning (add icons/text)

---

## Cross-Reference: ASCII Art

For generating ASCII banners, figlet text, decorative headers, and ASCII logos, use the **`ascii-art`** skill:

```bash
@ascii-art "Create a big banner that says HELLO"
@ascii-art "Make a cow say this message"
```

This skill complements cli-tui-styling for visual decorations.

---

## Testing Checklist

- [ ] Test in iTerm2, Windows Terminal, Alacritty
- [ ] Test with light AND dark backgrounds
- [ ] Test with different fonts (with/without Nerd Fonts)
- [ ] Check contrast ratios for accessibility
- [ ] Test with 256-color terminal (graceful degradation)
- [ ] Test with 8-color terminal (minimum viable)
## 📎 Resources

📎 `~/code/agents/skills/cli-tui-styling/resources/ansi-codes.md`
📎 `~/code/agents/skills/cli-tui-styling/resources/box-characters.md`
📎 `~/code/agents/skills/cli-tui-styling/resources/cli-design-guides.md`
📎 `~/code/agents/skills/cli-tui-styling/resources/color-scheme.yaml`
📎 `~/code/agents/skills/cli-tui-styling/resources/nerd-fonts-guide.md`
