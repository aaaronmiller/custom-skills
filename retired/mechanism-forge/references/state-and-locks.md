# State, history, delegation, and locks

## State layers

Separate:

- definition: component types, ranges, labels, and dependencies;
- current state: values, selections, locks, and routing;
- generated banks: options and provenance;
- artist/culture context: defaults and constraints;
- execution state: provider, queue, cost, progress, errors;
- history: reversible commands;
- artifact lineage: compiled intent and outputs.

## Command model

Represent user actions as commands where practical:

- set value;
- edit custom value;
- reroll selection;
- regenerate bank;
- recast category;
- lock/unlock;
- change lock scope;
- delegate/reclaim;
- connect/disconnect;
- add/remove module;
- apply critique;
- execute generation.

Commands make undo, replay, testing, worklogs, and multiplayer synchronization easier.

## Locks

A lock record should contain:

- target component or variable;
- locked value;
- scope;
- owner;
- created time or mechanism version;
- optional reason;
- whether dependent values are also frozen.

Lock scopes may be `iteration`, `sequence`, `artist`, `mechanism`, `battle`, or `culture`. A visual lock without scope is ambiguous.

## Delegation

Delegation assigns authority, not randomness. Store the delegate type and policy. An artist delegate may use traits and memories; a culture delegate uses formal grammar; a random delegate uses a constrained distribution.

Allow the player to inspect the chosen value and the reason when available. Reclaiming authority should preserve the current value unless the player resets it.

## Persistence

Serialize the mechanism definition version and state version. Provide migrations. Store custom user values, generated bank provenance, locks, routes, and module identities. Do not store secrets in mechanism state.

## History

Undo should restore bank contents and lock states, not only visible selections. Expensive generation actions may create checkpoints rather than being fully reversible. Artifact deletion requires confirmation and provenance handling.
