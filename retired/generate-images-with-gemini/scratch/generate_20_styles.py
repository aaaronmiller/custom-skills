import subprocess
import json
import re
import os
import sys
import time
import urllib.request

# List of 20 historical styles with prompts
styles = [
    {
        "name": "impressionism",
        "style_desc": "Impressionism (Claude Monet style)",
        "prompt": "Convert this image of the dog into the style of Impressionism, like a Claude Monet oil painting with visible light brushstrokes, dappled outdoor lighting, and vibrant colors, keeping the exact same pose and expression of the dog."
    },
    {
        "name": "cubism",
        "style_desc": "Cubism (Pablo Picasso style)",
        "prompt": "Convert this image of the dog into the style of Analytical Cubism, breaking the scene down into multi-angled geometric facets and earthy tones, keeping the dog's expression and pose recognizable but abstracted."
    },
    {
        "name": "surrealism",
        "style_desc": "Surrealism (Salvador Dali style)",
        "prompt": "Convert this image of the dog into the style of Surrealism, with dreamlike elements, melting clocks or distorted landscape backgrounds, while preserving the dog's pose and expression."
    },
    {
        "name": "art_nouveau",
        "style_desc": "Art Nouveau (Alphonse Mucha style)",
        "prompt": "Convert this image of the dog into the style of Art Nouveau, featuring elegant flowing organic lines, decorative floral borders, and soft pastel colors, keeping the dog's pose and expression."
    },
    {
        "name": "pop_art",
        "style_desc": "Pop Art (Andy Warhol style)",
        "prompt": "Convert this image of the dog into the style of Pop Art, like an Andy Warhol silkscreen print with high contrast, bold outlines, and saturated block colors, preserving the dog's pose and expression."
    },
    {
        "name": "baroque",
        "style_desc": "Baroque (Rembrandt style)",
        "prompt": "Convert this image of the dog into the style of Baroque painting, using Rembrandt's signature chiaroscuro with dramatic high-contrast lighting, deep shadows, and rich warm tones, keeping the dog's pose and expression."
    },
    {
        "name": "expressionism",
        "style_desc": "Expressionism (Edvard Munch style)",
        "prompt": "Convert this image of the dog into the style of Expressionism, like Edvard Munch's paintings, using swirling brushstrokes, intense emotional colors, and distorted backgrounds, keeping the dog's pose and expression."
    },
    {
        "name": "fauvism",
        "style_desc": "Fauvism (Henri Matisse style)",
        "prompt": "Convert this image of the dog into the style of Fauvism, with wild, non-naturalistic vibrant colors, loose painterly brushwork, and simplified shapes, keeping the dog's pose and expression."
    },
    {
        "name": "pointillism",
        "style_desc": "Pointillism (Georges Seurat style)",
        "prompt": "Convert this image of the dog into the style of Pointillism, composed entirely of tiny, distinct dots of pure color that blend visually, keeping the dog's pose and expression."
    },
    {
        "name": "ukiyo_e",
        "style_desc": "Ukiyo-e (Katsushika Hokusai style)",
        "prompt": "Convert this image of the dog into the style of a traditional Japanese Ukiyo-e woodblock print, with bold clean outlines, flat areas of color, and stylized waves or mountain backgrounds, keeping the dog's pose and expression."
    },
    {
        "name": "art_deco",
        "style_desc": "Art Deco (Tamara de Lempicka style)",
        "prompt": "Convert this image of the dog into the style of Art Deco, using bold geometric shapes, sharp metallic lines, and streamlined modern forms, keeping the dog's pose and expression."
    },
    {
        "name": "renaissance",
        "style_desc": "Renaissance (Leonardo da Vinci style)",
        "prompt": "Convert this image of the dog into the style of High Renaissance, like a Leonardo da Vinci oil painting with sfumato blending, classic composition, and warm sepia tones, keeping the dog's pose and expression."
    },
    {
        "name": "romanticism",
        "style_desc": "Romanticism (William Turner style)",
        "prompt": "Convert this image of the dog into the style of Romanticism, with dramatic atmospheric effects, swirling clouds, misty light, and strong emotional intensity, keeping the dog's pose and expression."
    },
    {
        "name": "post_impressionism",
        "style_desc": "Post-Impressionism (Vincent van Gogh style)",
        "prompt": "Convert this image of the dog into the style of Vincent van Gogh, with thick impasto brushstrokes, swirling starry patterns, and intense, vivid colors, keeping the dog's pose and expression."
    },
    {
        "name": "symbolism",
        "style_desc": "Symbolism (Gustav Klimt style)",
        "prompt": "Convert this image of the dog into the style of Gustav Klimt, with decorative gold leaf patterns, intricate mosaic details, and rich ornamental textures, keeping the dog's pose and expression."
    },
    {
        "name": "gothic",
        "style_desc": "Gothic Painting / Medieval Manuscript style",
        "prompt": "Convert this image of the dog into the style of a Medieval Gothic illuminated manuscript, with gilded gold backgrounds, flat perspectives, and ornate decorative margins, keeping the dog's pose and expression."
    },
    {
        "name": "rococo",
        "style_desc": "Rococo (Jean-Honoré Fragonard style)",
        "prompt": "Convert this image of the dog into the style of Rococo, using soft pastel colors, whimsical lighthearted outdoor scenes, and delicate ornamental details, keeping the dog's pose and expression."
    },
    {
        "name": "dadaism",
        "style_desc": "Dadaism (Hannah Höch photomontage style)",
        "prompt": "Convert this image of the dog into the style of Dadaist photomontage, with surreal cut-and-paste elements from newspapers, machinery parts, and textured collages, keeping the dog's pose and expression."
    },
    {
        "name": "pre_raphaelite",
        "style_desc": "Pre-Raphaelite Brotherhood (John Everett Millais style)",
        "prompt": "Convert this image of the dog into the style of Pre-Raphaelite painting, featuring brilliant luminous colors, highly detailed botanical environments, and romantic realism, keeping the dog's pose and expression."
    },
    {
        "name": "neoclassicism",
        "style_desc": "Neo-Classicism (Jacques-Louis David style)",
        "prompt": "Convert this image of the dog into the style of Neoclassicism, with clear drawings, sober colors, shallow space, and a heroic classical theme, keeping the dog's pose and expression."
    }
]

