---
name: mechanism-forge
description: >-
  Design, implement, evaluate, and refactor diegetic creative mechanisms for
  Culture Foundry: tactile HTML interfaces that behave like instruments,
  workshop devices, consoles, looms, synths, cameras, editing benches, or
  fabrication rigs while preserving complete user control, delegation, locks,
  accessibility, state visibility, and reusable generation contracts. Use when
  creating mechanism components, control grammars, visual design languages,
  medium-specific creative devices, or skills that encode a mechanism for reuse.
---

# Mechanism Forge

Use this skill when a creative workflow must become a playable device rather than a generic form. A mechanism is an instrument, factory, character build, and executable brief at once. Its visual identity matters, but function determines form.

The default mechanism stack may be plain HTML/CSS/JavaScript, Svelte, or another component system requested by the project. Preserve state and generation contracts independently of presentation so the same mechanism can be reskinned across cultures and eras.

## Definition

A mechanism is a bounded interface that combines:

- cultural vocabulary and memory;
- artist or collective traits;
- player-authored variables;
- delegated and randomized variables;
- locks and inheritance rules;
- medium-specific controls;
- material and technology limits;
- references and source artifacts;
- execution adapters;
- cost, progress, and validation feedback;
- provenance for every generated artifact.

A mechanism is not a decorated prompt form. If the wood, brass, screen, or glyph skin is removed, the control grammar must still be coherent.

## Required design sequence

1. Identify the creative decision being made.
2. Identify the variable type: discrete choice, continuum, ordered sequence, relation, route, threshold, reference, lock, or action.
3. Choose a physical or visual control whose affordance matches that variable.
4. Define the state model before styling.
5. Define manual, assisted, delegated, random, inherited, and locked behaviors.
6. Define how the control affects the creative-intent graph.
7. Define visible feedback, reversibility, keyboard operation, and reduced-motion behavior.
8. Place the control according to workflow frequency, consequence, and dependency.
9. Implement the smallest complete mechanism before adding ornament.
10. Validate prediction, accessibility, responsiveness, and generation output.

## Control grammar

Use controls semantically:

- **Wheel or drum:** discrete cyclic options with a visible current item and neighboring possibilities.
- **Detented knob:** bounded discrete values where rotational selection is meaningful.
- **Continuous knob:** scalar intensity, bias, or probability with precise keyboard fallback.
- **Slider or fader:** ordered continuum where relative position should remain visible.
- **Lever:** consequential mode transition or routing change.
- **Toggle:** binary state with persistent on/off indication.
- **Patch cable or route line:** explicit connection between modules.
- **Card, cassette, plate, or socket:** swappable knowledge, memory, style, reference, or artist module.
- **Shutter or door:** reveal advanced controls or mark an execution boundary.
- **Gauge:** observed resource, progress, confidence, or load, not an editable value unless the design clearly combines input and display.
- **Punch strip, step row, or timeline:** ordered sequence.
- **XY pad or field:** two related continuous variables.
- **Button:** immediate action. Labels must state the result.

Do not use a knob for arbitrary text, a gauge for a dropdown, or a lever for a low-consequence preference merely because it looks mechanical.

## Control and delegation states

Every creative variable should support an intentional subset of these modes:

- `manual`: user chooses or writes the value.
- `bank`: user chooses from generated options.
- `artist`: artist agent chooses according to traits and memory.
- `culture`: value is drawn from cultural grammar.
- `reference`: value is derived from a selected artifact.
- `rival`: value is borrowed or transformed from another culture.
- `random-constrained`: selected randomly within explicit constraints.
- `mutation`: inherited value changes within a bounded range.
- `locked`: current value persists across iterations or frames.

Do not reduce this to manual versus random. The project’s authorship model depends on controlled relinquishment.

Locks require visible scope. A lock may persist for one reroll, one sequence, one artist, one mechanism version, one battle, or an entire cultural lineage. The UI must state the scope and allow unlocking without deleting the value.

