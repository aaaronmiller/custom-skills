# Accessibility and motion

## Custom controls

Use native inputs when possible. When a visual knob wraps a range input, keep the input focusable and synchronized. Provide an accessible name, current value, minimum, maximum, and step.

Keyboard expectations:

- arrows: small adjustment;
- Page Up/Down: larger adjustment;
- Home/End: minimum/maximum;
- Enter/Space: activate buttons and toggles;
- Escape: close popovers and service panels;
- Tab: follows workflow order.

## Visual states

Indicate state through at least two channels: position plus label, shape plus color, lamp plus text, or pattern plus border. Maintain contrast in dark and light themes.

## Motion

Under reduced motion:

- replace spinning gears with static ready/progress states;
- shorten shutters and drawers to near-instant transitions;
- avoid parallax and oscillation;
- preserve causal feedback through text, lamps, and progress bars.

Do not animate controls merely because they can move. Motion should show manipulation, processing, routing, or state change.

## Touch and responsive layout

Hit targets should be approximately 44 CSS pixels where possible. On narrow screens, preserve control grouping and labels. Reflow modules vertically rather than shrinking knobs below usability. Provide a compact service view for dense settings.

## Canvas and WebGL

If a mechanism uses canvas or WebGL, maintain a parallel accessible control tree in the DOM. The visual scene cannot be the only interface.
