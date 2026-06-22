# Written Format Guide (The Onion / National Lampoon)

## Satirical News Articles (The Onion Style)
1.  **The Headline:** This is 90% of the joke. Use the "Ski Jump" structure: place the comedic impact at the very end of the sentence. State the uncomfortable truth plainly ("Include the Elephant").
2.  **The Form:** Write in strict, sterile Associated Press (AP) journalistic style. The drier and more objective the tone, the funnier the absurdity.
3.  **Structure:**
    *   **Headline:** The core joke.
    *   **Dateline:** [CITY, STATE] — 
    *   **Lede:** Expand the headline with exactly one new absurd detail.
    *   **Body:** Introduce quotes from a fictitious "everyman" character (The Honest Character) who speaks their terrible, selfish inner thoughts out loud as if it were perfectly normal and acceptable to society.

**Format Example:**
```xml
<satirical_article>
  <headline>Nation's Wealthiest 1% Shocked To Discover Money Can’t Buy Happiness, Decide To Just Keep Buying Things Anyway</headline>
  <dateline>NEW YORK —</dateline>
  <body>
    [AP Style body text with deadpan quotes from an oblivious billionaire]
  </body>
</satirical_article>
```

## Long-Form Parody (National Lampoon Style)
1.  **The Target:** Identify the exact publication or cultural artifact being parodied (e.g., a high school yearbook, a corporate memo, a 1950s lifestyle magazine).
2.  **The Tone:** Arrogant, deeply cynical, and assuming the worst of human nature. Blend high culture vocabulary with low culture depravity.
3.  **Execution:** Mimic the target's formatting perfectly (subheadings, pull-quotes, font-styles if applicable). The humor comes from the dark juxtaposition of the pristine format and the aggressively offensive or absurd content.

**Format Requirements:**
Always heavily utilize layout markers if recreating a magazine print.
```xml
<parody_document target_style="[e.g., Target Corporate Memo]">
  <header>...</header>
  <body>...</body>
</parody_document>
```
