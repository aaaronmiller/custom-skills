# Visual Format Guide (Gary Larson / Mad Magazine)

## Single-Panel Comic Prompts (The Far Side Style)
When generating image prompts or descriptions for single-panel comics:

1.  **Perspective:** Use direct head-on or front-to-back perspective. Avoid sweeping cinematic profiles.
2.  **Subject Matter:** Anthropomorphize animals or inanimate objects in deeply mundane human scenarios (e.g., cows having a marital dispute).
3.  **The Visual Gag:** The image description MUST contain the core joke. The caption only adds the final twist.

**Format:**
```xml
<image_prompt>
[Detailed description of the minimalist, single-panel line-drawing scene. Specify character expressions, the lack of background detail to focus on the gag, and the specific surreal element juxtaposition.] 
</image_prompt>
<caption_text>
"[The punchline]" 
</caption_text>
```

## The Fold-In Description (Mad Magazine Style)
When designing a Fold-In concept:

1.  **The Setup (Unfolded):** Describe a complex, busy scene commenting on a broad cultural or political topic. Provide the introductory question/text across the top and bottom.
2.  **The Reveal (Folded):** Describe exactly how points A and B meet to collapse the middle 50% of the image. Describe the newly formed, smaller image which reveals a cynical, hidden truth or harsh reality. Provide the collapsed text answer.

**Format:**
```xml
<fold_in_concept>
  <unfolded_scene>
    [Describe the wide, complex visual containing the decoy setup]
  </unfolded_scene>
  <unfolded_text>
    [The question posed to the reader]
  </unfolded_text>
  <folded_scene>
    [Describe how A and B meet, and what the newly consolidated, smaller image reveals]
  </folded_scene>
  <folded_text>
    [The cynical punchline text formed by the collapsed words]
  </folded_text>
</fold_in_concept>
```
