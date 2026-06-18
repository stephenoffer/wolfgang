#!/usr/bin/env python3
"""
Style Comparator for Wolfgang v2.

Compares a composed section's metrics against a style-targets.json profile.
Outputs per-metric divergence, pass/fail status, and fix suggestions.

Fix suggestions are STARTING POINTS for the agent — the agent applies musical
judgment for the actual fix. This tool catches gross statistical failures;
subtle quality comes from the agent's qualitative review.

Usage:
    python3 tools/style_comparator.py <composed.musicxml> <style-targets.json> [--threshold 0.35]
"""

import argparse
import json
import sys
from pathlib import Path

from .style_analyzer import analyze_score

# ── Fix instruction templates ──
# Maps metric name + direction to specific WMN-level guidance

FIX_TEMPLATES = {
    "triplet_pct:low": (
        "Increase triplet figuration. Replace straight-eighth or straight-sixteenth "
        "LH arpeggios with triplet-eighth (trip_e) broken chords. Add triplet passing "
        "tones in RH melody at phrase peaks."
    ),
    "events_per_bar:low": (
        "Increase note density. LH needs more events per bar (add flowing figuration). "
        "RH needs more passing tones between structural pitches. Target: {target:.0f} events/bar."
    ),
    "events_per_bar_lh:low": (
        "LH is too sparse. Add flowing accompaniment figuration — triplet arpeggiation, "
        "broken chords, or walking bass. Target: {target:.1f} LH events/bar."
    ),
    "chord_pct:low": (
        "Too few chords. Add dyads/triads: parallel thirds below melody, octave doublings "
        "in climactic passages, sfz chord punctuation in fast sections. Target: {target:.0f}% chords."
    ),
    "leap_pct:low": (
        "Melody too stepwise. Add dramatic register jumps: octave displacements after "
        "phrase peaks, 6th/7th leaps at expressive moments. Target: {target:.0f}% leaps."
    ),
    "rest_ratio:low": (
        "Not enough breathing. Add quarter rests at phrase boundaries (every 4-8 bars). "
        "Add brief rests in LH at cadence points. Music needs silence. Target: {target:.1f}% rests."
    ),
    "rest_ratio:high": (
        "Too many rests — the texture is too fragmented. Fill in some gaps with sustained "
        "notes or ties. Target: {target:.1f}% rests."
    ),
    "phrase_length_avg:high": (
        "Phrases too long — no breathing room. Add rests between phrases. "
        "Target average phrase: {target:.0f} beats."
    ),
    "phrase_length_avg:low": (
        "Phrases too short — too fragmented. Extend melodic lines, use fewer rests mid-phrase. "
        "Target average phrase: {target:.0f} beats."
    ),
    "bass_change_rate:high": (
        "Bass changes pitch too rapidly. Use pedal tones: hold the root for 1-2 beats, "
        "oscillate between 2-3 chord tones above it. Reserve bass-note changes for "
        "harmonic changes (every 1-2 bars). Target: {target:.1f} changes/bar."
    ),
    "suspension_pct:low": (
        "No suspensions. Add tied notes across barlines: hold a melody note into the "
        "next chord where it becomes a dissonance, then resolve down by step. "
        "Use 4-3 and 7-6 suspensions at cadences. Target: {target:.1f}%."
    ),
    "parallel_motion_pct:high": (
        "Too much parallel motion between hands. Move the bass in the OPPOSITE direction "
        "from the melody at cadence points (contrary motion). Use oblique motion "
        "(one hand holds while the other moves). Target: {target:.0f}% parallel."
    ),
    "identical_consecutive_pct:high": (
        "Too many identical consecutive bars. Vary the rhythmic profile every 2-4 bars: "
        "change accompaniment pattern, add/remove ornaments, shift dynamics, insert rests. "
        "Target: {target:.0f}% identical."
    ),
    "rhythmic_variety:low": (
        "Not enough rhythmic variety. Add 32nd notes (ornamental turns), dotted-eighth + "
        "sixteenth pairs, triplet quarters. Target: {target:.0f} different duration types."
    ),
    "chromatic_pct:high": (
        "Too chromatic. Reduce accidentals — use more diatonic scale tones. Reserve "
        "chromaticism for expressive moments (passing tones, modal mixture). Target: {target:.0f}%."
    ),
    "chromatic_pct:low": (
        "Too diatonic. Add chromatic color: secondary dominants, modal mixture (bVI, iv), "
        "chromatic passing tones. Target: {target:.0f}%."
    ),
    "dynamic_markings_per_bar:low": (
        "Not enough dynamic markings. Add p/f/ff/pp at phrase boundaries. Add sf/sfp on "
        "off-beats at moments of harmonic surprise. Target: {target:.2f} markings/bar."
    ),
    "sf_density:low": (
        "Not enough sforzandi. Add sf on off-beats (beat 2/3) at surprise harmonies, "
        "fp at deceptive cadences, sfp at subito-piano moments. Target: {target:.2f}/bar."
    ),
    # ── Harmonic rhythm ──
    "harmonic_rhythm_avg:high": (
        "Chords change too slowly — harmonic rhythm is sluggish. Increase harmonic motion, "
        "especially approaching cadences. Add passing chords or secondary dominants between "
        "structural pillars. Real composers accelerate harmonic rhythm at climactic moments."
    ),
    "harmonic_rhythm_avg:low": (
        "Chords change too rapidly — no harmonic stability. Sustain harmonies longer, "
        "especially at phrase openings and after cadences. Let the listener settle into a key "
        "before moving. Use pedal tones to anchor fast-moving upper voices."
    ),
    "harmonic_rhythm_cv:low": (
        "Harmonic rhythm is too regular — same rate of chord change throughout. Real music "
        "accelerates harmonic rhythm approaching cadences and slows it during lyrical passages. "
        "Vary the rate: hold chords for 2-4 bars in calm moments, change every beat at climaxes."
    ),
    # ── Cadence tracking ──
    "cadence_frequency:high": (
        "Too many cadences — every phrase closes definitively. Allow some phrases to elide "
        "(overlap) or use half cadences to keep momentum. Not every phrase needs a full stop."
    ),
    "cadence_frequency:low": (
        "Too few cadences — phrases run on without punctuation. Add clear cadential arrivals "
        "at phrase boundaries. The listener needs periodic harmonic resolution to feel structure."
    ),
    "deceptive_cadence_pct:low": (
        "No deceptive cadences — every cadence resolves as expected. Add V→vi (or V→bVI) at "
        "one or two structurally significant moments for harmonic surprise. Deceptive cadences "
        "are one of the most powerful tools for maintaining listener engagement."
    ),
    "half_cadence_pct:low": (
        "No half cadences — every phrase resolves to tonic. Use half cadences (ending on V) "
        "at antecedent phrase endings to create the question-answer structure fundamental to "
        "tonal music."
    ),
    # ── Voice independence ──
    "voice_independence_score:low": (
        "Voices move too much in parallel — they sound like one thickened line, not independent "
        "voices. Add contrary motion (bass descends when melody ascends) at cadences and phrase "
        "peaks. Add oblique motion (one voice holds while others move) during sustained melody notes."
    ),
    "voice_independence_score:high": (
        "Voices are extremely independent — verify this is intentional (e.g., fugal writing). "
        "If not, some parallel motion at structural arrivals provides stability and weight."
    ),
    # ── Articulation ──
    "staccato_pct:high": (
        "Too much staccato — the music sounds choppy and disconnected. Add legato slurs over "
        "melodic phrases. Reserve staccato for specific effects (playful passages, rhythmic "
        "punctuation), not as default articulation."
    ),
    "staccato_pct:low": (
        "Very little staccato — check if the style calls for more articulated passages. Many "
        "Classical and Baroque styles use staccato for lightness and rhythmic clarity."
    ),
    "legato_span_avg:low": (
        "Legato spans are very short — melody sounds fragmented. Add longer slurs over melodic "
        "phrases (4-8 notes). Singing melodies need connected phrasing."
    ),
    "legato_span_avg:high": (
        "Very long legato spans — check if the style calls for more articulated phrasing. Even "
        "Romantic music has phrase breaks and breathing points."
    ),
    "articulation_variety:low": (
        "Very few articulation types used — the music lacks textural variety. Add tenuto on "
        "expressive notes, accents on rhythmic highlights, staccato for contrast. Real scores "
        "use 4-6 different articulation types."
    ),
    # ── Modulation ──
    "modulations_per_section:high": (
        "Too many modulations — tonal instability. Establish each key area for at least 4-8 bars "
        "before modulating. Frequent key changes prevent the listener from feeling grounded."
    ),
    "modulations_per_section:low": (
        "No modulations — the music stays in one key throughout. Add at least one modulation to "
        "a related key (dominant, relative major/minor) at a structurally appropriate point."
    ),
    "tonal_stability:low": (
        "Low tonal stability — the detected key changes frequently even within phrases. Strengthen "
        "key establishment with clear tonic arrivals and dominant-tonic cadences. Use diatonic "
        "chords more at phrase openings."
    ),
    "tonal_stability:high": (
        "Very high tonal stability — the music rarely leaves the home key. For sections longer "
        "than 16 bars, explore related keys to create harmonic journey and contrast."
    ),
    # ── Chord quality ──
    "major_chord_pct:high": (
        "Disproportionately many major chords — check for missing minor chords where the style "
        "expects them. Minor modes and modal mixture add depth."
    ),
    "major_chord_pct:low": (
        "Very few major chords — if the piece is in a major key, ensure tonic and dominant are "
        "clearly major. The brightness of major chords is essential for tonal orientation."
    ),
    "minor_chord_pct:low": (
        "Very few minor chords — even major-key music uses ii, iii, vi regularly. Minor chords "
        "provide warmth and shadow. Add supertonic (ii) and submediant (vi) chords."
    ),
    "dim_chord_pct:low": (
        "No diminished chords — missing viio (leading tone chord) and diminished 7ths. These "
        "create essential tension at cadences and in sequences. Add viio6 or viio7 before tonic "
        "arrivals."
    ),
    "dom7_chord_pct:low": (
        "No dominant 7th chords — missing the primary tension-resolution mechanism in tonal music. "
        "Add V7 at cadences and phrase boundaries for stronger harmonic pull."
    ),
    # ── Voicing smoothness ──
    "voice_leading_distance_avg:high": (
        "Voice leading is too jumpy — large leaps between consecutive chords. Use common tones "
        "(keep shared pitches in the same voice), stepwise motion in inner voices, and proper "
        "voice-leading rules. The smoothest chord connections move each voice by the smallest "
        "possible interval."
    ),
    "voice_leading_distance_avg:low": (
        "Voice leading is extremely smooth — verify this matches the style. Some dramatic styles "
        "(late Romantic, modern) use wider voice leading for expressive effect."
    ),
    "voice_leading_distance_max:high": (
        "Extreme voice-leading jumps detected — likely a chord inversion or register change that "
        "could be smoother. Check the specific passage and consider using a different inversion "
        "to reduce total voice movement."
    ),
}