SOURCE_IMAGE = "/mnt/c/Users/Administrator/Pictures/GROK.jpg"
TARGET_DIR = "/mnt/c/Users/Administrator/Pictures"

def download_image(url, dest_path):
    print(f"Downloading from {url} to {dest_path}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("Download complete.")
        return True
    except Exception as e:
        print(f"Failed to download image: {e}")
        return False

def run_style_generation(style):
    style_name = style["name"]
    prompt = style["prompt"]
    output_filename = f"GROK_{style_name}.jpg"
    final_dest = os.path.join(TARGET_DIR, output_filename)
    
    # Skip if already exists
    if os.path.exists(final_dest) and os.path.getsize(final_dest) > 1000:
        print(f"[{style_name.upper()}] Output already exists at {final_dest}. Skipping.")
        return
        
    print(f"\n==========================================")
    print(f"Processing: {style['style_desc']}")
    print(f"==========================================")
    
    # Execute gemini CLI
    cmd = [
        "gemini",
        "-p", f"/edit {SOURCE_IMAGE} \"{prompt}\"",
        "-y",
        "-o", "json"
    ]
    
    try:
        # Run command with 300s timeout and empty workspace in /tmp
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd="/tmp")
        if result.returncode != 0:
            print(f"Error executing gemini CLI for {style_name}: {result.stderr}")
            return
            
        # Parse JSON output
        try:
            data = json.loads(result.stdout)
            response_text = data.get("response", "")
        except json.JSONDecodeError:
            print("Failed to parse stdout as JSON. Raw stdout:")
            print(result.stdout)
            response_text = result.stdout
            
        print("Response received:")
        print(response_text)
        
        # 1. Search for output file in Pictures directory (agent might have saved it there directly)
        # Check standard name variants
        standard_path_pattern = os.path.join(TARGET_DIR, f"GROK_{style_name.upper()}.jpg")
        if os.path.exists(standard_path_pattern) and os.path.getsize(standard_path_pattern) > 1000:
            print(f"Found auto-saved file: {standard_path_pattern}")
            os.rename(standard_path_pattern, final_dest)
            print(f"Renamed and verified at {final_dest}")
            return

        # 2. Extract image URL (e.g. catbox or other storage) from response text
        url_match = re.search(r'MEDIA:(https?://\S+)', response_text)
        if url_match:
            url = url_match.group(1).rstrip(')')
            if download_image(url, final_dest):
                return
                
        # 3. Check for files in local ./nanobanana-output/ directory
        # The prompt slug name is usually used by nanobanana
        # Let's search inside ./nanobanana-output/ for recently modified files
        output_dir = "./nanobanana-output"
        if os.path.exists(output_dir):
            files = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]
            if files:
                # Get the most recently modified file
                latest_file = max(files, key=os.path.getmtime)
                # Check if it was modified in the last 60 seconds
                if time.time() - os.path.getmtime(latest_file) < 60:
                    print(f"Found output file in nanobanana-output: {latest_file}")
                    os.rename(latest_file, final_dest)
                    print(f"Moved to {final_dest}")
                    return

        # 4. Check if any file was written to TARGET_DIR containing GROK and style in name
        for filename in os.listdir(TARGET_DIR):
            if "grok" in filename.lower() and style_name.lower() in filename.lower() and filename != output_filename:
                full_path = os.path.join(TARGET_DIR, filename)
                print(f"Found matching file in Pictures: {full_path}")
                os.rename(full_path, final_dest)
                print(f"Renamed to {final_dest}")
                return

        print(f"Warning: Could not find output file or media URL for {style_name}")
        
    except subprocess.TimeoutExpired:
        print(f"Timeout expired for {style_name} generation.")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Create output dir if needed
    os.makedirs(TARGET_DIR, exist_ok=True)
    
    # Process all styles
    for style in styles:
        run_style_generation(style)
        # Sleep to avoid rate limits (429)
        time.sleep(5)
