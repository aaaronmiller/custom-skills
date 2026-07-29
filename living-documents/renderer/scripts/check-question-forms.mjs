import assert from 'node:assert/strict';
import { parseQuestionSection } from '../public/question-forms.mjs';

const fixture = `---
id: intake
---

# Intake

Context before the questions.

## Questions for the user

Reply with the number and option.

### Question 1: Where should this live?

**A. Existing project. Recommended.** Keeps one authority.

**B. New project.** Creates a separate boundary.

**Write-in:** Name another owner and explain why.

### Question 2: How should it run?

**A. Locally.** Lowest setup cost.

**B. Remotely. Recommended.** Keeps the steering machine responsive.

**C. Both.** Select at launch.

**Write-in:** Describe another topology.
`;

const parsed = parseQuestionSection(fixture);
assert(parsed);
assert.equal(parsed.before, '# Intake\n\nContext before the questions.');
assert.equal(parsed.lead, 'Reply with the number and option.');
assert.equal(parsed.questions.length, 2);
assert.deepEqual(parsed.questions[0].options.map((option) => option.id), ['a', 'b']);
assert.equal(parsed.questions[0].options[0].recommended, true);
assert.equal(parsed.questions[0].writeIn, 'Name another owner and explain why.');
assert.equal(parsed.questions[1].options.length, 3);
assert.equal(parsed.questions[1].options[1].recommended, true);
assert.equal(parseQuestionSection('# No questions here'), null);

console.log('question form parser checks passed');
