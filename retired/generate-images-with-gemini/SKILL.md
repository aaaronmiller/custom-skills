---
name: generate-images-with-gemini
description: ALWAYS invoke when the user asks to generate, edit, or upscale images
  using Gemini CLI, Antigravity CLI, Nano Banana, or gemini-3.1-flash.
version: 1.1.0
author: Antigravity Agent
license: MIT
prerequisites:
  commands:
  - gemini
  - jq
  files:
  - ~/.gemini/oauth_creds.json
  - ~/.gemini/settings.json
metadata:
  tags:
  - image-generation
  - gemini
  - nano-banana
  - headless
  - automation
inputs:
- name: prompt
  description: The text prompt describing the image to generate.
  required: true
  type: string
- name: output_path
  description: Custom local path where the generated image should be moved/saved.
  required: false
  type: string
outputs:
- name: image_path
  description: The file path to the generated image file.
  type: string
tags:
- image
- ai/llm
- automation
grade: B
source: custom
---

# Generate Images with Gemini (Nano Banana)

Automated headless generation, editing, and refinement of images using the Nano Banana image generation capability of `gemini-3.1-flash` via the Gemini/Antigravity CLI.

## Authentication Config

The CLI automatically authenticates using the user's cached OAuth tokens. The active configuration is located at:
- **Settings:** `~/.gemini/settings.json` (configured with `"selectedType": "oauth-personal"`)
- **Credentials:** `~/.gemini/oauth_creds.json`

### Security Warning
Do not hardcode or commit access tokens into source code or settings templates. The `oauth_creds.json` file has local permissions (`0600`) and should remain excluded from version control via `.gitignore`.

## CLI Command Reference

### Slash Commands

| Command | Action | Example |
| :--- | :--- | :--- |
| `/generate` | Render images from prompts | `/generate a sleek sports car` |
| `/edit` | Edit existing assets | `/edit change the car color to blue` |
| `/icon` | Generate UI favicons & icons | `/icon a minimalist gear icon` |
| `/pattern` | Tileable textures and background prints | `/pattern carbon fiber texture` |
| `/restore` | Upscale and clean up blurry outputs | `/restore (applied to selected image)` |

## Headless Execution

To generate images programmatically from pipelines, CLI scripts, or other agents, run:

```bash
gemini -p "/generate <prompt>" -y
```

### Options

| Flag | Description |
| :--- | :--- |
| `-p`, `--prompt` | Non-interactive prompt execution |
| `-o json` | JSON formatted response output |
| `-y`, `--yolo` | Auto-approves command confirmations (crucial for headless scripts) |

### Automation One-Liner (Parsing Output)
Use `jq` to extract the path of the generated image:
```bash
IMAGE_PATH=$(gemini -p "/generate a cute red panda sitting on a tree branch" -y -o json | jq -r '.local_path')
echo "Image generated successfully at: $IMAGE_PATH"
```

## Image Save Paths & Output Behavior

By default, the Nano Banana extension saves generated images relative to the **current working directory (CWD) from which you launched the `gemini` command**:

- **Destination Folder:** `./nanobanana-output/` (created automatically in the launching folder if it doesn't exist).
- **Naming Pattern:** Slugified versions of the prompt (e.g., `"sunset over mountains"` becomes `./nanobanana-output/sunset_over_mountains.png`).

### Customizing Save Locations
If you need images saved directly in another folder (e.g., your project's assets), you can run the command from that folder or copy/move the output from `./nanobanana-output/` using standard shell utilities.

## Examples

### Example A: Basic Generation (Local Workspace)
Running the command from your project directory `/home/cheta/code/my-app/`:
```bash
cd /home/cheta/code/my-app/
gemini -p "/generate a corporate website hero background vector" -y
```
- **Result:** Image saved to `/home/cheta/code/my-app/nanobanana-output/a_corporate_website_hero_background_vector.png`

### Example B: Shell Script Integration
A bash wrapper script (`bin/nanobanana.sh`) is provided in this skill's folder to allow calling it directly:
```bash
./bin/nanobanana.sh "a sci-fi cockpit view" "./dist/assets/hero.png"
```

## Troubleshooting
- **Permission Denied:** Ensure your terminal has read access to `~/.gemini/oauth_creds.json`.
- **Command Hangs:** Nano Banana calls external APIs. Image generation typically takes 5 to 15 seconds. If executing programmatically, verify subprocess timeouts are set to at least 30 seconds.


