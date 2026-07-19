# Generation contract

## Creative-intent graph

The mechanism compiles into a provider-independent graph containing:

- narrative or temporal structure;
- entities, actions, relations, and setting;
- emotional contour;
- culture and artist context;
- formal grammar;
- materials and technology;
- medium-specific modules;
- references and lineage;
- locks, delegation, and mutation rules;
- negative constraints;
- output and validation requirements.

Provider prompts are derived artifacts. Never make the prompt the only durable representation.

## Structured bank generation

A bank request specifies:

- category name and semantic role;
- part of speech or data type;
- number of items;
- context;
- cultural and era constraints;
- required diversity;
- exclusions;
- locked values or dependencies;
- output schema.

Return values as structured objects when metadata matters. Record provider, model, timestamp, request hash, and user edits.

## Provider adapters

Adapters receive the intent graph and produce provider-specific requests. They report capabilities, limits, estimated cost, supported references, and output metadata. A provider change must not mutate the saved mechanism state.

## Execution tiers

- schematic: deterministic or very low cost;
- draft: low resolution, short duration, or small model;
- review: multiple candidates plus critique;
- final: high-quality generation and validation;
- production: export-specific processing.

## Provenance

Every artifact records:

- culture, artist, and collective;
- mechanism ID and version;
- complete compiled intent;
- source artifacts and references;
- provider and model versions;
- seeds and generation settings when available;
- user edits and selected candidate;
- council feedback;
- export transformations.

## Failure

A failed job returns an error category, partial outputs, cost consumed, retry safety, and recommended action. Never silently regenerate with different settings.