## Mechanism anatomy

Organize the device into layers:

### Frame

Defines silhouette, material, portability, era, ownership, and cultural manufacture. The frame should leave enough negative space to distinguish modules.

### Primary controls

The few decisions used on almost every generation. They sit within easiest reach and carry the strongest labels.

### Modulation controls

Bias, complexity, density, novelty, emotional contour, variation, and other secondary adjustments. Group them by the primary control they modify.

### Knowledge modules

Vocabularies, symbol sets, stories, palettes, techniques, artist memories, references, and prohibitions. Represent these as swappable objects when possible.

### Execution bay

Provider, model, quality, cost, seed, batch count, and generation action. This area must clearly separate configuration from irreversible or expensive execution.

### Review bay

Candidates, comparisons, council feedback, provenance, rerouting, and selection. A mechanism is incomplete if it generates but cannot learn from results.

### Service view

Advanced settings, provider URLs, API aliases, logs, schemas, and debugging. Hide complexity without making it inaccessible.

## Layout doctrine

Treat layout with the seriousness of a cockpit, bench, or instrument:

- Place high-frequency controls near the dominant hand or primary scan path.
- Separate destructive, expensive, or final actions from exploratory controls.
- Align related controls and use consistent order across mechanisms.
- Keep state visible without opening menus.
- Use shape and position in addition to color.
- Reserve strong accent colors for state, alert, or action hierarchy.
- Make advanced sections discoverable through shutters, drawers, or service panels.
- Preserve a stable spatial grammar across the story and visual mechanisms.

When two mechanisms perform analogous operations, place them analogously. A user who learns “regenerate bank,” “recast category,” “lock variable,” and “execute” in one device should recognize them in another.

## Visual illusion of a real device

The illusion comes from causality:

- controls have depth and consistent lighting;
- moving parts remain aligned with tracks and pivots;
- labels appear manufactured for the device;
- materials meet at believable seams;
- screws, rivets, vents, and wear occur where construction requires them;
- displays sit within bezels;
- shadows and highlights communicate layers;
- motion follows mechanical constraints;
- control state produces corresponding visual and sonic feedback.

Use background textures sparingly. A single panel texture can establish material continuity, but individual components need their own geometry. Avoid a photograph with arbitrary HTML inputs floating on top unless the image was designed as a true control plate with measured anchor points.

Load `references/visual-language.md` for detailed surface, geometry, texture, typography, and motion rules.

## Generated content controls

Word banks, Mad-Lib patterns, style categories, and image instructions require two distinct operations:

- **Reroll selection:** choose different values from the existing bank.
- **Regenerate bank:** call a structured-output model to create a new valid option set from context.

A third operation, **recast category**, changes the category itself and generates a new bank appropriate to it. These must not be conflated.

Bank generation requires a schema. Specify part of speech, semantic role, count, cultural context, exclusions, tone, and relationship to locked variables. Store the resulting bank and provenance. Do not accept unstructured prose and parse it with brittle delimiters when structured output is available.

User-entered values remain valid even when absent from the bank. Editable drum or wheel values may open an inline editor, popover, or service field. Never trap the player inside generated options.

## Cross-medium mechanisms

Separate shared creative intent from medium translation.

Shared intent may include:

- narrative arc;
- subjects and relations;
- emotional contour;
- cultural symbols;
- density curve;
- repetition and rupture;
- audience and occasion;
- lineage references;
- prohibitions.

Image adapters translate into composition, palette, materials, camera, and spatial hierarchy. Music adapters translate into rhythm, pitch, timbre, form, and performance. Video adapters add shots, motion, continuity, and editing. 3D adapters add geometry, scale, topology, materials, and fabrication constraints.

Do not force all media into one universal prompt. Store a medium-independent creative-intent graph and compile it through adapters.

Load `references/generation-contract.md` when implementing provider adapters, structured outputs, intent graphs, or multimodal workflows.

