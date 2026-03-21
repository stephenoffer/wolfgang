# Musical Form Templates Reference

## Sonata Form

### Standard Layout
| Section | Subsection | ID | Key (Major) | Key (Minor) | Function |
|---|---|---|---|---|---|
| **Exposition** | Primary Theme (PT) | m1_expo_pt | I | i | Main theme, establishes tonic |
| | Transition (TR) | m1_expo_tr | I -> V | i -> III | Modulates, increases energy |
| | Secondary Theme (ST) | m1_expo_st | V | III (or v) | Contrasting theme, new key |
| | Closing (CL) | m1_expo_cl | V | III | Cadential, confirms new key |
| **Development** | Dev. phase 1 | m1_dev_1 | Unstable | Unstable | Fragments PT, explores keys |
| | Dev. phase 2 | m1_dev_2 | Unstable | Unstable | Climax, retransition to tonic |
| **Recapitulation** | Primary Theme | m1_recap_pt | I | i | PT returns in tonic |
| | Transition | m1_recap_tr | I -> I | i -> i | Modified, stays in tonic |
| | Secondary Theme | m1_recap_st | I | I (or i) | ST now in tonic |
| | Closing | m1_recap_cl | I | i | Final confirmation of tonic |
| **Coda** | Coda | m1_coda | I | i | Optional, final summation |

### Key Relationships in Development
Common key areas visited during development:
- Start: key of ST end (V or III)
- Middle: remote keys (vi, ii, bVI, bIII, iv)
- Retransition: dominant pedal returning to I

### ABC Section Structure
```abc
% Sonata form skeleton
% Exposition
[V:Vln1] [K:C] "PT"C4 | ... |"TR" ... | [K:G] "ST"G4 | ... |"CL" ... ||
% Development
[K:Am] "Dev1" ... | [K:F] ... | [K:Dm] "Dev2" ... | "Retrans" ... ||
% Recapitulation
[K:C] "PT"C4 | ... |"TR" ... |"ST"C4 | ... |"CL" ... ||"Coda" ... |]
```

## Sonata-Rondo Form

| Section | Key | Function | Relation |
|---|---|---|---|
| A (Refrain) | I | Main theme | Rondo element |
| B (Episode 1) | V or III | Contrasting, like ST | Sonata element |
| A (Refrain) | I | Return of main theme | Rondo element |
| C (Development) | Unstable | Development of A/B material | Sonata element |
| A (Refrain) | I | Return | Rondo element |
| B (Episode 1) | I | B now in tonic (recap) | Sonata element |
| A (Refrain) + Coda | I | Final statement | Both |

**Common in:** Final movements of Classical concertos and symphonies (Mozart, Beethoven).

## Rondo Forms

### Five-Part Rondo (ABACA)
| Section | Key | Character |
|---|---|---|
| A (Refrain) | I | Main theme, memorable, returns verbatim or varied |
| B (Episode 1) | V or vi | Contrasting character |
| A (Refrain) | I | Return (may be shortened) |
| C (Episode 2) | IV or ii or vi | Most contrasting, new material |
| A (Refrain) + Coda | I | Final statement, possibly extended |

### Seven-Part Rondo (ABACABA)
| Section | Key | Notes |
|---|---|---|
| A | I | Main theme |
| B | V | First contrast |
| A | I | Return |
| C | Remote | Greatest contrast |
| A | I | Return |
| B | I | Now in tonic |
| A + Coda | I | Final, extended |

## Theme and Variations

| Section | ID | Key | Character |
|---|---|---|---|
| Theme | m_theme | I | Simple, clear, memorable melody 8-32 bars |
| Var. 1 | m_var1 | I | Ornamental — melody decorated, rhythm preserved |
| Var. 2 | m_var2 | I | Rhythmic — new rhythmic pattern, harmony preserved |
| Var. 3 | m_var3 | i/I | Mode change — major to minor or reverse |
| Var. 4 | m_var4 | I | Textural — new accompaniment, different voicing |
| Var. 5 | m_var5 | I | Character — tempo change (slow or fast) |
| Var. n | m_varn | I | Virtuosic or climactic |
| Finale | m_finale | I | Coda, fugue, or return to theme |

**Variation techniques:** Melodic ornamentation, rhythmic diminution/augmentation, mode change, re-harmonization, contrapuntal treatment, tempo change, orchestral re-coloring, fragmentation, character transformation.

## Ternary Form

### Simple Ternary (ABA)
| Section | Key | Character |
|---|---|---|
| A | I | Main idea, complete in itself |
| B | V, vi, IV, or relative | Contrasting middle, new material |
| A | I | Return, exact or with minor changes |

### Modified Ternary (ABA')
| Section | Key | Notes |
|---|---|---|
| A | I | Main idea |
| B | Contrasting | Middle section |
| A' | I | Return with modifications: ornamented, extended, re-scored |

**Common in:** Slow movements, character pieces, arias, song forms.

## Binary Form

### Simple Binary (AB)
| Section | Key | Notes |
|---|---|---|
| A | I -> V (or III) | Opens in tonic, modulates, ends in new key |
| B | V -> I | Begins in new key, returns to tonic |

### Rounded Binary (||:A:||:BA':||)
| Section | Key | Notes |
|---|---|---|
| A | I -> V | Repeatable, modulates |
| B | Unstable | Contrasting or developmental |
| A' | I | Return of opening, stays in tonic |

**Common in:** Baroque dance movements, Classical minuets/trios, theme statements.

## Scherzo and Trio

