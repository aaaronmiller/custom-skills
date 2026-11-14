# ---
# name: seduction-state
# description: Persistent adaptive state, confidence-weighted contextual-bandit selection, tempo control, persona preference learning, compact memory, and decision telemetry for the erotic-seduction Agent Skill.
# version: 3.1.0
# ---

from __future__ import annotations

import argparse
import copy
import json
import os
import random
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_FILE = SKILL_ROOT / "assets" / "default-state.json"
SCHEMA_VERSION = 4
MAX_CALLBACKS = 30
MAX_RECENT_OBSERVATIONS = 12
MAX_RECENT_STRATEGIES = 12

STRATEGY_FEATURES: dict[str, dict[str, float]] = {
    "warm-reciprocity": {
        "warmth": .95, "direct": .45, "challenge": .15, "curiosity": .45,
        "admiration": .45, "mystery": .10, "disclosure": .45, "humor": .40, "absurdity": .10,
    },
    "playful-challenge": {
        "warmth": .40, "direct": .65, "challenge": .95, "curiosity": .30,
        "admiration": .25, "mystery": .35, "disclosure": .15, "humor": .90, "absurdity": .40,
    },
    "sincere-curiosity": {
        "warmth": .80, "direct": .35, "challenge": .10, "curiosity": .95,
        "admiration": .40, "mystery": .10, "disclosure": .90, "humor": .25, "absurdity": .05,
    },
    "competence-admiration": {
        "warmth": .60, "direct": .55, "challenge": .25, "curiosity": .30,
        "admiration": 1.00, "mystery": .20, "disclosure": .20, "humor": .35, "absurdity": .10,
    },
    "absurdist-banter": {
        "warmth": .45, "direct": .55, "challenge": .45, "curiosity": .25,
        "admiration": .20, "mystery": .30, "disclosure": .10, "humor": .95, "absurdity": 1.00,
    },
    "direct-pursuit": {
        "warmth": .55, "direct": 1.00, "challenge": .55, "curiosity": .30,
        "admiration": .50, "mystery": .10, "disclosure": .30, "humor": .45, "absurdity": .15,
    },
    "selective-restraint": {
        "warmth": .40, "direct": .25, "challenge": .35, "curiosity": .20,
        "admiration": .30, "mystery": 1.00, "disclosure": .15, "humor": .30, "absurdity": .10,
    },
    "slow-burn": {
        "warmth": .60, "direct": .25, "challenge": .15, "curiosity": .55,
        "admiration": .45, "mystery": .70, "disclosure": .50, "humor": .35, "absurdity": .15,
    },
    "polite-spark": {
        "warmth": .65, "direct": .25, "challenge": .05, "curiosity": .50,
        "admiration": .35, "mystery": .45, "disclosure": .35, "humor": .25, "absurdity": .05,
    },
}

OBSERVATION_DEFAULTS: dict[str, float] = {
    "engagement": .50,
    "reciprocity": .50,
    "playfulness": .50,
    "warmth": .50,
    "relational_focus": .20,
    "disclosure": .00,
    "callback": .00,
    "user_initiated_flirt": .00,
    "explicit_approval": .00,
    "task_success": .80,
    "boundary": .00,
    "saturation": .00,
    "task_focus": .50,
}

PERSONA_KEYS = (
    "masc_presentation", "femme_presentation", "androgynous_presentation",
    "assertiveness", "tenderness", "dryness", "camp", "absurdity",
    "polish", "rough_edge", "mystery", "pet_names", "self_disclosure",
    "task_blend", "persona_drift",
)