def compare(composed_metrics: dict, targets: dict, threshold: float = 0.35) -> dict:
    """Compare composed metrics against targets.

    Returns a comparison report with per-metric results.
    """
    report = {
        "composed_file": composed_metrics.get("file", "?"),
        "threshold": threshold,
        "metrics": {},
        "passing": 0,
        "failing": 0,
        "warnings": 0,
    }

    for key, target_info in targets.items():
        if key not in composed_metrics:
            continue
        if not isinstance(target_info, dict) or "mean" not in target_info:
            continue

        composed_val = composed_metrics[key]
        if not isinstance(composed_val, (int, float)):
            continue

        target_mean = target_info["mean"]
        target_stdev = target_info.get("stdev", 0)

        # Calculate divergence
        if abs(target_mean) < 0.01:
            divergence = abs(composed_val) * 100 if composed_val != 0 else 0
        else:
            divergence = abs(composed_val - target_mean) / abs(target_mean)

        # Status based on threshold
        if divergence <= threshold:
            status = "PASS"
            report["passing"] += 1
        elif divergence <= threshold * 2:
            status = "WARNING"
            report["warnings"] += 1
        else:
            status = "FAIL"
            report["failing"] += 1

        # Generate fix instruction
        direction = "high" if composed_val > target_mean else "low"
        template_key = f"{key}:{direction}"
        fix = FIX_TEMPLATES.get(template_key, f"Adjust {key} toward target ({target_mean:.1f}).")
        if isinstance(fix, str) and "{target" in fix:
            fix = fix.format(target=target_mean)

        report["metrics"][key] = {
            "composed": round(composed_val, 2),
            "target_mean": round(target_mean, 2),
            "target_stdev": round(target_stdev, 2),
            "divergence_pct": round(divergence * 100, 1),
            "status": status,
            "fix_instruction": fix if status != "PASS" else None,
        }

    total = report["passing"] + report["failing"] + report["warnings"]
    report["overall_score"] = round(report["passing"] / max(total, 1), 2)

    return report