| Section | ID | Key | Tempo/Character |
|---|---|---|---|
| Scherzo A | m_sch_a | I | Fast, energetic, rhythmic, often 3/4 |
| Scherzo B | m_sch_b | Contrasting | Developmental or contrasting |
| Scherzo A | m_sch_a | I | Return (may abbreviate) |
| Trio A | m_trio_a | IV, vi, or I | Contrasting character, often lyrical, lighter |
| Trio B | m_trio_b | Contrasting | Middle of trio |
| Trio A | m_trio_a | Trio key | Return |
| Scherzo da capo | m_sch_a, _b, _a | I | Exact repeat (often without internal repeats) |
| Coda | m_sch_coda | I | Optional, may recall trio |

## Through-Composed

No repeating sections. Each section presents new or substantially transformed material.

| Approach | Description | Example Use |
|---|---|---|
| Narrative arc | Sections follow a story | Symphonic poem, tone poem |
| Continuous development | Material evolves without return | Strauss, Wagner |
| Section chain | Distinct contrasting sections | Fantasy, rhapsody |

**Section planning:** Define a sequence of emotional/dramatic states. Each section flows into the next. Use motivic connections to maintain coherence.

## Concerto Forms

### Concerto First Movement (Double Exposition)
| Section | Key | Content |
|---|---|---|
| Orchestral Exposition | I throughout | Orchestra presents PT and ST both in tonic |
| Solo Exposition PT | I | Soloist enters with PT (often with new material) |
| Solo Exposition TR | I -> V | Transition, often virtuosic |
| Solo Exposition ST | V | ST in dominant, soloist leads |
| Development | Unstable | Both soloist and orchestra develop material |
| Recapitulation PT | I | Soloist + orchestra |
| Recapitulation ST | I | Now in tonic |
| Cadenza | I (6/4) | Solo, unaccompanied, improvised or composed |
| Coda | I | Orchestra closes |

### Concerto Slow Movement
| Form Option | Layout | Common In |
|---|---|---|
| ABA | Ternary, soloist leads A sections | Mozart, Beethoven |
| Theme + Var | Soloist varies theme, orchestra accompanies | Beethoven, Brahms |
| Romanza | Lyrical ABA with episodic middle | Mozart, Romantic |
| Rondo | ABACA, song-like | Less common |

### Concerto Finale
| Form Option | Layout | Common In |
|---|---|---|
| Rondo (ABACA) | Lively refrain, contrasting episodes | Mozart |
| Sonata-Rondo | ABACABA, combines both | Beethoven, Brahms |
| Sonata form | Full sonata, virtuosic | Romantic concertos |
| Theme + Var | Culminating variations | Brahms Violin Concerto, etc. |

## Symphony Movement Plans

### Standard Four-Movement Symphony
| Mvt | Tempo | Form | Key | Character |
|---|---|---|---|---|
| I | Fast (Allegro) | Sonata form, opt. slow intro | I | Dramatic, energetic, main argument |
| II | Slow (Adagio/Andante) | ABA, Theme+Var, Sonata | IV, V, vi, or bVI | Lyrical, reflective, emotional depth |
| III | Moderate-Fast | Scherzo+Trio or Minuet+Trio | I or relative | Dance-like, rhythmic, lighter |
| IV | Fast (Allegro/Presto) | Sonata, Rondo, Sonata-Rondo | I | Triumphant conclusion, resolution |

### Three-Movement Plan (Concerto / Some Symphonies)
| Mvt | Tempo | Form | Key |
|---|---|---|---|
| I | Fast | Sonata (double expo for concerto) | I |
| II | Slow | ABA or Theme+Var | Contrasting key |
| III | Fast | Rondo or Sonata-Rondo | I |

### Alternative Movement Plans
| Plan | Movements | Example |
|---|---|---|
| 5-movement | Fast-Scherzo-Slow-Scherzo-Fast | Mahler 5, Beethoven 6 |
| 2-movement | Slow-Fast or Fast-Slow | Beethoven Op.111 |
| Continuous | Attacca between movements | Schumann 4, Mendelssohn Scottish |
| Cyclical | Theme recurs across movements | Berlioz Fantastique, Franck |

## Key Relationships per Form Section

| Relationship | Interval | Function | Typical Location |
|---|---|---|---|
| Tonic (I) | Unison | Home key | Opening, closing, recap |
| Dominant (V) | P5 up | Main contrast in major | ST in major-key sonata expo |
| Relative major (III) | m3 up | Main contrast in minor | ST in minor-key sonata expo |
| Subdominant (IV) | P4 up | Relaxation, warmth | Slow movement, trio |
| Relative minor (vi) | m3 down | Shadow of tonic | Slow movement, episodes |
| Flat submediant (bVI) | m6 up | Romantic color | Slow movement, development |
| Mediant (iii/III) | M3/m3 up | Chromatic shift | Romantic key relations |
| Neapolitan (bII) | m2 up | Dramatic tension | Development, approach to cadenza |

## Section Proportion Guidelines

| Form | Expo | Dev | Recap | Coda |
|---|---|---|---|---|
| Classical Sonata | 35-40% | 20-25% | 30-35% | 5-10% |
| Romantic Sonata | 25-35% | 25-35% | 25-30% | 10-15% |
| Beethoven late | 25-30% | 30-35% | 20-25% | 15-20% |

| Form | Section A | Section B | Section A' |
|---|---|---|---|
| Ternary (ABA) | 35-40% | 25-30% | 30-35% |
| Scherzo+Trio | Scherzo 40% | Trio 30% | Da Capo 30% |

**Golden ratio:** Place the climax at approximately 61.8% of the way through the piece or movement.
