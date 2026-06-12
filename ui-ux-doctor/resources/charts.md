# Chart Type Selection Guide

## By Data Relationship
| Data Type | Best Chart | Avoid | Notes |
|-----------|-----------|-------|-------|
| Comparison (few items) | Bar chart (vertical) | Pie chart > 5 slices | Horizontal bars if labels long |
| Comparison (many items) | Horizontal bar | Grouped bars > 4 groups | Sort by value, not alphabetical |
| Trend over time | Line chart | Bar chart for continuous data | Area chart if cumulative matters |
| Part of whole | Donut chart (2-5 parts) | Pie chart > 5 slices | Stacked bar if comparing across groups |
| Distribution | Histogram / Box plot | Bar chart for continuous ranges | Violin plot for detailed shape |
| Correlation | Scatter plot | Line chart (implies causation) | Add trend line if relationship exists |
| Composition over time | Stacked area | Stacked bar > 7 periods | Normalize to 100% if comparing proportions |
| Ranking | Horizontal bar (sorted) | Vertical bar (hard to read labels) | Highlight top/bottom with color |
| Geographic | Choropleth / Bubble map | 3D maps | Ensure colorblind-safe palette |
| Flow/Process | Sankey / Alluvial | Pie charts for flow data | Label key transitions |
| Hierarchy | Treemap | Nested pie charts | Sunburst for drilldown |
| Real-time | Sparkline / Gauge | Full chart for glanceable data | Mini charts for dashboards |
| Budget/Target | Bullet chart | Gauge for precise comparison | Show target, actual, range |

## Accessibility Requirements for All Charts
- Never rely on color alone: use patterns, labels, or direct annotation
- Minimum 3:1 contrast for data elements against background
- Include text alternative (summary or data table) for screen readers
- Interactive charts must be keyboard navigable
- Tooltips should appear on focus, not just hover
- Provide option to view underlying data table

## Common Chart Anti-Patterns
| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| 3D charts | Distorts perception | Always use 2D |
| Dual Y-axis | Misleads correlation | Two separate charts |
| Truncated Y-axis | Exaggerates differences | Start at 0 (or clearly mark) |
| Rainbow palette | Colorblind-hostile | Sequential or diverging palette |
| Over-gridlines | Visual noise | Light, minimal gridlines |
| Missing zero line | Hard to judge magnitude | Include baseline |
| Pie chart > 5 slices | Impossible to compare | Switch to bar chart |
| Animated transitions > 500ms | Feels sluggish | 200-300ms transitions |
