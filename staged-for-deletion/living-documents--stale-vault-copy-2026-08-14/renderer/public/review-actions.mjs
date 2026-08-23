export const darkThemes = new Set(['obsidian', 'graphite', 'high-contrast']);

export function resolveQuickTheme({ theme, prefersDark = false, lastDark = 'obsidian' }) {
  const effectiveDark = theme === 'system' ? prefersDark : darkThemes.has(theme);
  return effectiveDark ? 'paper' : (darkThemes.has(lastDark) ? lastDark : 'obsidian');
}

export function annotationDialogConfig(scope, { targetTitle = 'Current page', quote = '' } = {}) {
  const layout = scope === 'layout';
  return {
    scope: layout ? 'layout' : 'content',
    title: layout ? 'Suggest a reader layout change' : 'Add a content note',
    eyebrow: layout ? 'Reader layout · local note' : 'Document content · local note',
    target: layout ? `Reader layout · ${targetTitle}` : targetTitle,
    fieldLabel: layout ? 'Describe the layout or behavior change' : 'Your note',
    help: layout
      ? 'Describe placement, styling, navigation, or reader behavior. This does not edit renderer source.'
      : 'Attach context, a question, an objection, a decision, or evidence. This does not edit canonical Markdown.',
    submitLabel: layout ? 'Save layout note' : 'Save content note',
    quote: layout ? '' : quote.trim(),
    showQuote: !layout && Boolean(quote.trim()),
    showMarkdownDraft: !layout,
  };
}
