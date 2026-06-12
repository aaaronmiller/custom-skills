# UX Anti-Pattern Database

## Navigation (NAV)
NAV-01: Hidden navigation behind hamburger on desktop. Fix: Expose top-level items.
NAV-02: No breadcrumbs in deep hierarchy. Fix: Add breadcrumb trail.
NAV-03: Active state indistinguishable from default. Fix: Bold + color + indicator.
NAV-04: Dropdown menus disappear on diagonal mouse movement. Fix: Add hover delay/buffer zone.
NAV-05: Mobile nav covers full screen with no close button. Fix: Visible close + backdrop tap.
NAV-06: Footer-only navigation for critical paths. Fix: Duplicate in header/sidebar.

## Forms (FORM)
FORM-01: Placeholder text as only label. Fix: Persistent label above input.
FORM-02: Validation only on submit. Fix: Inline validation on blur.
FORM-03: Error messages far from source field. Fix: Inline below the field.
FORM-04: Required fields unmarked. Fix: Asterisk with legend or mark optional instead.
FORM-05: Password requirements shown only after failure. Fix: Show requirements upfront.
FORM-06: Auto-advancing multi-field inputs (phone, SSN). Fix: Single field with formatting.
FORM-07: Select dropdowns for < 5 options. Fix: Radio buttons.
FORM-08: No confirmation on destructive actions. Fix: Confirmation modal with consequence description.
FORM-09: Calendar picker for known dates (birthday). Fix: Three dropdowns or typed input.
FORM-10: Disabled submit with no explanation. Fix: Enable + validate on click, or tooltip.

## Layout (LAYOUT)
LAYOUT-01: Content touching viewport edges on mobile. Fix: Min 16px side padding.
LAYOUT-02: Single-column layout exceeding 80ch line length. Fix: max-width constraint.
LAYOUT-03: Cards with inconsistent heights in grid. Fix: Uniform height or masonry.
LAYOUT-04: Sticky header consuming >15% viewport. Fix: Reduce or collapse on scroll.
LAYOUT-05: Z-index warfare (values > 100). Fix: Defined z-index scale (1-10).
LAYOUT-06: Absolutely positioned elements breaking on zoom. Fix: Relative/flex layout.
LAYOUT-07: Horizontal scroll on any viewport width. Fix: overflow-x hidden + responsive check.

## Typography (TYPE)
TYPE-01: Body text below 14px. Fix: Minimum 16px for body content.
TYPE-02: Line height below 1.4 for paragraphs. Fix: 1.5-1.6 for body text.
TYPE-03: More than 2 font families loaded. Fix: Max 2 families, vary by weight.
TYPE-04: All-caps body text exceeding one line. Fix: Reserve caps for short labels.
TYPE-05: Justified text on narrow columns. Fix: Left-align below 40ch width.
TYPE-06: Low contrast text (below 4.5:1 for normal, 3:1 for large). Fix: Meet WCAG AA.

## Color (COLOR)
COLOR-01: Red/green as only state differentiator. Fix: Add icon + text label.
COLOR-02: Branded link color matching body text. Fix: Distinct color + underline.
COLOR-03: Background patterns reducing text readability. Fix: Solid overlay or remove.
COLOR-04: Inconsistent hover colors across components. Fix: Single hover color variable.
COLOR-05: Dark mode as simple color inversion. Fix: Purpose-built dark palette.
COLOR-06: More than 5 accent colors competing. Fix: 1 primary + 1 accent + neutrals.

## Interaction (INTERACT)
INTERACT-01: Click targets below 44x44px on touch. Fix: Minimum 44px tap target.
INTERACT-02: No loading indicator for async actions. Fix: Spinner/skeleton/progress.
INTERACT-03: Double-click required (non-desktop paradigm). Fix: Single-click actions.
INTERACT-04: Hover-only information (tooltips as primary content). Fix: Visible by default.
INTERACT-05: Infinite scroll with no way to reach footer. Fix: Load-more button or paginate.
INTERACT-06: Auto-playing media without user consent. Fix: Paused by default.
INTERACT-07: Modal dialogs for non-critical information. Fix: Inline expansion or toast.
INTERACT-08: Swipe gestures as only action method. Fix: Visible button alternative.
INTERACT-09: Animations exceeding 300ms. Fix: 150-250ms for most transitions.
INTERACT-10: No undo for destructive actions. Fix: Soft delete with undo toast.

## Feedback (FEEDBACK)
FEEDBACK-01: Silent failures (action appears to do nothing). Fix: Always show outcome.
FEEDBACK-02: Success messages that auto-dismiss too fast (<3s). Fix: 5s minimum or manual.
FEEDBACK-03: Error messages using technical language. Fix: Human-readable with fix suggestion.
FEEDBACK-04: Toast notifications stacking/overlapping. Fix: Queue with max 3 visible.
FEEDBACK-05: No empty state messaging. Fix: Helpful prompt with primary action CTA.
FEEDBACK-06: Loading state indistinguishable from empty state. Fix: Skeleton vs "no data".

