# Workflow Patterns

## Sequential Workflows

For complex tasks, break operations into clear, sequential steps. It is often helpful to give Claude an overview of the process towards the beginning of SKILL.md:

```markdown
For example, filling a PDF form with a script such as `example-form-fill.py` involves these steps:

1. Analyze the form (for example, with `example-analyze-form.py`)
2. Create field mapping (edit fields.json)
3. Validate mapping (for example, with `example-validate-fields.py`)
4. Fill the form (for example, with `example-fill-form.py`)
5. Verify output (for example, with `example-verify-output.py`)
```

## Conditional Workflows

For tasks with branching logic, guide Claude through decision points:

```markdown
1. Determine the modification type:
   **Creating new content?** → Follow "Creation workflow" below
   **Editing existing content?** → Follow "Editing workflow" below

2. Creation workflow: [steps]
3. Editing workflow: [steps]
```