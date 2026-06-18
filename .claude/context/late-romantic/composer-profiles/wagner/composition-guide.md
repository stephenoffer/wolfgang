# Wagner — Composition Guide (Late Romantic Period)

**This is the same composer as romantic/composer-profiles/wagner.**
**See romantic/composer-profiles/wagner/composition-guide.md for the full guide.**

Wagner spans both the Romantic and Late Romantic periods. His stylistic evolution:
- **Early Wagner** (Flying Dutchman, Tannhäuser, Lohengrin): still uses aria/recitative structure, clearer phrases, more conventional harmony. More Romantic than Late Romantic.
- **Middle Wagner** (Tristan und Isolde, Die Meistersinger): mature style — endless melody, Leitmotif system, chromatic saturation. This is the definitive "Wagnerian" sound.
- **Late Wagner** (Ring Cycle, Parsifal): fully developed system, maximum chromatic ambiguity, slowest harmonic rhythm, most complex Leitmotif weaving.

**For composition, use the romantic/wagner/composition-guide.md fingerprints.** The late-romantic classification refers to his historical influence and harmonic language, not a separate set of techniques.

## Additional Late-Period Fingerprints

Beyond the core 5 (see romantic profile), late Wagner also shows:

- **Harmonic stasis** — The Ring and Parsifal often stay on a single chord or harmonic area for 16–32 bars. The static harmony is not lazy — it is overwhelming: the music suspends time.
- **The "Parsifal" sound** — Extremely slow tempo, widely spaced orchestral chords, high strings sustaining above everything, extreme softness (ppp to pp). Used for the sacred/mystical.
- **Leitmotif counterpoint** — Multiple Leitmotifs heard simultaneously in different instruments, at different tempos, with different characters. Not polyphony of melodies — polyphony of symbols.

## ShortScore Field Recommendations

Same as romantic/wagner/composition-guide.md. Additionally:

**Parsifal texture:**
- `"tempo": 52` or slower.
- High strings: sustained chords in 3-part harmony, pppp.
- No rhythmic pulse in any instrument.
- `"expr": "wie Glockenklang"` (like bell-sound) — Wagner's marking in Parsifal.

**Leitmotif counterpoint:**
- Write each Leitmotif as a separate voice layer.
- Document which symbolic meaning each layer carries.
- All layers: simultaneously active, different dynamics.