## Artist and culture integration

A mechanism belongs to someone and somewhere. Its defaults can derive from:

- artist habits and unresolved critiques;
- collective roles and routing authority;
- culture-level formal grammar;
- available materials and technology;
- current historical events;
- imported rival influences;
- mechanism wear, defects, and modifications.

Do not hard-code style into presentation only. Cultural rules must affect banks, allowed combinations, control ranges, evaluation, and generated artifacts.

When inheriting a mechanism, preserve version history and identify modified modules. A broken or biased control may become a signature only when the state model represents the bias.

## Cost and execution safety

Before generation, show:

- selected provider and model;
- local or remote route;
- estimated request count;
- approximate cost or compute class;
- output count;
- quality tier;
- references included;
- whether an expensive agent loop is enabled.

The execute control requires an unmistakable ready state. During generation, show progress, cancellation, and partial results. Do not store API keys in browser localStorage. Send requests through a trusted local bridge or secure backend. Mask stored credentials and never return their plaintext value.

## Accessibility

Every mechanism must remain operable without drag-only interaction or visual texture recognition.

- Native inputs or correct ARIA semantics underlie custom controls.
- Keyboard arrows adjust wheels, knobs, sliders, and step values.
- Current values are readable by assistive technology.
- Locks have text labels and state.
- Color is never the only state signal.
- Motion respects reduced-motion settings.
- Hit targets are large enough for touch.
- Focus order follows workflow.
- Popovers and service panels trap focus correctly and close predictably.
- Canvas or WebGL controls have an accessible DOM mirror.

Load `references/accessibility-and-motion.md` for implementation checks.

## Progressive disclosure map

Read supporting files only when the task requires them:

- `references/control-taxonomy.md` for selecting controls and defining value semantics.
- `references/visual-language.md` for physical illusion, materials, component geometry, typography, and skins.
- `references/state-and-locks.md` for state machines, persistence, history, delegation, and locking scopes.
- `references/generation-contract.md` for structured banks, creative-intent graphs, provider adapters, cost, and provenance.
- `references/accessibility-and-motion.md` for keyboard, screen reader, reduced motion, responsive layout, and safe animation.
- `references/evaluation-rubric.md` for testing legibility, tactile coherence, prediction, reuse, and output quality.
- `examples/mechanism-spec.example.json` for a complete machine-readable mechanism definition.
- `scripts/validate-mechanism.mjs` after implementing or changing a mechanism specification.

## Implementation requirements

A reusable mechanism component should expose:

- stable mechanism and component IDs;
- typed state;
- defaults and migrations;
- serialization and restoration;
- undo/redo history;
- lock and delegation scopes;
- bank provenance;
- event or command interface;
- generation compiler output;
- accessibility labels;
- responsive rules;
- visual skin tokens;
- test fixtures.

Prefer pure transformations for state changes and prompt compilation. Keep provider calls outside presentation components. A visual skin must not change semantic state.

## Validation sequence

1. Validate the mechanism specification against its schema or project validator.
2. Test every control with keyboard and pointer.
3. Verify visible state matches serialized state.
4. Lock values, reroll, regenerate banks, and confirm lock scope.
5. Enter a custom value not in a bank and ensure it survives.
6. Test undo and redo across control, bank, and category changes.
7. Test dark and light themes.
8. Test narrow and wide layouts.
9. Test reduced-motion mode.
10. Compile a generation request and inspect every inherited, delegated, and locked value.
11. Confirm cost and provider information before execution.
12. Verify output provenance references the exact mechanism version.

## Completion report

Report:

- mechanism purpose and creative decisions;
- control grammar and layout rationale;
- state, lock, and delegation behavior;
- changed files;
- generated or changed schemas;
- accessibility and responsive checks;
- generation-contract sample;
- validations run;
- remaining risks.

Do not call a mechanism reusable unless it can serialize state, restore state, and compile a provider-independent creative intent.
