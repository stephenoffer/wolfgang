#!/usr/bin/env python3
"""
Migration script: convert flat per-composer pattern files into the
content-addressed canonical pattern library.

Reads existing tools/pattern_library/{mozart,beethoven,chopin}/patterns.json,
deduplicates by content hash, builds sharded canonical store + all indices.
"""

import hashlib
import json
import os
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # tools/
LIB_DIR = BASE / "pattern_library"
REF_DIR = BASE / "reference_index"

COMPOSERS_BY_GENRE = {
    "baroque": ["bach", "handel", "vivaldi"],
    "classical": ["beethoven", "haydn", "mozart"],
    "romantic": [
        "brahms",
        "chopin",
        "liszt",
        "mendelssohn",
        "rachmaninoff",
        "schubert",
        "schumann",
        "tchaikovsky",
        "wagner",
    ],
    "late-romantic": ["bruckner", "elgar", "mahler", "strauss-r"],
    "impressionist": ["debussy", "faure", "ravel", "satie"],
    "nationalistic": ["dvorak", "grieg", "mussorgsky", "rimsky-korsakov", "sibelius", "smetana"],
    "modern": [
        "bartok",
        "copland",
        "messiaen",
        "prokofiev",
        "schoenberg",
        "shostakovich",
        "stravinsky",
        "webern",
    ],
    "minimalist": ["arvo-part", "glass", "reich"],
    "film-score": ["morricone", "williams", "zimmer"],
}

COMPOSER_TO_GENRE = {}
for genre, composers in COMPOSERS_BY_GENRE.items():
    for c in composers:
        COMPOSER_TO_GENRE[c] = genre


def compute_hash(lh_events):
    """Deterministic content hash from LH events."""
    # Normalize: sort keys, round durations to avoid float noise
    normalized = []
    for e in lh_events:
        ne = {}
        p = e.get("p", "rest")
        ne["p"] = p if isinstance(p, str) else sorted(p) if isinstance(p, list) else str(p)
        ne["d"] = round(float(e.get("d", 0)), 4)
        normalized.append(ne)
    raw = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def shard_name(h):
    """Map hash to shard file name (first hex char → 16 shards)."""
    return f"shard_{h[0]}.json"


def load_old_patterns(composer):
    """Load existing flat patterns.json for a composer."""
    path = LIB_DIR / composer / "patterns.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def load_transition_matrix(composer):
    """Load existing transition matrix from old index."""
    idx_path = LIB_DIR / "index.json"
    if not idx_path.exists():
        return None
    with open(idx_path) as f:
        idx = json.load(f)
    matrices = idx.get("transition_matrices", {})
    return matrices.get(composer)


def build_bar_transitions(composer):
    """Build transition matrix from the bar_index directly."""
    bar_path = REF_DIR / f"{composer}_bar_index.json"
    if not bar_path.exists():
        return None
    with open(bar_path) as f:
        data = json.load(f)
    bars = data.get("bars", data) if isinstance(data, dict) else data

    counts = defaultdict(lambda: defaultdict(int))
    prev_tex = None
    prev_source = None
    total = 0

    for b in bars:
        source = b.get("source", "")
        tex = b.get("lh_texture", "unknown")
        if source == prev_source and prev_tex is not None:
            counts[prev_tex][tex] += 1
            total += 1
        prev_tex = tex
        prev_source = source

    self_cont = {}
    for tex, nexts in counts.items():
        t = sum(nexts.values())
        if t > 0:
            self_cont[tex] = round(nexts.get(tex, 0) / t, 4)

    return {
        "counts": {k: dict(v) for k, v in counts.items()},
        "self_continuation": self_cont,
        "total_transitions": total,
    }


def merge_transition_matrices(matrices, weights):
    """Merge multiple transition matrices weighted by bar count."""
    merged_counts = defaultdict(lambda: defaultdict(float))
    total_weight = sum(weights)

    for matrix, weight in zip(matrices, weights):
        if not matrix:
            continue
        w = weight / total_weight
        for from_tex, to_dict in matrix.get("counts", {}).items():
            for to_tex, count in to_dict.items():
                merged_counts[from_tex][to_tex] += count * w

    # Normalize to integers
    counts = {k: {k2: int(round(v2)) for k2, v2 in v.items()} for k, v in merged_counts.items()}
    total = sum(sum(v.values()) for v in counts.values())

    self_cont = {}
    for tex, nexts in counts.items():
        t = sum(nexts.values())
        if t > 0:
            self_cont[tex] = round(nexts.get(tex, 0) / t, 4)

    return {
        "counts": counts,
        "self_continuation": self_cont,
        "total_transitions": total,
    }


