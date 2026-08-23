/* Parse the canonical Living Documents question convention without a Markdown dependency. */

function normalize(value = '') {
  return String(value).replaceAll('\r\n', '\n').replace(/\s+/g, ' ').trim();
}

function stripInlineMarkdown(value = '') {
  return normalize(value)
    .replace(/^\*\*|\*\*$/g, '')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\*([^*]+)\*/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

export function parseQuestionSection(markdown = '') {
  const body = String(markdown).replace(/^---\s*\n[\s\S]*?\n---\s*\n?/, '').trim();
  const marker = body.match(/^## Questions for the user\s*$/m);
  if (!marker || marker.index === undefined) return null;

  const before = body.slice(0, marker.index).trim();
  const questionBody = body.slice(marker.index + marker[0].length).trim();
  const headings = [...questionBody.matchAll(/^### Question (\d+):\s*(.+)$/gm)];
  if (!headings.length) return null;

  const lead = questionBody.slice(0, headings[0].index).trim();
  const questions = headings.map((heading, index) => {
    const start = heading.index + heading[0].length;
    const end = headings[index + 1]?.index ?? questionBody.length;
    const block = questionBody.slice(start, end).trim();
    const chunks = block.split(/\n\s*\n/).map((chunk) => chunk.trim()).filter(Boolean);
    const options = [];
    let writeIn = '';

    for (const chunk of chunks) {
      const option = chunk.match(/^\*\*([A-Z])\.\s+([\s\S]*?)\*\*\s*([\s\S]*)$/);
      if (option) {
        const label = stripInlineMarkdown(option[2]);
        const detail = stripInlineMarkdown(option[3]);
        options.push({
          id: option[1].toLowerCase(),
          label,
          detail,
          recommended: /\brecommended\b/i.test(`${label} ${detail}`),
        });
        continue;
      }
      const custom = chunk.match(/^\*\*Write-in:\*\*\s*([\s\S]*)$/i);
      if (custom) writeIn = stripInlineMarkdown(custom[1]);
    }

    return {
      id: `question-${heading[1]}`,
      number: Number(heading[1]),
      title: stripInlineMarkdown(heading[2]),
      options,
      writeIn,
    };
  }).filter((question) => question.options.length >= 2);

  return questions.length ? { before, lead, questions } : null;
}
