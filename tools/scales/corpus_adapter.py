"""
CorpusAdapter — creates novel music from real Mozart DNA.

Takes actual bars from the 6,987-bar Mozart corpus and transforms
them: transposition, re-harmonization, rhythmic variation, fragment
combination, density adjustment. Produces novel bars that sound
authentically Mozartean because they're built from real musical cells.

Not copying — adapting. The rhythmic skeletons, melodic gestures,
and textural behaviors come from real Mozart, but the specific
pitches, harmonies, and combinations are new.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .pitch import (
    build_scale,
    clamp_to_range,
    is_minor_key,
    key_to_root_midi,
    midi_to_pitch,
    pitch_to_midi,
)

_CORPUS_DIR = Path(__file__).parent.parent / "reference_index"


@dataclass
class CorpusQuery:
    """Multi-dimensional query for corpus bar retrieval."""

    time_sig: Tuple[int, int] = (4, 4)
    key_mode: str = "minor"
    rh_texture: Optional[str] = None
    lh_texture: Optional[str] = None
    melody_density_range: Optional[Tuple[int, int]] = None
    accomp_density_range: Optional[Tuple[int, int]] = None
    melody_direction: Optional[str] = None
    phrase_position: Optional[str] = None
    has_grace_notes: Optional[bool] = None
    has_dotted_rhythms: Optional[bool] = None
    exclude_sources: List[str] = field(default_factory=list)
    n: int = 10


@dataclass
class AdaptedBar:
    """A corpus bar transformed for the target context."""

    rh_events: List[Dict] = field(default_factory=list)
    rh_inner_events: List[Dict] = field(default_factory=list)  # inner RH voice ('//' polyphony)
    lh_inner_events: List[Dict] = field(default_factory=list)  # inner LH voice ('//' polyphony)
    lh_events: List[Dict] = field(default_factory=list)
    target_key: str = "Gm"
    target_bar_num: int = 1
    source_provenance: List[str] = field(default_factory=list)
    transforms_applied: List[str] = field(default_factory=list)
    melody_density: int = 0
    accomp_density: int = 0


# Parallel-mode degree mapping. Converting a major exemplar for a minor phrase
# (or the reverse) means changing the 3rd, 6th and 7th degrees — it does NOT
# mean bending every note to the nearest scale tone.
_MAJOR_TO_MINOR = {4: 3, 9: 8, 11: 10}
_MINOR_TO_MAJOR = {3: 4, 8: 9, 10: 11}


def _remode(midi: int, tonic_pc: int, src_mode: str, tgt_mode: str) -> int:
    """Re-cast one pitch from one mode into the other, keeping everything else.

    Snapping to the target scale — which is what this used to do to EVERY note —
    deletes exactly the notes that matter. The brief tells the composer that a
    single chromatic inflection "colors the emotional temperature of the
    phrase", and then hands it exemplars with every chromatic note flattened
    onto the nearest diatonic degree. Appoggiaturas, applied dominants, the
    raised fourth and the Neapolitan all vanished before the composer saw them.
    """
    if src_mode == tgt_mode:
        return midi
    table = _MAJOR_TO_MINOR if src_mode != "minor" else _MINOR_TO_MAJOR
    degree = (midi - tonic_pc) % 12
    if degree not in table:
        return midi
    return midi + (table[degree] - degree)


class CorpusAdapter:
    """Adapts real Mozart corpus bars to new musical contexts."""

    def __init__(self, composer: str = "mozart"):
        self.composer = composer
        self._bars: Optional[List[Dict]] = None
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        self._bars = []
        corpus_dir = _CORPUS_DIR / self.composer
        for shard in sorted(corpus_dir.glob("bars_*.json")):
            with open(shard) as f:
                self._bars.extend(json.load(f))
        if not self._bars:
            # Smaller composers keep bars inline in bar_index.json
            index_path = corpus_dir / "bar_index.json"
            if index_path.exists():
                try:
                    with open(index_path) as f:
                        data = json.load(f)
                    if isinstance(data, dict) and isinstance(data.get("bars"), list):
                        self._bars.extend(data["bars"])
                except (json.JSONDecodeError, OSError):
                    pass
        self._loaded = True

    # ─── Retrieval ────────────────────────────────────────────────────

    def retrieve(self, query: CorpusQuery) -> List[Dict]:
        """Multi-dimensional corpus bar retrieval with scoring."""
        self._ensure_loaded()

        candidates = []
        for bar in self._bars:
            score = self._score_bar(bar, query)
            if score > 0:
                candidates.append((score, bar))

        candidates.sort(key=lambda x: -x[0])
        return [bar for _, bar in candidates[: query.n]]

    def _score_bar(self, bar: Dict, q: CorpusQuery) -> float:
        """Score a bar against a query. Returns 0 if hard filters fail."""
        # Hard filters
        ts = bar.get("time_sig", [4, 4])
        if tuple(ts) != q.time_sig:
            return 0.0
        if bar.get("key_mode", "") != q.key_mode:
            return 0.0
        if bar.get("source", "") in q.exclude_sources:
            return 0.0

        score = 1.0

        # Texture match (0.30 weight)
        if q.rh_texture and bar.get("rh_texture") == q.rh_texture:
            score += 0.3
        if q.lh_texture and bar.get("lh_texture") == q.lh_texture:
            score += 0.3

        # Density match (0.20 weight)
        md = bar.get("melody_density", 0)
        ad = bar.get("accomp_density", 0)
        if q.melody_density_range:
            lo, hi = q.melody_density_range
            if lo <= md <= hi:
                score += 0.2
            elif md < lo - 3 or md > hi + 3:
                return 0.0  # too far off

        if q.accomp_density_range:
            lo, hi = q.accomp_density_range
            if lo <= ad <= hi:
                score += 0.1

        # Melody direction (0.15 weight)
        if q.melody_direction and bar.get("melody_direction") == q.melody_direction:
            score += 0.15

        # Phrase position (0.10 weight)
        if q.phrase_position and bar.get("phrase_position") == q.phrase_position:
            score += 0.1

        # Features (0.05 each)
        if (
            q.has_dotted_rhythms is not None
            and bar.get("has_dotted_rhythms") == q.has_dotted_rhythms
        ):
            score += 0.05
        if q.has_grace_notes is not None and bar.get("has_grace_notes") == q.has_grace_notes:
            score += 0.05

        # Prefer higher density (more musical content)
        score += min(0.1, (md + ad) / 200)

        return score

    # ─── Transposition ────────────────────────────────────────────────

    def transpose_bar(self, bar: Dict, target_key: str, target_bar_num: int = 1) -> AdaptedBar:
        """Transpose a corpus bar to a target key using interval_from_root.

        Uses the bar's interval_from_root values for key-agnostic transposition.
        Falls back to chromatic transposition from rh_display/lh_display.
        """
        source_key = bar.get("key", "C")
        target_root = key_to_root_midi(target_key)
        target_mode = "minor" if is_minor_key(target_key) else "major"
        target_scale = build_scale(target_root + 48, target_mode)

        source_mode = bar.get("key_mode") or ("minor" if is_minor_key(source_key) else "major")
        rh_adapted = self._transpose_events(
            bar.get("rh_events", []),
            bar.get("rh_display", []),
            source_key,
            target_key,
            target_root,
            target_scale,
            target_mode,
            register_base=60,  # RH in octave 4+
            source_mode=source_mode,
        )
        lh_adapted = self._transpose_events(
            bar.get("lh_events", []),
            bar.get("lh_display", []),
            source_key,
            target_key,
            target_root,
            target_scale,
            target_mode,
            register_base=36,  # LH in octave 2-3
            source_mode=source_mode,
        )

        rh_inner = bar.get("rh_inner_display") or []
        rh_inner_adapted = (
            self._transpose_events(
                rh_inner,
                rh_inner,
                source_key,
                target_key,
                target_root,
                target_scale,
                target_mode,
                register_base=60,
                source_mode=source_mode,
            )
            if rh_inner
            else []
        )
        # The LOWER staff's inner voice — a chorale's tenor, the middle line of a
        # keyboard texture. It was extracted into the corpus and then dropped
        # here, so four-part writing reached the brief as two parts.
        lh_inner = bar.get("lh_inner_display") or []
        lh_inner_adapted = (
            self._transpose_events(
                lh_inner,
                lh_inner,
                source_key,
                target_key,
                target_root,
                target_scale,
                target_mode,
                register_base=36,
            )
            if lh_inner
            else []
        )

        return AdaptedBar(
            rh_events=rh_adapted,
            rh_inner_events=rh_inner_adapted,
            lh_inner_events=lh_inner_adapted,
            lh_events=lh_adapted,
            target_key=target_key,
            target_bar_num=target_bar_num,
            source_provenance=[f"{bar.get('source', '?')} bar {bar.get('bar_num', '?')}"],
            transforms_applied=[f"transpose {source_key}->{target_key}"],
            melody_density=len([e for e in rh_adapted if e.get("type") != "rest"]),
            accomp_density=len([e for e in lh_adapted if e.get("type") != "rest"]),
        )

    def _transpose_events(
        self,
        events: List[Dict],
        display: List[Dict],
        source_key: str,
        target_key: str,
        target_root: int,
        target_scale: List[int],
        target_mode: str,
        register_base: int,
        source_mode: str = "major",
    ) -> List[Dict]:
        """Transpose a list of events to the target key.

        EXACT interval transposition. Chromatic notes are preserved; only a
        change of MODE alters a pitch, and then only the 3rd, 6th and 7th
        degrees that define the mode.
        """
        result = []
        source_root = key_to_root_midi(source_key)
        transpose_semitones = target_root - source_root

        # Prefer display events (have actual pitches)
        use_events = display if display else events

        def _ornaments(src: Dict) -> Dict:
            """Carry through ornament/grace metadata the corpus actually stores
            (slurs/dynamics/articulation are NOT in the corpus — only these)."""
            orn = {}
            if src.get("has_trill"):
                orn["has_trill"] = True
            if src.get("has_turn"):
                orn["has_turn"] = True
            if src.get("is_grace"):
                orn["is_grace"] = True
            return orn

        for evt in use_events:
            if evt.get("type") == "rest":
                result.append({"type": "rest", "dur": evt.get("dur", 1.0)})
                continue

            dur = evt.get("dur", 1.0)

            if evt.get("type") == "chord":
                pitches = evt.get("pitches", [])
                new_pitches = []
                for p in pitches:
                    midi = pitch_to_midi(p)
                    if midi is not None:
                        new_midi = _remode(
                            midi + transpose_semitones, target_root, source_mode, target_mode
                        )
                        new_pitches.append(midi_to_pitch(new_midi, target_key))
                chord_evt = {"type": "chord", "pitches": new_pitches, "dur": dur}
                if "chord_intervals" in evt:
                    chord_evt["chord_intervals"] = evt["chord_intervals"]
                chord_evt.update(_ornaments(evt))
                result.append(chord_evt)
            else:
                # Single note
                pitch_str = evt.get("pitch")
                if pitch_str:
                    midi = pitch_to_midi(pitch_str)
                    if midi is not None:
                        new_midi = _remode(
                            midi + transpose_semitones, target_root, source_mode, target_mode
                        )
                        note_evt = {
                            "type": "note",
                            "pitch": midi_to_pitch(new_midi, target_key),
                            "dur": dur,
                        }
                        note_evt.update(_ornaments(evt))
                        result.append(note_evt)
                    else:
                        result.append({"type": "rest", "dur": dur})
                elif "interval_from_root" in evt:
                    interval = evt["interval_from_root"]
                    new_midi = target_root + 48 + interval
                    if register_base > 48:
                        new_midi = clamp_to_range(new_midi, 60, 96)
                    else:
                        new_midi = clamp_to_range(new_midi, 36, 72)
                    new_midi = _remode(new_midi, target_root, source_mode, target_mode)
                    interval_evt = {
                        "type": "note",
                        "pitch": midi_to_pitch(new_midi, target_key),
                        "dur": dur,
                    }
                    interval_evt.update(_ornaments(evt))
                    result.append(interval_evt)
                else:
                    result.append({"type": "rest", "dur": dur})

        return result

    # ─── Variation ────────────────────────────────────────────────────

    def dotted_inject(self, adapted: AdaptedBar) -> AdaptedBar:
        """Convert pairs of even notes into dotted+short pairs."""
        for events_key in ("rh_events", "lh_events"):
            events = (
                getattr(adapted, events_key)
                if hasattr(adapted, events_key)
                else adapted.__dict__.get(events_key, [])
            )
            new_events = []
            i = 0
            while i < len(events):
                if (
                    i + 1 < len(events)
                    and events[i].get("type") == "note"
                    and events[i + 1].get("type") == "note"
                    and events[i].get("dur") == events[i + 1].get("dur")
                    and events[i]["dur"] in (0.5, 0.25)
                    and random.random() < 0.3
                ):
                    # Convert pair to dotted+short
                    d = events[i]["dur"]
                    new_events.append({**events[i], "dur": d * 1.5})
                    new_events.append({**events[i + 1], "dur": d * 0.5})
                    i += 2
                else:
                    new_events.append(events[i])
                    i += 1
            if events_key == "rh_events":
                adapted.rh_events = new_events
            else:
                adapted.lh_events = new_events
        adapted.transforms_applied.append("dotted_inject")
        return adapted

    def density_adjust(
        self, adapted: AdaptedBar, target_density: int, hand: str = "lh"
    ) -> AdaptedBar:
        """Adjust density by merging or splitting events."""
        events = adapted.rh_events if hand == "rh" else adapted.lh_events
        note_events = [e for e in events if e.get("type") != "rest"]
        current = len(note_events)

        if current == 0 or target_density == current:
            return adapted

        if target_density < current:
            # Reduce: merge short notes into longer ones
            merged = []
            i = 0
            while (
                i < len(events)
                and len([e for e in merged if e.get("type") != "rest"]) < target_density
            ):
                merged.append(events[i])
                i += 1
            # Keep remaining duration as the last note extended
            if merged and i < len(events):
                remaining_dur = sum(e.get("dur", 0) for e in events[i:])
                merged[-1]["dur"] = merged[-1].get("dur", 0) + remaining_dur
            if hand == "rh":
                adapted.rh_events = merged
            else:
                adapted.lh_events = merged
        else:
            # Increase: split long notes into shorter repetitions
            expanded = []
            for e in events:
                if (
                    e.get("type") == "note"
                    and e.get("dur", 0) >= 1.0
                    and len(expanded) < target_density
                ):
                    half_dur = e["dur"] / 2
                    expanded.append({**e, "dur": half_dur})
                    expanded.append({**e, "dur": half_dur})
                else:
                    expanded.append(e)
            if hand == "rh":
                adapted.rh_events = expanded
            else:
                adapted.lh_events = expanded

        adapted.transforms_applied.append(f"density_adjust_{hand}_{target_density}")
        return adapted

    def register_shift(
        self, adapted: AdaptedBar, hand: str = "rh", semitones: int = 12
    ) -> AdaptedBar:
        """Shift all notes in one hand by semitones (usually ±12 for octave)."""
        events = adapted.rh_events if hand == "rh" else adapted.lh_events
        for e in events:
            if e.get("type") == "note" and e.get("pitch"):
                midi = pitch_to_midi(e["pitch"])
                if midi is not None:
                    new_midi = midi + semitones
                    if hand == "rh":
                        new_midi = clamp_to_range(new_midi, 48, 96)
                    else:
                        new_midi = clamp_to_range(new_midi, 24, 72)
                    e["pitch"] = midi_to_pitch(new_midi, adapted.target_key)
            elif e.get("type") == "chord" and e.get("pitches"):
                new_pitches = []
                for p in e["pitches"]:
                    midi = pitch_to_midi(p)
                    if midi is not None:
                        new_midi = clamp_to_range(midi + semitones, 24, 96)
                        new_pitches.append(midi_to_pitch(new_midi, adapted.target_key))
                e["pitches"] = new_pitches

        adapted.transforms_applied.append(f"register_shift_{hand}_{semitones:+d}")
        return adapted

    # ─── Combination ──────────────────────────────────────────────────

    def combine_hands(
        self, rh_bar: Dict, lh_bar: Dict, target_key: str, target_bar_num: int = 1
    ) -> AdaptedBar:
        """Take RH from one corpus bar and LH from another."""
        rh_adapted = self.transpose_bar(rh_bar, target_key, target_bar_num)
        lh_adapted = self.transpose_bar(lh_bar, target_key, target_bar_num)

        return AdaptedBar(
            rh_events=rh_adapted.rh_events,
            lh_events=lh_adapted.lh_events,
            target_key=target_key,
            target_bar_num=target_bar_num,
            source_provenance=[
                f"{rh_bar.get('source', '?')} bar {rh_bar.get('bar_num', '?')} (RH)",
                f"{lh_bar.get('source', '?')} bar {lh_bar.get('bar_num', '?')} (LH)",
            ],
            transforms_applied=["combine_hands"],
            melody_density=rh_adapted.melody_density,
            accomp_density=lh_adapted.accomp_density,
        )

    # ─── Conversion to LayerIR events ─────────────────────────────────

    def adapted_bar_to_shorthand(self, adapted: AdaptedBar) -> Dict:
        """Convert an AdaptedBar to direct_compose shorthand.

        Delegates to the brief's renderer, which keeps chords as chords, carries
        ornaments and grace notes, and shows the inner voice with ``//``. The
        version that lived here collapsed every chord to ONE note — the top of a
        right-hand chord, the bottom of a left-hand one — so a bar of real
        chordal writing came out as a single line with the harmony deleted.
        """
        from .composition_brief import _adapted_to_shorthand

        rh, lh = _adapted_to_shorthand(adapted)
        return {"rh": rh, "lh": lh}

    # ─── Top-level: adapt a phrase ────────────────────────────────────

    def adapt_phrase(
        self,
        n_bars: int,
        target_key: str,
        bar_start: int = 1,
        textures: Optional[List[Tuple[str, str]]] = None,
        densities: Optional[List[int]] = None,
        directions: Optional[List[str]] = None,
        phrase_position: str = "middle",
        inject_dotted: bool = True,
    ) -> List[AdaptedBar]:
        """Adapt n_bars of corpus material to a phrase context.

        For each bar, retrieves the best matching corpus bar,
        transposes to target key, and applies variations.
        """
        key_mode = "minor" if is_minor_key(target_key) else "major"
        results = []
        used_sources: List[str] = []

        for i in range(n_bars):
            rh_tex = textures[i][0] if textures and i < len(textures) else None
            lh_tex = textures[i][1] if textures and i < len(textures) else None
            density = densities[i] if densities and i < len(densities) else None
            direction = directions[i] if directions and i < len(directions) else None

            # Infer phrase position for first/last bars
            pos = phrase_position
            if i == 0:
                pos = "opening"
            elif i == n_bars - 1:
                pos = "cadential"

            query = CorpusQuery(
                time_sig=(4, 4),
                key_mode=key_mode,
                rh_texture=rh_tex,
                lh_texture=lh_tex,
                melody_density_range=(max(3, (density or 8) - 4), (density or 8) + 4)
                if density
                else None,
                melody_direction=direction,
                phrase_position=pos,
                has_dotted_rhythms=True if inject_dotted else None,
                exclude_sources=used_sources[-3:],  # avoid repeating recent sources
                n=5,
            )

            candidates = self.retrieve(query)
            if not candidates:
                # Tier 2: relax textures
                query.rh_texture = None
                query.lh_texture = None
                candidates = self.retrieve(query)
            if not candidates:
                # Tier 3: relax everything except key_mode and time_sig
                query.phrase_position = None
                query.melody_direction = None
                query.has_dotted_rhythms = None
                query.melody_density_range = None
                candidates = self.retrieve(query)
            if not candidates and key_mode == "minor":
                # Tier 4: use major-key material (86% of corpus) —
                # the transposition to minor will adapt the scale
                query.key_mode = "major"
                query.rh_texture = rh_tex  # restore texture preference
                query.lh_texture = lh_tex
                candidates = self.retrieve(query)
            if not candidates:
                # Tier 5: any bar at all
                query.rh_texture = None
                query.lh_texture = None
                query.key_mode = "major"
                candidates = self.retrieve(query)

            if candidates:
                bar = candidates[0]
                adapted = self.transpose_bar(bar, target_key, bar_start + i)

                # Apply dotted rhythm injection for variety
                if inject_dotted and random.random() < 0.4:
                    adapted = self.dotted_inject(adapted)

                # Adjust density if target specified
                if density and adapted.melody_density > 0:
                    if abs(adapted.melody_density - density) > 3:
                        adapted = self.density_adjust(adapted, density, "rh")

                results.append(adapted)
                used_sources.append(bar.get("source", ""))
            else:
                # Empty bar as placeholder
                results.append(
                    AdaptedBar(
                        target_key=target_key,
                        target_bar_num=bar_start + i,
                        source_provenance=["fallback:empty"],
                    )
                )

        return results
