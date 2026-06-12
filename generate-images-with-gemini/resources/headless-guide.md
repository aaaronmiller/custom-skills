# Headless Automation Guide

This guide describes how to trigger the Gemini CLI in headless mode to programmatically generate images (using Nano Banana / gemini-3.1-flash).

## Execution Wrapper Script Example

You can trigger image generation programmatically from other scripts. Below is a Python script template that runs the CLI in headless mode and parses the output.

```python
import subprocess
import json
import sys

def generate_image(prompt):
    command = [
        "gemini",
        "-p", f"/generate {prompt}",
        "-o", "json",
        "-y"
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        # Parse the JSON response
        data = json.loads(result.stdout)
        return data
    except subprocess.CalledProcessError as e:
        print(f"Error executing Gemini CLI: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON output: {result.stdout}", file=sys.stderr)
        return None

if __name__ == "__main__":
    prompt = "a retro-futuristic robot painting a canvas"
    response = generate_image(prompt)
    if response:
        print(json.dumps(response, indent=2))
```

## Config Schema Details

The settings JSON (`resources/settings.json`) mirrors the main Antigravity configuration settings found at `/home/cheta/.gemini/settings.json`.

During headless execution, the CLI automatically authenticates via `/home/cheta/.gemini/oauth_creds.json` as it is globally cached. Do not copy the raw access tokens into code repositories, as they expire and present security risks. The CLI reads them natively.