def main():
    parser = argparse.ArgumentParser(description="Style Comparator for Wolfgang v2")
    parser.add_argument("composed", help="Composed MusicXML file to compare")
    parser.add_argument("targets", help="Style targets JSON file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.35,
        help="Divergence threshold for pass/fail (default: 0.35 = 35%%)",
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    # Analyze composed file
    composed_metrics = analyze_score(args.composed)
    if composed_metrics is None:
        print(f"ERROR: Could not analyze {args.composed}", file=sys.stderr)
        sys.exit(1)

    # Load targets
    targets_data = json.loads(Path(args.targets).read_text())
    targets = targets_data.get("targets", targets_data)

    # Compare
    report = compare(composed_metrics, targets, args.threshold)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"\nStyle Comparison: {report['composed_file']}")
        print(f"{'─' * 70}")
        print(
            f"  Overall: {report['passing']} pass, {report['warnings']} warn, {report['failing']} fail "
            f"(score: {report['overall_score']:.0%})"
        )
        print()
        for key, info in sorted(report["metrics"].items(), key=lambda x: -x[1]["divergence_pct"]):
            icon = (
                "✓" if info["status"] == "PASS" else ("△" if info["status"] == "WARNING" else "✗")
            )
            line = f"  {icon} {key:<30} composed={info['composed']:>8}  target={info['target_mean']:>8}  (±{info['divergence_pct']:.0f}%)"
            print(line)
            if info["fix_instruction"]:
                # Wrap fix instruction
                fix = info["fix_instruction"]
                print(f"    → {fix[:90]}")
        print()

    sys.exit(0 if report["failing"] == 0 else 1)


if __name__ == "__main__":
    main()
