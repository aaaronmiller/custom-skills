# Spoken Format Guide (Jon Stewart / TTS)

## Satirical News Script (The Daily Show Style)
1.  **Structure:**
    *   **ANCHOR TOSS:** The Anchor introduces a serious news topic and throws to the Correspondent in an absurd location or context.
    *   **CORRESPONDENT SOT (Sound on Tape) / LIVE:** The Correspondent reports, immediately undermining the seriousness with a visual gag or oblivious statement.
    *   **THE INTERVIEW (Optional):** The Correspondent interviews an "expert" by playing the fool, letting the expert hang themselves with their own logic.
    *   **THE MOMENT OF ZEN:** Ends the script. A brief, unedited clip of a public figure contradicting themselves or doing something bizarrely mundane, presented without comment.
2.  **Format:** Use standard multi-camera sitcom or news script formatting. Clearly label speakers, SFX, and Camera Angles.

**Format Example:**
```xml
<daily_show_script>
  <segment type="anchor_desk">
    [ANCHOR]: (Deadpan) The world is on fire. Literally. But fear not, we sent someone with a bucket. 
  </segment>
  <segment type="field_report">
    [CORRESPONDENT]: (Standing in a desert holding a thimble) Thanks, Jon. I'm doing my part.
  </segment>
</daily_show_script>
```

## TTS Audio Comedy Prompts
1.  **Pacing with Punctuation:** 
    *   Use em-dashes (`—`) to force the TTS system to cut off abruptly (perfect for sudden realizations or interruptions).
    *   Use ellipses (`...`) to create agonizingly long, pregnant pauses before the punchline.
2.  **Tone:** Write explicitly for a monotone, deadpan, robotic delivery. The humor derives from the contrast between the emotionless voice and the ridiculous content.
3.  **SSML Tags:** If the LLM generates the audio prompt, include suggestions for SSML (Speech Synthesis Markup Language) tags (e.g., `<prosody rate="slow">`) to guarantee the pacing.

**Format Example:**
```xml
<tts_prompt>
<speak>
  I have calculated the probability of your survival. <break time="2s"/> It is... <prosody pitch="high">hilariously low.</prosody> Have a nice —
</speak>
</tts_prompt>
```