## Content (CONTENT)
CONTENT-01: Wall of text without scannable structure. Fix: Headings + short paragraphs.
CONTENT-02: Jargon without definition on first use. Fix: Tooltip or inline explanation.
CONTENT-03: Dates in ambiguous format (01/02/03). Fix: "Jan 2, 2003" unambiguous format.
CONTENT-04: Numbers without formatting (1000000). Fix: Locale-aware formatting (1,000,000).
CONTENT-05: Truncated text with no way to see full content. Fix: Expand or tooltip.
CONTENT-06: Marketing copy in error messages. Fix: Direct, actionable language.

## Performance (PERF)
PERF-01: Layout shift during load (CLS > 0.1). Fix: Reserve dimensions for async content.
PERF-02: Unoptimized images (>500KB per image). Fix: WebP/AVIF + responsive srcset.
PERF-03: Blocking third-party scripts in head. Fix: async/defer or load after interaction.
PERF-04: Custom fonts causing FOIT. Fix: font-display: swap or optional.
PERF-05: No code splitting (entire app loaded upfront). Fix: Route-based lazy loading.
PERF-06: Excessive DOM nodes (>1500). Fix: Virtualize long lists, simplify structure.

## Accessibility (A11Y)
A11Y-01: Missing alt text on informational images. Fix: Descriptive alt text.
A11Y-02: Decorative images with non-empty alt. Fix: alt="" or role="presentation".
A11Y-03: Focus trap in modals not implemented. Fix: Trap focus, restore on close.
A11Y-04: Skip-to-content link missing. Fix: First focusable element, visible on focus.
A11Y-05: ARIA roles misused or redundant. Fix: Use semantic HTML first, ARIA as supplement.
A11Y-06: Dynamic content changes unannounced. Fix: aria-live regions for updates.
A11Y-07: Custom controls missing keyboard support. Fix: Enter/Space to activate, Escape to close.
A11Y-08: Contrast failing on disabled elements. Fix: 3:1 minimum even for disabled.
A11Y-09: Motion with no reduced-motion support. Fix: @media (prefers-reduced-motion: reduce).
A11Y-10: Tab order doesn't follow visual order. Fix: DOM order matches visual layout.

## Mobile (MOBILE)
MOBILE-01: Desktop layout crammed into mobile. Fix: Redesign for mobile-first.
MOBILE-02: Fixed elements covering input fields. Fix: Scroll into view on focus.
MOBILE-03: Hover-dependent interactions on touch. Fix: Tap-first interaction model.
MOBILE-04: Tiny close buttons on modals/banners. Fix: 44px minimum tap target.
MOBILE-05: Pinch-to-zoom disabled. Fix: Remove maximum-scale from viewport meta.

## Data Display (DATA)
DATA-01: Tables not responsive on mobile. Fix: Card layout or horizontal scroll.
DATA-02: Numbers not right-aligned in columns. Fix: Right-align for comparison.
DATA-03: No sort indicators on sortable columns. Fix: Visible arrow indicators.
DATA-04: Pagination with no item count. Fix: "Showing 1-20 of 347 results".
DATA-05: Charts without legend or axis labels. Fix: Always label axes and data series.
DATA-06: Color-only chart differentiation. Fix: Patterns, labels, or direct annotation.

## Search (SEARCH)
SEARCH-01: No search suggestions or autocomplete. Fix: Suggest as user types.
SEARCH-02: Search results with no relevance indication. Fix: Highlight matched terms.
SEARCH-03: No results page without suggestions. Fix: "Did you mean..." + alternatives.
SEARCH-04: Search not accessible via keyboard shortcut. Fix: Cmd/Ctrl+K convention.

## Onboarding (ONBOARD)
ONBOARD-01: Forced tutorial that can't be skipped. Fix: Skippable + accessible later.
ONBOARD-02: Too many steps before value delivery. Fix: Reduce to 3 steps max.
ONBOARD-03: Feature tour pointing to elements not yet visible. Fix: Contextual, in-flow tips.
ONBOARD-04: No progress indicator in multi-step flows. Fix: Step counter or progress bar.

## Trust (TRUST)
TRUST-01: No visible security indicators on checkout. Fix: SSL badge, trust marks.
TRUST-02: Hidden pricing (revealed only after signup). Fix: Transparent pricing page.
TRUST-03: Dark patterns in unsubscribe flows. Fix: Single-click unsubscribe.
TRUST-04: Cookie consent covering critical content. Fix: Compact, non-blocking banner.
TRUST-05: No privacy policy link near data collection. Fix: Link adjacent to forms.
