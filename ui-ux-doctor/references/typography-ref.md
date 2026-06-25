# Font Pairing Database

## Sans + Sans Pairings
| Heading | Body | Vibe | Best For |
|---------|------|------|----------|
| Inter | Inter | Neutral/Professional | SaaS, Dashboards, Admin |
| Geist | Geist Mono | Developer/Modern | Dev tools, Technical |
| Manrope | Inter | Friendly/Professional | Startups, Products |
| Space Grotesk | DM Sans | Geometric/Clean | Tech, Crypto, AI |
| Plus Jakarta Sans | Inter | Warm/Modern | SaaS, Marketing |
| Satoshi | General Sans | Sharp/Contemporary | Agency, Portfolio |
| Cabinet Grotesk | DM Sans | Bold/Distinctive | Headlines, Landing |
| Outfit | Source Sans 3 | Clean/Versatile | Corporate, Education |

## Serif + Sans Pairings
| Heading | Body | Vibe | Best For |
|---------|------|------|----------|
| Playfair Display | Source Sans 3 | Editorial/Elegant | Media, Publishing |
| Fraunces | Inter | Warm/Sophisticated | Lifestyle, Premium |
| Instrument Serif | Instrument Sans | Unified/Refined | Luxury, Fashion |
| Lora | Nunito | Readable/Warm | Blog, Education |
| DM Serif Display | DM Sans | Modern/Harmonious | Marketing, Brand |
| Crimson Pro | Work Sans | Classic/Professional | Finance, Legal |
| Merriweather | Open Sans | Traditional/Trusted | Government, Healthcare |
| Libre Baskerville | Raleway | Refined/Airy | Editorial, Portfolio |

## Monospace (for code/data contexts)
| Font | Use Case | Pairing With |
|------|----------|-------------|
| JetBrains Mono | Code blocks, IDE | Inter, Geist |
| Fira Code | Ligature-heavy code | Source Sans 3 |
| IBM Plex Mono | Data tables, terminal | IBM Plex Sans |
| Berkeley Mono | Premium code display | Geist, SF Pro |
| Geist Mono | Modern code/data | Geist |

## Type Scale (recommended)
| Level | Size | Weight | Line Height | Use |
|-------|------|--------|-------------|-----|
| Display | 4rem-6rem | 700-900 | 1.1 | Hero headlines only |
| H1 | 2.25rem | 700 | 1.2 | Page titles |
| H2 | 1.5rem | 600 | 1.3 | Section headers |
| H3 | 1.25rem | 600 | 1.4 | Subsections |
| Body | 1rem (16px) | 400 | 1.5-1.6 | Paragraphs |
| Small | 0.875rem | 400 | 1.5 | Captions, metadata |
| Tiny | 0.75rem | 500 | 1.4 | Labels, badges |

## Common Issues and Fixes
| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| Text feels cramped | Line height < 1.4 | Increase to 1.5-1.6 for body |
| Hierarchy unclear | All similar sizes | Enforce 1.25x minimum ratio between levels |
| Headings feel weak | Light weight headings | 600+ for h2/h3, 700+ for h1 |
| Body hard to read | Font too thin at 16px | 400 weight minimum, consider 450 |
| Numbers misaligned | Proportional figures in tables | Enable tabular-nums (font-feature-settings) |
| Font loading flash | FOIT or FOUT | font-display: swap + preload critical fonts |