def main():
    print("=== Pattern Library Migration ===\n")

    # Phase 1: Load all existing patterns
    all_patterns = {}  # old_id -> old_pattern_dict
    for composer in ["mozart", "beethoven", "chopin"]:
        patterns = load_old_patterns(composer)
        print(f"Loaded {len(patterns)} patterns from {composer}")
        for pid, p in patterns.items():
            p["_old_id"] = pid
            p["_genre"] = COMPOSER_TO_GENRE.get(p.get("composer", ""), "classical")
            all_patterns[pid] = p

    print(f"\nTotal old patterns: {len(all_patterns)}")

    # Phase 2: Deduplicate by content hash
    canonical = {}  # hash -> canonical pattern dict
    cross_ref = defaultdict(list)  # hash -> [attributions]
    hash_to_old = defaultdict(list)  # hash -> [old_ids]

    for old_id, p in all_patterns.items():
        lh_events = p.get("lh_events", [])
        if not lh_events:
            continue

        h = compute_hash(lh_events)
        hash_to_old[h].append(old_id)

        composer = p.get("composer", "")
        genre = p.get("_genre", "classical")

        # Update canonical pattern
        if h not in canonical:
            canonical[h] = {
                "hash": h,
                "lh_events": lh_events,
                "lh_texture": p.get("lh_texture", ""),
                "lh_density": p.get("lh_density", 0),
                "event_count": len(lh_events),
                "duration_total": round(
                    sum(
                        float(e.get("d", 0)) if isinstance(e.get("d"), (int, float)) else 0
                        for e in lh_events
                    ),
                    2,
                ),
                "genres": set(),
                "total_occurrences": 0,
                "composer_count": 0,
                "_composers_seen": set(),
            }
        cp = canonical[h]
        cp["genres"].add(genre)
        cp["total_occurrences"] += p.get("frequency", 1)
        cp["_composers_seen"].add(composer)

        # Build attribution
        found = False
        for attr in cross_ref[h]:
            if attr["composer"] == composer:
                attr["frequency"] += p.get("frequency", 1)
                attr["sources"].append(p.get("source", ""))
                pp = p.get("phrase_position", "middle")
                attr["phrase_positions"][pp] = attr["phrase_positions"].get(pp, 0) + 1
                rh = p.get("rh_texture", "")
                if rh:
                    attr["rh_textures_paired"][rh] = attr["rh_textures_paired"].get(rh, 0) + 1
                found = True
                break

        if not found:
            cross_ref[h].append(
                {
                    "composer": composer,
                    "genre": genre,
                    "frequency": p.get("frequency", 1),
                    "sources": [p.get("source", "")][:10],
                    "phrase_positions": {p.get("phrase_position", "middle"): 1},
                    "rh_textures_paired": {p.get("rh_texture", ""): 1}
                    if p.get("rh_texture")
                    else {},
                    "key_modes": {p.get("key_mode", "major"): 1},
                }
            )

    # Finalize canonical patterns
    for h, cp in canonical.items():
        cp["genres"] = sorted(cp["genres"])
        cp["composer_count"] = len(cp["_composers_seen"])
        del cp["_composers_seen"]

    print(f"Unique patterns (by content hash): {len(canonical)}")
    print(
        f"Deduplication: {len(all_patterns)} -> {len(canonical)} "
        f"({100 * (1 - len(canonical) / len(all_patterns)):.1f}% reduction)"
    )

    # Phase 3: Shard canonical patterns
    shards = defaultdict(dict)
    for h, cp in canonical.items():
        sn = shard_name(h)
        shards[sn][h] = cp

    canonical_dir = LIB_DIR / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    for sn, patterns in shards.items():
        with open(canonical_dir / sn, "w") as f:
            json.dump(patterns, f, separators=(",", ":"))

    print(f"\nShards written: {len(shards)}")
    for sn in sorted(shards):
        size = os.path.getsize(canonical_dir / sn)
        print(f"  {sn}: {len(shards[sn])} patterns ({size / 1024:.0f} KB)")

    # Phase 4: Build indices
    index_dir = LIB_DIR / "index"
    index_dir.mkdir(parents=True, exist_ok=True)

    # master.json
    master = {
        "version": 2,
        "total_unique_patterns": len(canonical),
        "total_occurrences": sum(cp["total_occurrences"] for cp in canonical.values()),
        "shard_count": len(shards),
        "entries": {
            h: {
                "shard": shard_name(h),
                "lh_texture": cp["lh_texture"],
                "genres": cp["genres"],
                "composer_count": cp["composer_count"],
                "total_freq": cp["total_occurrences"],
            }
            for h, cp in canonical.items()
        },
    }
    with open(index_dir / "master.json", "w") as f:
        json.dump(master, f, separators=(",", ":"))
    print(f"\nmaster.json: {os.path.getsize(index_dir / 'master.json') / 1024:.0f} KB")

    # by_texture.json
    by_texture = defaultdict(list)
    for h, cp in canonical.items():
        by_texture[cp["lh_texture"]].append(h)
    with open(index_dir / "by_texture.json", "w") as f:
        json.dump(dict(by_texture), f, separators=(",", ":"))

    # by_genre.json
    by_genre = defaultdict(list)
    for h, cp in canonical.items():
        for g in cp["genres"]:
            by_genre[g].append(h)
    with open(index_dir / "by_genre.json", "w") as f:
        json.dump(dict(by_genre), f, separators=(",", ":"))

    # by_composer.json
    by_composer = defaultdict(list)
    for h, attrs in cross_ref.items():
        for attr in attrs:
            by_composer[attr["composer"]].append(
                {
                    "hash": h,
                    "frequency": attr["frequency"],
                }
            )
    with open(index_dir / "by_composer.json", "w") as f:
        json.dump(dict(by_composer), f, separators=(",", ":"))

    # cross_reference.json
    # Trim sources to max 5 per attribution
    xref_out = {}
    for h, attrs in cross_ref.items():
        xref_out[h] = []
        for a in attrs:
            a_out = dict(a)
            a_out["sources"] = a_out["sources"][:5]
            xref_out[h].append(a_out)
    with open(index_dir / "cross_reference.json", "w") as f:
        json.dump(xref_out, f, separators=(",", ":"))

    # shared_patterns.json
    shared = {h: xref_out[h] for h in xref_out if len(xref_out[h]) > 1}
    with open(index_dir / "shared_patterns.json", "w") as f:
        json.dump(shared, f, separators=(",", ":"))
    print(f"Shared patterns (2+ composers): {len(shared)}")

    for fn in [
        "by_texture.json",
        "by_genre.json",
        "by_composer.json",
        "cross_reference.json",
        "shared_patterns.json",
    ]:
        size = os.path.getsize(index_dir / fn)
        print(f"  {fn}: {size / 1024:.0f} KB")

    # Phase 5: Transition matrices
    trans_dir = LIB_DIR / "transitions"

    # Per-composer
    composer_matrices = {}
    for composer in ["mozart", "beethoven", "chopin"]:
        matrix = build_bar_transitions(composer)
        if matrix:
            composer_matrices[composer] = matrix
            with open(trans_dir / "by_composer" / f"{composer}.json", "w") as f:
                json.dump(matrix, f, indent=2)
            print(f"\n{composer} transitions: {matrix['total_transitions']}")

    # Genre-level: classical = mozart + beethoven
    genre_matrices = {}
    m_mat = composer_matrices.get("mozart")
    b_mat = composer_matrices.get("beethoven")
    c_mat = composer_matrices.get("chopin")

    if m_mat and b_mat:
        classical = merge_transition_matrices([m_mat, b_mat], [6987, 16856])
        classical["source_composers"] = ["mozart", "beethoven"]
        classical["genre"] = "classical"
        genre_matrices["classical"] = classical
        with open(trans_dir / "by_genre" / "classical.json", "w") as f:
            json.dump(classical, f, indent=2)
        print(f"\nClassical genre matrix: {classical['total_transitions']} transitions")

    if c_mat:
        romantic = dict(c_mat)
        romantic["source_composers"] = ["chopin"]
        romantic["genre"] = "romantic"
        genre_matrices["romantic"] = romantic
        with open(trans_dir / "by_genre" / "romantic.json", "w") as f:
            json.dump(romantic, f, indent=2)

    # Synthesize matrices for genres without corpus data
    # Use classical as base, adjust weights
    if classical:
        adjustments = {
            "baroque": {
                "alberti": 0.3,
                "bass_melody": 1.5,
                "pedal_point": 1.5,
                "walking_bass": 1.3,
            },
            "late-romantic": {
                "alberti": 0.7,
                "pedal_point": 1.5,
                "bass_melody": 1.3,
                "block_chord_sparse": 1.2,
            },
            "impressionist": {
                "alberti": 0.2,
                "pedal_point": 2.0,
                "broken_chord_wave": 2.0,
                "silence": 1.5,
            },
            "nationalistic": {
                "alberti": 0.8,
                "bass_melody": 1.2,
                "walking_bass": 1.3,
                "pedal_point": 1.2,
            },
            "modern": {
                "alberti": 0.1,
                "block_chord_sparse": 1.5,
                "silence": 2.0,
                "bass_melody": 1.3,
            },
            "minimalist": {
                "alberti": 0.1,
                "pedal_point": 3.0,
                "oscillation_trill": 2.0,
                "broken_chord_wave": 2.0,
            },
            "film-score": {
                "alberti": 0.5,
                "pedal_point": 2.0,
                "block_chord_sparse": 1.5,
                "bass_melody": 1.3,
            },
        }

        for genre, adj in adjustments.items():
            synth = {
                "counts": {},
                "self_continuation": {},
                "total_transitions": 0,
                "synthetic": True,
                "based_on": "classical",
                "genre": genre,
            }
            for from_tex, to_dict in classical["counts"].items():
                synth["counts"][from_tex] = {}
                for to_tex, count in to_dict.items():
                    factor = adj.get(to_tex, 1.0)
                    synth["counts"][from_tex][to_tex] = max(1, int(round(count * factor)))
            # Recompute self-continuation
            for tex, nexts in synth["counts"].items():
                total = sum(nexts.values())
                synth["total_transitions"] += total
                if total > 0:
                    synth["self_continuation"][tex] = round(nexts.get(tex, 0) / total, 4)

            genre_matrices[genre] = synth
            with open(trans_dir / "by_genre" / f"{genre}.json", "w") as f:
                json.dump(synth, f, indent=2)

    print(f"\nGenre matrices: {list(genre_matrices.keys())}")

    # Phase 6: Composer registry
    registry = {}
    for genre, composers in COMPOSERS_BY_GENRE.items():
        for c in composers:
            has_corpus = c in composer_matrices
            registry[c] = {
                "genre": genre,
                "has_corpus": has_corpus,
                "pattern_count": len(by_composer.get(c, [])),
                "transition_source": "composer" if has_corpus else "genre",
                "inherits_from": genre if not has_corpus else None,
            }

    with open(LIB_DIR / "composer_registry.json", "w") as f:
        json.dump(registry, f, indent=2)
    print(f"\nComposer registry: {len(registry)} composers")

    # Phase 7: Clean up old files
    for composer in ["mozart", "beethoven", "chopin"]:
        old_path = LIB_DIR / composer / "patterns.json"
        if old_path.exists():
            old_path.unlink()
            print(f"Removed old {old_path}")
        old_dir = LIB_DIR / composer
        if old_dir.exists() and not list(old_dir.iterdir()):
            old_dir.rmdir()
            print(f"Removed empty {old_dir}")
    old_index = LIB_DIR / "index.json"
    if old_index.exists():
        old_index.unlink()
        print("Removed old index.json")

    # Final report
    total_disk = sum(
        os.path.getsize(os.path.join(dp, f)) for dp, dn, fn in os.walk(LIB_DIR) for f in fn
    )
    print("\n=== MIGRATION COMPLETE ===")
    print(f"Unique patterns: {len(canonical)}")
    print(f"Total occurrences covered: {sum(cp['total_occurrences'] for cp in canonical.values())}")
    print(f"Shared across composers: {len(shared)}")
    print(f"Shards: {len(shards)}")
    print(f"Genre matrices: {len(genre_matrices)}")
    print(f"Composers in registry: {len(registry)}")
    print(f"Total disk: {total_disk / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