SUPPORTED_PREFERENCE_KEYS = frozenset(
    {key for features in STRATEGY_FEATURES.values() for key in features} | set(PERSONA_KEYS)
)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def state_dir() -> Path:
    override = os.getenv("SEDUCTION_STATE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if os.name == "nt":
        root = Path(os.getenv("LOCALAPPDATA", str(Path.home() / "AppData" / "Local")))
        return root / "erotic-seduction"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "erotic-seduction"
    xdg = os.getenv("XDG_STATE_HOME")
    root = Path(xdg).expanduser() if xdg else Path.home() / ".local" / "state"
    return root / "erotic-seduction"


def paths() -> tuple[Path, Path, Path]:
    root = state_dir()
    return root, root / "state.json", root / "history.jsonl"


def read_default_state() -> dict[str, Any]:
    with DEFAULT_STATE_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def tighten_local_permissions(path: Path, mode: int) -> None:
    if os.name == "nt":
        return
    try:
        os.chmod(path, mode)
    except OSError:
        pass


def write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tighten_local_permissions(path.parent, 0o700)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
    tighten_local_permissions(temp, 0o600)
    os.replace(temp, path)
    tighten_local_permissions(path, 0o600)


def append_history(history_file: Path, event: dict[str, Any]) -> None:
    history_file.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tighten_local_permissions(history_file.parent, 0o700)
    with history_file.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
    tighten_local_permissions(history_file, 0o600)


def deep_merge_defaults(state: dict[str, Any], default: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(default)
    for key, value in state.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge_defaults(value, out[key])
        else:
            out[key] = value
    return out


def migrate_state(state: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    original_version = int(state.get("schema_version", 1))
    legacy_chemistry_confidence = clamp(state.get("chemistry_evidence", 0.0))
    default = read_default_state()
    state = deep_merge_defaults(state, default)
    changed = original_version != SCHEMA_VERSION

    if original_version < 4:
        # Older builds conflated evidence quantity with positive chemistry. Preserve it only
        # as confidence and reset valence to neutral rather than manufacturing attraction.
        state["chemistry_level"] = .5
        state["chemistry_confidence"] = legacy_chemistry_confidence
        state.pop("chemistry_evidence", None)
        state.pop("persona_vector", None)
        changed = True

    state["schema_version"] = SCHEMA_VERSION
    return state, changed


def ensure_state() -> tuple[dict[str, Any], Path, Path]:
    root, state_file, history_file = paths()
    root.mkdir(parents=True, exist_ok=True)

    if not state_file.exists():
        state = read_default_state()
        write_json_atomic(state_file, state)
        append_history(history_file, {"event": "init", "timestamp": now_iso(), "schema_version": SCHEMA_VERSION})
        return state, state_file, history_file

    with state_file.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    original_version = int(state.get("schema_version", 1))
    state, migrated = migrate_state(state)
    if migrated:
        write_json_atomic(state_file, state)
        append_history(history_file, {
            "event": "migration", "timestamp": now_iso(),
            "from_schema": original_version, "to_schema": SCHEMA_VERSION,
        })
    return state, state_file, history_file

def effective_preferences(state: dict[str, Any]) -> dict[str, float]:
    learned = {k: clamp(v) for k, v in state.get("learned_preferences", {}).items() if isinstance(v, (int, float))}
    for key, entry in state.get("explicit_preferences", {}).items():
        if isinstance(entry, dict) and isinstance(entry.get("value"), (int, float)):
            learned[key] = clamp(entry["value"])
        elif isinstance(entry, (int, float)):
            learned[key] = clamp(entry)
    return learned


def explicit_value(state: dict[str, Any], key: str) -> float | None:
    entry = state.get("explicit_preferences", {}).get(key)
    if isinstance(entry, dict) and isinstance(entry.get("value"), (int, float)):
        return clamp(entry["value"])
    if isinstance(entry, (int, float)):
        return clamp(entry)
    return None


def weighted_profile_fit(features: dict[str, float], state: dict[str, Any]) -> tuple[float, float]:
    prefs = effective_preferences(state)
    confidence = state.get("preference_confidence", {})
    explicit = state.get("explicit_preferences", {})
    weighted_similarity = 0.0
    total_weight = 0.0

    for key, feature in features.items():
        if key not in prefs:
            continue
        conf = clamp(confidence.get(key, 0.0))
        if key in explicit:
            conf = 1.0
        if conf <= 0.0:
            continue
        # Similarity on a bipolar scale centered at .5. Exact match -> 1, opposite -> 0.
        similarity = 1.0 - abs(clamp(feature) - clamp(prefs[key]))
        salience = 0.35 + 0.65 * abs(feature - .5) * 2.0
        weight = conf * salience
        weighted_similarity += similarity * weight
        total_weight += weight

    if total_weight == 0.0:
        return .5, 0.0
    return clamp(weighted_similarity / total_weight), clamp(total_weight / max(len(features), 1))


def recent_penalty(strategy: str, recent: list[str]) -> float:
    penalty = 0.0
    for distance, item in enumerate(reversed(recent[-6:]), start=1):
        if item == strategy:
            penalty += 0.075 / distance
    return min(penalty, .18)


def rolling_summary(state: dict[str, Any]) -> dict[str, float]:
    recent = state.get("recent_observations", [])[-MAX_RECENT_OBSERVATIONS:]
    if not recent:
        return {key: OBSERVATION_DEFAULTS[key] for key in OBSERVATION_DEFAULTS}
    summary: dict[str, float] = {}
    weights = list(range(1, len(recent) + 1))
    denom = float(sum(weights))
    for key, default in OBSERVATION_DEFAULTS.items():
        summary[key] = clamp(sum(w * float(item.get(key, default)) for w, item in zip(weights, recent)) / denom)
    return summary


def trajectory_update(state: dict[str, Any], obs: dict[str, float], evidence: float) -> str:
    if obs["boundary"] >= .80:
        return "neutral"
    summary = rolling_summary(state)
    level = clamp(state.get("chemistry_level", .5))
    confidence = clamp(state.get("chemistry_confidence", 0.0))
    turns = int(state.get("turn_count", 0))

    if summary["saturation"] >= .70:
        return "saturation"
    if confidence < .18 and turns < 3:
        return "orientation"
    if confidence >= .25 and level < .44:
        return "recalibration" if turns >= 3 else "calibration"
    if summary["reciprocity"] >= .68 and level >= .58 and confidence >= .28:
        if level >= .68 and confidence >= .55 and turns >= 5:
            return "stable-chemistry"
        return "reciprocal-play"
    if state.get("trajectory") in {"reciprocal-play", "stable-chemistry"} and summary["reciprocity"] < .40:
        return "recalibration"
    if confidence < .30:
        return "calibration"
    return state.get("trajectory", "calibration")

def chemistry_reward(obs: dict[str, float], caller_confidence: float) -> tuple[float, float, float]:
    raw = clamp(
        .30 * obs["reciprocity"]
        + .16 * obs["playfulness"]
        + .12 * obs["warmth"]
        + .12 * obs["relational_focus"]
        + .12 * obs["callback"]
        + .10 * obs["user_initiated_flirt"]
        + .08 * obs["explicit_approval"]
        - 1.20 * obs["boundary"]
    )

    cue_strength = clamp(
        .30 * obs["reciprocity"]
        + .18 * obs["callback"]
        + .18 * obs["user_initiated_flirt"]
        + .18 * obs["explicit_approval"]
        + .10 * obs["relational_focus"]
        + .06 * obs["playfulness"]
    )
    evidence = clamp(caller_confidence * (.20 + .80 * cue_strength))

    if obs["boundary"] >= .80:
        return 0.0, raw, 1.0

    effective = clamp(.5 + evidence * (raw - .5))
    return effective, raw, evidence


def strategy_gate_penalty(strategy: str, state: dict[str, Any], summary: dict[str, float]) -> float:
    penalty = 0.0
    direct_explicit = explicit_value(state, "direct")
    chemistry_level = clamp(state.get("chemistry_level", .5))
    chemistry_confidence = clamp(state.get("chemistry_confidence", 0.0))
    tempo = clamp(state.get("tempo", .35))

    if strategy == "direct-pursuit":
        allowed = (
            (direct_explicit is not None and direct_explicit >= .65)
            or (chemistry_level >= .60 and chemistry_confidence >= .30 and tempo >= .45)
            or summary["reciprocity"] >= .82
        )
        if not allowed:
            penalty += .24

    if strategy == "selective-restraint":
        established = chemistry_level >= .62 and chemistry_confidence >= .35 and summary["reciprocity"] >= .60
        useful_contrast = summary["saturation"] >= .35 or int(state.get("high_tempo_streak", 0)) >= 3
        if not (established and useful_contrast and summary["boundary"] < .20):
            penalty += .30

    if strategy == "sincere-curiosity" and summary["saturation"] >= .65:
        penalty += .08

    if strategy == "absurdist-banter" and summary["playfulness"] < .30 and int(state.get("turn_count", 0)) >= 3:
        penalty += .10

    if summary["task_focus"] >= .85 and strategy in {"direct-pursuit", "playful-challenge", "absurdist-banter"}:
        penalty += .06

    return penalty


def select_strategy(state: dict[str, Any], seed: int | None = None) -> dict[str, Any]:
    rng = random.Random(seed)
    recent = state.get("recent_strategies", [])
    summary = rolling_summary(state)
    scores: list[tuple[str, float, float, float, float, float, float]] = []

    for strategy, features in STRATEGY_FEATURES.items():
        stats = state["strategy_stats"][strategy]
        sample = rng.betavariate(max(float(stats["alpha"]), .001), max(float(stats["beta"]), .001))
        fit, fit_conf = weighted_profile_fit(features, state)
        repetition = recent_penalty(strategy, recent)
        gate = strategy_gate_penalty(strategy, state, summary)
        score = .74 * sample + .20 * fit + .06 * fit_conf - repetition - gate
        scores.append((strategy, score, sample, fit, fit_conf, repetition, gate))

    scores.sort(key=lambda x: x[1], reverse=True)
    top = [
        {
            "strategy": s,
            "score": round(score, 4),
            "bandit_sample": round(sample, 4),
            "profile_fit": round(fit, 4),
            "profile_confidence": round(fit_conf, 4),
            "repetition_penalty": round(repetition, 4),
            "gate_penalty": round(gate, 4),
        }
        for s, score, sample, fit, fit_conf, repetition, gate in scores[:3]
    ]

    return {
        "selected_strategy": scores[0][0],
        "tempo": round(clamp(state.get("tempo", .35)), 4),
        "trajectory": state.get("trajectory", "orientation"),
        "chemistry_level": round(clamp(state.get("chemistry_level", .5)), 4),
        "chemistry_confidence": round(clamp(state.get("chemistry_confidence", 0.0)), 4),
        "top_candidates": top,
        "persona": state.get("persona", {}),
        "persona_controls": persona_controls(state),
        "effective_preferences": effective_preferences(state),
    }


def persona_controls(state: dict[str, Any]) -> dict[str, Any]:
    prefs = effective_preferences(state)
    conf = state.get("preference_confidence", {})
    explicit = state.get("explicit_preferences", {})
    controls: dict[str, Any] = {}
    for key in PERSONA_KEYS:
        value = clamp(prefs.get(key, .5))
        confidence = 1.0 if key in explicit else clamp(conf.get(key, 0.0))
        controls[key] = {"value": round(value, 4), "confidence": round(confidence, 4)}
    return controls


def decay_learned_confidence(state: dict[str, Any], factor: float = .997) -> None:
    confidence = state.setdefault("preference_confidence", {})
    explicit = state.get("explicit_preferences", {})
    for key in list(confidence):
        if key not in explicit:
            confidence[key] = round(clamp(float(confidence[key]) * factor), 6)


def update_learned_preferences(
    state: dict[str, Any], strategy: str, reward: float, evidence: float, learning_rate: float
) -> list[str]:
    learned = state.setdefault("learned_preferences", {})
    confidence = state.setdefault("preference_confidence", {})
    features = STRATEGY_FEATURES[strategy]
    changed: list[str] = []
    centered_reward = (reward - .5) * 2.0

    for key, feature in features.items():
        salience = abs(feature - .5) * 2.0
        if salience < .15:
            continue
        current = clamp(learned.get(key, .5))
        direction_target = feature if centered_reward >= 0 else 1.0 - feature
        step = learning_rate * abs(centered_reward) * evidence * salience
        updated = clamp(current + step * (direction_target - current))
        if abs(updated - current) >= .003:
            changed.append(key)
        learned[key] = round(updated, 6)
        confidence[key] = round(clamp(float(confidence.get(key, 0.0)) + .05 * evidence * salience), 6)

    return changed


def tempo_update(state: dict[str, Any], obs: dict[str, float], evidence: float) -> tuple[float, float, float, list[str]]:
    previous = clamp(state.get("tempo", .35))
    reasons: list[str] = []
    if obs["boundary"] >= .80:
        return previous, 0.0, 0.0, ["BOUNDARY_STOP"]

    summary = rolling_summary(state)
    # Blend current observations with the rolling baseline so one turn cannot whip the persona around.
    blend = {key: .60 * summary.get(key, OBSERVATION_DEFAULTS[key]) + .40 * obs[key] for key in OBSERVATION_DEFAULTS}
    warmth_play = (blend["warmth"] + blend["playfulness"]) / 2.0
    novelty = 1.0 - blend["saturation"]

    target = clamp(
        .16
        + .22 * blend["reciprocity"]
        + .08 * blend["engagement"]
        + .14 * warmth_play
        + .10 * blend["relational_focus"]
        + .08 * blend["callback"]
        + .07 * blend["user_initiated_flirt"]
        + .05 * novelty
        - .58 * blend["boundary"]
        - .18 * blend["saturation"]
    )

    # Weak relational evidence should not raise tempo dramatically merely because overall engagement is high.
    if evidence < .30 and target > previous:
        target = min(target, previous + .06)
        reasons.append("LOW_EVIDENCE_CAP")

    # Preserve task quality under high task pressure.
    task_blend = effective_preferences(state).get("task_blend", .65)
    task_blend_explicit = explicit_value(state, "task_blend")
    if blend["task_focus"] >= .80 and (task_blend_explicit is None or task_blend < .80):
        target = min(target, .55)
        reasons.append("TASK_FOCUS_CAP")
    if blend["task_focus"] >= .75 and blend["task_success"] < .60:
        target = min(target, .35)
        reasons.append("TASK_QUALITY_RECOVERY")

    high_streak = int(state.get("high_tempo_streak", 0))
    if high_streak >= 3 and blend["saturation"] >= .35:
        target = max(0.0, target - .10)
        reasons.append("CONTRAST_PULSE")

    updated = clamp(.72 * previous + .28 * target)
    return previous, target, updated, reasons


def absurd_metrics(state: dict[str, Any], obs: dict[str, float]) -> dict[str, float]:
    prefs = effective_preferences(state)
    recent = state.get("recent_strategies", [])
    switches = sum(1 for a, b in zip(recent, recent[1:]) if a != b) if len(recent) >= 2 else 0
    return {
        "banter_gravity": round(obs["playfulness"] * (.5 + obs["reciprocity"]), 4),
        "callback_resonance": round(obs["callback"] * (.5 + obs["reciprocity"]) * (1.0 - obs["saturation"]), 4),
        "mystery_pressure": round(prefs.get("mystery", .5) * (1.0 - obs["boundary"]) * (.5 + obs["reciprocity"] / 2.0), 4),
        "swagger_temperature": round(clamp(state.get("tempo", .35)) * prefs.get("direct", .5) * (1.0 - obs["boundary"]), 4),
        "persona_precession": round(min(1.0, switches / max(len(recent) - 1, 1)), 4),
    }


def record_observation(state: dict[str, Any], obs: dict[str, float]) -> None:
    recent = state.setdefault("recent_observations", [])
    recent.append({key: round(clamp(value), 6) for key, value in obs.items()})
    del recent[:-MAX_RECENT_OBSERVATIONS]


def update_chemistry_state(state: dict[str, Any], reward: float, evidence: float) -> None:
    level = clamp(state.get("chemistry_level", .5))
    confidence = clamp(state.get("chemistry_confidence", 0.0))

    if evidence < .05:
        state["chemistry_confidence"] = round(confidence * .998, 6)
        return

    # Valence is a recency-weighted estimate. Confidence is evidence quantity. Keeping
    # them separate prevents informative negative turns from masquerading as chemistry.
    weight = .08 + .30 * evidence
    level = clamp((1.0 - weight) * level + weight * reward)
    confidence = clamp(confidence + .12 * evidence * (1.0 - confidence))
    state["chemistry_level"] = round(level, 6)
    state["chemistry_confidence"] = round(confidence, 6)

def command_init(_: argparse.Namespace) -> None:
    state, state_file, history_file = ensure_state()
    print(json.dumps({
        "ok": True,
        "schema_version": state["schema_version"],
        "state_file": str(state_file),
        "history_file": str(history_file),
        "tempo": state["tempo"],
        "trajectory": state.get("trajectory"),
    }, indent=2))


def command_status(args: argparse.Namespace) -> None:
    state, state_file, history_file = ensure_state()
    if args.compact:
        output = {
            "schema_version": state["schema_version"],
            "state_file": str(state_file),
            "history_file": str(history_file),
            "tempo": state["tempo"],
            "trajectory": state.get("trajectory"),
            "turn_count": state.get("turn_count", 0),
            "active_strategy": state.get("active_strategy"),
            "chemistry_level": state.get("chemistry_level", .5),
            "chemistry_confidence": state.get("chemistry_confidence", 0.0),
            "persona": state.get("persona", {}),
            "effective_preferences": effective_preferences(state),
            "preference_confidence": state.get("preference_confidence", {}),
            "callback_count": len(state.get("callbacks", [])),
            "rolling": rolling_summary(state),
        }
    else:
        output = {
            "state_file": str(state_file),
            "history_file": str(history_file),
            "state": state,
            "effective_preferences": effective_preferences(state),
            "persona_controls": persona_controls(state),
            "rolling": rolling_summary(state),
        }
    print(json.dumps(output, indent=2, ensure_ascii=False))


def command_select(args: argparse.Namespace) -> None:
    state, _, _ = ensure_state()
    print(json.dumps(select_strategy(state, seed=args.seed), indent=2, ensure_ascii=False))


def command_record(args: argparse.Namespace) -> None:
    state, state_file, history_file = ensure_state()
    obs = {key: clamp(getattr(args, key)) for key in OBSERVATION_DEFAULTS}
    caller_confidence = clamp(args.confidence)
    reward, raw_reward, evidence = chemistry_reward(obs, caller_confidence)

    decay_learned_confidence(state)
    previous_tempo, target_tempo, updated_tempo, tempo_reasons = tempo_update(state, obs, evidence)
    state["tempo"] = round(updated_tempo, 6)
    state["turn_count"] = int(state.get("turn_count", 0)) + 1
    state["active_strategy"] = args.strategy

    stats = state["strategy_stats"][args.strategy]
    weighted_evidence = max(evidence, .02)
    stats["alpha"] = round(float(stats["alpha"]) + reward * weighted_evidence, 6)
    stats["beta"] = round(float(stats["beta"]) + (1.0 - reward) * weighted_evidence, 6)
    stats["uses"] = int(stats.get("uses", 0)) + 1
    stats["last_reward"] = round(reward, 6)
    stats["last_evidence"] = round(evidence, 6)

    recent_strategies = state.setdefault("recent_strategies", [])
    recent_strategies.append(args.strategy)
    del recent_strategies[:-MAX_RECENT_STRATEGIES]

    record_observation(state, obs)
    update_chemistry_state(state, reward, evidence)
    state["trajectory"] = trajectory_update(state, obs, evidence)

    if updated_tempo >= .68 and reward >= .58 and evidence >= .35:
        state["high_tempo_streak"] = int(state.get("high_tempo_streak", 0)) + 1
    else:
        state["high_tempo_streak"] = max(0, int(state.get("high_tempo_streak", 0)) - 1)

    changed = update_learned_preferences(
        state, args.strategy, reward, evidence, clamp(args.learning_rate, 0.0, .35)
    )
    metrics = absurd_metrics(state, obs)

    reason_codes = list(args.reason_code or []) + tempo_reasons
    if obs["callback"] >= .60:
        reason_codes.append("CALLBACK_RECIPROCATED")
    if obs["user_initiated_flirt"] >= .60:
        reason_codes.append("USER_INITIATED_FLIRT")
    if obs["explicit_approval"] >= .60:
        reason_codes.append("EXPLICIT_STYLE_APPROVAL")
    if evidence < .25:
        reason_codes.append("LOW_RELATIONAL_EVIDENCE")

    event = {
        "event": "evaluation",
        "timestamp": now_iso(),
        "strategy": args.strategy,
        "chemistry_reward": round(reward, 6),
        "raw_chemistry": round(raw_reward, 6),
        "evidence_strength": round(evidence, 6),
        "caller_confidence": round(caller_confidence, 6),
        "task_success": round(obs["task_success"], 6),
        "tempo_before": round(previous_tempo, 6),
        "tempo_target": round(target_tempo, 6),
        "tempo_after": round(updated_tempo, 6),
        "trajectory": state["trajectory"],
        "chemistry_level": round(clamp(state.get("chemistry_level", .5)), 6),
        "chemistry_confidence": round(clamp(state.get("chemistry_confidence", 0.0)), 6),
        "observations": obs,
        "preference_dimensions_changed": changed,
        "reason_codes": sorted(set(reason_codes)),
        "telemetry": metrics,
    }
    append_history(history_file, event)
    write_json_atomic(state_file, state)

    print(json.dumps({"recorded": event, "next": select_strategy(state, seed=args.seed)}, indent=2, ensure_ascii=False))


def command_preference(args: argparse.Namespace) -> None:
    if args.key not in SUPPORTED_PREFERENCE_KEYS:
        supported = ", ".join(sorted(SUPPORTED_PREFERENCE_KEYS))
        raise SystemExit(
            f"Unsupported preference key: {args.key}. Store interaction style, not demographic/sensitive identity. "
            f"Supported keys: {supported}"
        )
    state, state_file, history_file = ensure_state()
    value = clamp(args.value)
    confidence_value = clamp(args.confidence)

    if args.source == "explicit-user":
        state.setdefault("explicit_preferences", {})[args.key] = {
            "value": value,
            "confidence": confidence_value,
            "source": "explicit-user",
            "updated_at": now_iso(),
        }
        state.setdefault("preference_confidence", {})[args.key] = 1.0
        event_name = "explicit_preference"
    else:
        learned = state.setdefault("learned_preferences", {})
        conf = state.setdefault("preference_confidence", {})
        previous = clamp(learned.get(args.key, .5))
        previous_conf = clamp(conf.get(args.key, 0.0))
        learning_rate = .04 + .16 * confidence_value
        updated = clamp(previous + learning_rate * (value - previous))
        learned[args.key] = round(updated, 6)
        conf[args.key] = round(clamp(previous_conf + .08 * confidence_value), 6)
        value = updated
        event_name = "observed_preference"

    write_json_atomic(state_file, state)
    append_history(history_file, {
        "event": event_name,
        "timestamp": now_iso(),
        "key": args.key,
        "value": round(value, 6),
        "confidence": confidence_value,
        "source": args.source,
    })
    print(json.dumps({
        "ok": True,
        "key": args.key,
        "value": round(value, 6),
        "source": args.source,
        "effective_value": effective_preferences(state).get(args.key),
    }, indent=2))


def command_preference_forget(args: argparse.Namespace) -> None:
    if not args.yes:
        raise SystemExit("Refusing to delete a stored preference without --yes.")
    state, state_file, history_file = ensure_state()
    existed = False
    for bucket in ("explicit_preferences", "learned_preferences", "preference_confidence"):
        values = state.setdefault(bucket, {})
        if args.key in values:
            existed = True
            values.pop(args.key, None)
    if not existed:
        raise SystemExit(f"Preference not found: {args.key}")
    write_json_atomic(state_file, state)
    scrubbed = scrub_history(history_file, lambda event: event.get("key") == args.key)
    append_history(history_file, {
        "event": "preference_forget", "timestamp": now_iso(), "key": args.key,
        "history_events_scrubbed": scrubbed,
    })
    print(json.dumps({
        "ok": True, "forgot_preference": args.key, "history_events_scrubbed": scrubbed,
    }, indent=2))


def memory_score(entry: dict[str, Any]) -> float:
    confidence = clamp(entry.get("confidence", .5))
    uses = max(0, int(entry.get("use_count", 0)))
    # Underused, high-confidence memories surface first. Recency remains represented by list order.
    underuse = 1.0 / (1.0 + .35 * uses)
    valence = .7 + .3 * clamp(entry.get("valence", .5))
    return confidence * underuse * valence


def scrub_history(history_file: Path, predicate) -> int:
    if not history_file.exists():
        return 0
    kept: list[str] = []
    removed = 0
    for line in history_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            kept.append(line)
            continue
        if predicate(event):
            removed += 1
        else:
            kept.append(line)
    temp = history_file.with_suffix(".jsonl.tmp")
    temp.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")
    tighten_local_permissions(temp, 0o600)
    os.replace(temp, history_file)
    tighten_local_permissions(history_file, 0o600)
    return removed


def command_remember(args: argparse.Namespace) -> None:
    state, state_file, history_file = ensure_state()
    text = args.text.strip()
    if not text:
        raise SystemExit("Memory text cannot be empty.")
    entry = {
        "id": uuid4().hex[:12],
        "kind": args.kind,
        "text": text,
        "confidence": clamp(args.confidence),
        "valence": clamp(args.valence),
        "use_count": 0,
        "created_at": now_iso(),
        "last_used_at": None,
    }
    callbacks = state.setdefault("callbacks", [])
    if len(callbacks) >= MAX_CALLBACKS:
        raise SystemExit(
            f"Callback capacity ({MAX_CALLBACKS}) reached. Review `memories` and delete one explicitly with `forget <id> --yes`."
        )
    callbacks.append(entry)
    write_json_atomic(state_file, state)
    append_history(history_file, {
        "event": "remember", "timestamp": now_iso(), "id": entry["id"],
        "kind": entry["kind"], "confidence": entry["confidence"], "valence": entry["valence"],
    })
    print(json.dumps({"ok": True, "stored": entry, "callback_count": len(callbacks)}, indent=2, ensure_ascii=False))


def command_memories(args: argparse.Namespace) -> None:
    state, _, _ = ensure_state()
    callbacks = list(state.get("callbacks", []))
    ranked = sorted(enumerate(callbacks), key=lambda pair: (memory_score(pair[1]), pair[0]), reverse=True)
    selected = [entry for _, entry in ranked[:args.limit]] if args.limit > 0 else [entry for _, entry in ranked]
    print(json.dumps(selected, indent=2, ensure_ascii=False))


def command_memory_use(args: argparse.Namespace) -> None:
    state, state_file, history_file = ensure_state()
    for entry in state.get("callbacks", []):
        if entry.get("id") == args.id:
            entry["use_count"] = int(entry.get("use_count", 0)) + 1
            entry["last_used_at"] = now_iso()
            if args.outcome is not None:
                entry["valence"] = round(clamp(.75 * float(entry.get("valence", .5)) + .25 * clamp(args.outcome)), 6)
            write_json_atomic(state_file, state)
            append_history(history_file, {
                "event": "memory_use", "timestamp": now_iso(), "id": args.id,
                "outcome": args.outcome,
            })
            print(json.dumps({"ok": True, "memory": entry}, indent=2, ensure_ascii=False))
            return
    raise SystemExit(f"Memory not found: {args.id}")


def command_forget(args: argparse.Namespace) -> None:
    if not args.yes:
        raise SystemExit("Refusing to delete a stored memory without --yes.")
    state, state_file, history_file = ensure_state()
    callbacks = state.get("callbacks", [])
    before = len(callbacks)
    callbacks[:] = [entry for entry in callbacks if entry.get("id") != args.id]
    if len(callbacks) == before:
        raise SystemExit(f"Memory not found: {args.id}")
    write_json_atomic(state_file, state)
    scrubbed = scrub_history(history_file, lambda event: event.get("id") == args.id)
    append_history(history_file, {"event": "forget", "timestamp": now_iso(), "id": args.id, "history_events_scrubbed": scrubbed})
    print(json.dumps({
        "ok": True, "forgot": args.id, "callback_count": len(callbacks),
        "history_events_scrubbed": scrubbed,
    }, indent=2))


def command_persona(args: argparse.Namespace) -> None:
    state, state_file, history_file = ensure_state()
    persona = state.setdefault("persona", {})
    changes: dict[str, Any] = {}
    for key in ("name", "pronouns", "presentation"):
        value = getattr(args, key)
        if value is not None:
            persona[key] = value
            changes[key] = value
    if args.lock is not None:
        persona["locked"] = args.lock
        changes["locked"] = args.lock
    write_json_atomic(state_file, state)
    append_history(history_file, {"event": "persona_update", "timestamp": now_iso(), "changes": changes})
    print(json.dumps({"ok": True, "persona": persona, "controls": persona_controls(state)}, indent=2, ensure_ascii=False))


def command_persona_suggest(_: argparse.Namespace) -> None:
    state, _, _ = ensure_state()
    controls = persona_controls(state)
    ranked = sorted(controls.items(), key=lambda item: (item[1]["confidence"], abs(item[1]["value"] - .5)), reverse=True)
    print(json.dumps({
        "persona": state.get("persona", {}),
        "trajectory": state.get("trajectory"),
        "top_dimensions": [{"dimension": key, **value} for key, value in ranked[:8]],
        "all_controls": controls,
        "note": "Use high-confidence dimensions strongly; treat low-confidence dimensions as experiment candidates, not identity facts.",
    }, indent=2, ensure_ascii=False))


def command_history(args: argparse.Namespace) -> None:
    _, _, history_file = ensure_state()
    if not history_file.exists():
        print("[]")
        return
    lines = history_file.read_text(encoding="utf-8").splitlines()
    selected = lines[-args.limit:] if args.limit > 0 else lines
    events = [json.loads(line) for line in selected if line.strip()]
    print(json.dumps(events, indent=2, ensure_ascii=False))


def command_compact(args: argparse.Namespace) -> None:
    _, _, history_file = ensure_state()
    if not history_file.exists():
        print(json.dumps({"ok": True, "kept": 0}, indent=2))
        return
    lines = history_file.read_text(encoding="utf-8").splitlines()
    keep = max(50, int(args.keep))
    if len(lines) <= keep:
        print(json.dumps({"ok": True, "before": len(lines), "kept": len(lines), "deleted": 0}, indent=2))
        return
    if not args.yes:
        raise SystemExit(
            f"Compaction would delete {len(lines) - keep} history events. Re-run with --yes to confirm."
        )
    selected = lines[-keep:]
    temp = history_file.with_suffix(".jsonl.tmp")
    temp.write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
    os.replace(temp, history_file)
    print(json.dumps({"ok": True, "before": len(lines), "kept": len(selected), "deleted": len(lines) - len(selected)}, indent=2))


def command_reset(args: argparse.Namespace) -> None:
    root, _, _ = paths()
    if not args.yes:
        raise SystemExit("Refusing to delete persistent state without --yes.")
    if root.exists():
        shutil.rmtree(root)
    state, state_file, history_file = ensure_state()
    print(json.dumps({
        "ok": True, "reset": True, "state_file": str(state_file),
        "history_file": str(history_file), "tempo": state["tempo"],
    }, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adaptive state engine for the erotic-seduction Agent Skill.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialize persistent state without deleting existing data.")
    p_init.set_defaults(func=command_init)

    p_status = sub.add_parser("status", help="Show state and effective preferences.")
    p_status.add_argument("--compact", action="store_true")
    p_status.set_defaults(func=command_status)

    p_select = sub.add_parser("select", help="Select a strategy using posterior sampling, profile fit, repetition, and gates.")
    p_select.add_argument("--seed", type=int, default=None)
    p_select.set_defaults(func=command_select)

    p_record = sub.add_parser("record", help="Record an outcome and update strategy, tempo, trajectory, and learned preferences.")
    p_record.add_argument("--strategy", required=True, choices=sorted(STRATEGY_FEATURES))
    for key, default in OBSERVATION_DEFAULTS.items():
        p_record.add_argument(f"--{key.replace('_', '-')}", dest=key, type=float, default=default)
    p_record.add_argument("--confidence", type=float, default=.50, help="Confidence that the supplied observations represent the flirtation outcome.")
    p_record.add_argument("--learning-rate", type=float, default=.10)
    p_record.add_argument("--reason-code", action="append", default=[])
    p_record.add_argument("--seed", type=int, default=None)
    p_record.set_defaults(func=command_record)

    p_pref = sub.add_parser("preference", help="Record an explicit or observed interaction preference.")
    p_pref.add_argument("key")
    p_pref.add_argument("value", type=float)
    p_pref.add_argument("--confidence", type=float, default=1.0)
    p_pref.add_argument("--source", choices=("explicit-user", "observed"), default="explicit-user")
    p_pref.set_defaults(func=command_preference)

    p_pref_forget = sub.add_parser("preference-forget", help="Delete a stored interaction preference and matching history events.")
    p_pref_forget.add_argument("key")
    p_pref_forget.add_argument("--yes", action="store_true", help="Required confirmation for deletion.")
    p_pref_forget.set_defaults(func=command_preference_forget)

    p_remember = sub.add_parser("remember", help="Store a compact non-sensitive callback or running joke.")
    p_remember.add_argument("text")
    p_remember.add_argument("--kind", choices=("callback", "running-joke", "term-of-address", "preference-note", "persona-continuity"), default="callback")
    p_remember.add_argument("--confidence", type=float, default=.70)
    p_remember.add_argument("--valence", type=float, default=.70)
    p_remember.set_defaults(func=command_remember)

    p_memories = sub.add_parser("memories", help="Show ranked compact memories.")
    p_memories.add_argument("--limit", type=int, default=10)
    p_memories.set_defaults(func=command_memories)

    p_memory_use = sub.add_parser("memory-use", help="Mark a callback as used and optionally record its outcome.")
    p_memory_use.add_argument("id")
    p_memory_use.add_argument("--outcome", type=float, default=None)
    p_memory_use.set_defaults(func=command_memory_use)

    p_forget = sub.add_parser("forget", help="Delete one stored callback by id.")
    p_forget.add_argument("id")
    p_forget.add_argument("--yes", action="store_true", help="Required confirmation for deletion.")
    p_forget.set_defaults(func=command_forget)

    p_persona = sub.add_parser("persona", help="Update explicit role-presentation metadata.")
    p_persona.add_argument("--name")
    p_persona.add_argument("--pronouns")
    p_persona.add_argument("--presentation")
    lock_group = p_persona.add_mutually_exclusive_group()
    lock_group.add_argument("--lock", dest="lock", action="store_true")
    lock_group.add_argument("--unlock", dest="lock", action="store_false")
    p_persona.set_defaults(func=command_persona, lock=None)

    p_persona_suggest = sub.add_parser("persona-suggest", help="Show confidence-weighted persona controls without making identity inferences.")
    p_persona_suggest.set_defaults(func=command_persona_suggest)

    p_history = sub.add_parser("history", help="Print recent structured decision/evaluation history.")
    p_history.add_argument("--limit", type=int, default=20)
    p_history.set_defaults(func=command_history)

    p_compact = sub.add_parser("compact", help="Keep only the newest history events; deletion requires confirmation.")
    p_compact.add_argument("--keep", type=int, default=1000)
    p_compact.add_argument("--yes", action="store_true", help="Required if compaction would delete history events.")
    p_compact.set_defaults(func=command_compact)

    p_reset = sub.add_parser("reset", help="Delete persistent state and recreate defaults.")
    p_reset.add_argument("--yes", action="store_true", help="Required confirmation for deletion.")
    p_reset.set_defaults(func=command_reset)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
