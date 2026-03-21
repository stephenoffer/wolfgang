# Section Review Checklist

## Priority Levels
- **CRITICAL**: Must fix before approval. Invalid ABC that won't convert.
- **HIGH**: Must fix. Musical errors that are clearly audible.
- **MEDIUM**: Fix if possible. Issues that affect quality but aren't errors.
- **LOW**: Note for awareness. Subjective improvements.

## A. Notation (CRITICAL)

| Check | How to Verify |
|-------|---------------|
| Measure durations correct | Sum note durations per measure = time signature |
| All declared voices present | Every V: in header has [V:name] lines in body |
| Barlines aligned | Same number of barlines in each voice |
| Valid note names | Only A-G, a-g with optional ^_= and ,' |
| Valid ABC syntax | No unmatched brackets, valid repeat signs |

## B. Voice Leading (HIGH)

| Error | Detection | Fix |
|-------|-----------|-----|
| Parallel 5ths | Two voices move by the same interval and are a 5th apart | Change inner voice by step |
| Parallel octaves | Two voices move in same direction, staying an octave apart | Change direction of one voice |
| Parallel unisons | Two voices on same note move to same note | Vary one voice |
| Unresolved leading tone | 7th scale degree doesn't go to tonic | Move to tonic |
| Unresolved 7th | Chord 7th doesn't step down | Step down |
| Augmented melodic interval | Aug 2nd, Aug 4th in a melody | Fill in with passing tone or use different note |
| Voice crossing | Lower voice goes above higher voice | Swap or re-voice |

## C. Range Violations (HIGH)

| Instrument | Lowest | Highest | If Violated |
|-----------|--------|---------|-------------|
| Violin | G,3 | e'''7 | Rarely an issue; check extreme high |
| Viola | C,3 | e''6 | Watch for going below C3 |
| Cello | C,,2 | a'5 | Watch high passages |
| Contrabass | E,,1 | g4 | Very limited upper range |
| Flute | c'4 | d'''7 | No notes below middle C |
| Oboe | B,3 | a''6 | Watch low register |
| Clarinet Bb | D3 written | b''6 written | Written pitch, not concert |
| Bassoon | B,,1 | e'5 | Check extreme high |
| Horn F | B,,1 written | f''5 written | Written pitch |
| Trumpet Bb | E3 written | b'5 written | Written pitch |
| Trombone | E,,2 | b4 | Limited high range |
| Tuba | D,,1 | f4 | Very limited high |
| Timpani | C,,2 | c4 | Usually just 2-4 notes |
| Piano | A,,,0 | c''''8 | Almost never violated |

## D. Theme Verification (HIGH)

| Check | How to Verify |
|-------|---------------|
| Theme present | Find the interval pattern from themes.json in the composed voice |
| Correct transformation | If inversion: intervals are reversed. If augmentation: durations doubled |
| Connecting motif present | If usage_plan includes it for this section |
| Theme in correct voice | Theme should be in the melody voice per orchestration plan |

## E. Harmonic (MEDIUM)

| Check | How to Verify |
|-------|---------------|
| Chord matches plan | Vertical sonority at each beat matches harmony plan |
| Modulation correct | Key change occurs at planned measure |
| Cadence type correct | Final chord progression matches planned cadence |

## F. Expression (MEDIUM)

| Check | How to Verify |
|-------|---------------|
| Dynamics present | At least one dynamic marking per 8 measures |
| Dynamic arc sensible | Matches narrative intensity target |
| Articulations present | Appropriate for style and character |
| Tempo marking | Present at start of section if tempo changes |
