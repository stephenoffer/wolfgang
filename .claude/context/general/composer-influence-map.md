# Composer Influence Map

> When composing in a specific composer's style, also consult the profiles of their influences and contemporaries listed here. Early/late period distinctions are crucial — a composer's style often belongs to a different period than their birth would suggest.

## Cross-Period Composer Influences

### Period-Boundary Composers

These composers straddle period boundaries. Their early and late works require different stylistic references:

| Composer | Early style → consult | Mature style → consult | Late style → consult |
|---|---|---|---|
| **Beethoven** | Haydn, Mozart (Classical) | Beethoven's own middle period | Schubert, early Romantic harmony |
| **Mozart** | J.C. Bach, Haydn (Classical) | Mozart's own mature style | Beethoven (foreshadowed), Romantic lyricism |
| **Schubert** | Mozart, Beethoven (Classical form) | Schubert's own Romantic melody | Schumann, Brahms (harmonic adventure) |
| **Wagner** | Weber, Meyerbeer (early Romantic opera) | Wagner's own Tristan chromaticism | Bruckner, Mahler, R. Strauss, Debussy |
| **Liszt** | Chopin, Paganini (Romantic virtuosity) | Liszt's own thematic transformation | Debussy, Bartók, Schoenberg (late proto-atonality) |
| **Debussy** | Fauré, Massenet (French Romantic) | Debussy's own Impressionism | Ravel, Messiaen, Stravinsky |
| **Stravinsky** | Rimsky-Korsakov (Russian Nationalism) | Stravinsky's own Neoclassicism | Webern (late serial period) |
| **Bartók** | R. Strauss, Debussy | Bartók's own folk-modernist synthesis | Shostakovich, Lutosławski |
| **Schoenberg** | Wagner, Brahms (late Romantic) | Schoenberg's own atonality | Webern, Berg, Boulez |

### Influence Chains (Teacher → Student / Predecessor → Successor)

| Chain | Stylistic inheritance |
|---|---|
| Bach → Mozart → Beethoven | Counterpoint → Classical balance → Dramatic development |
| Haydn → Mozart → Beethoven | Symphonic form → Operatic lyricism → Heroic expansion |
| Beethoven → Schubert → Schumann → Brahms | Motivic intensity → Lyric melody → Literary fusion → Developing variation |
| Weber → Wagner → Bruckner → Mahler → Strauss | Romantic opera → Music drama → Symphonic expansion → Orchestral innovation → Operatic lyricism |
| Chopin → Liszt → Debussy → Ravel | Piano poetry → Virtuoso transformation → Impressionist color → Precision + color |
| Mussorgsky → Debussy → Ravel → Messiaen | Raw modality → Impressionist freedom → Orchestral mastery → Modes + birdsong |
| Rimsky-Korsakov → Stravinsky → (Neoclassicism) | Orchestral color → Rhythmic revolution → Classical forms reinterpreted |
| Schoenberg → Webern → Boulez | Free atonality → Concentrated serialism → Total serialism |
| Fauré → Ravel → Messiaen | Refined harmony → Precision + color → Modes + mysticism |

### "Also load when composing in the style of..." Lookup

| When style_influence is... | Also load these profiles for context |
|---|---|
| **Bach** | Handel (contrast), Vivaldi (influence on concerto style) |
| **Handel** | Bach (contrast), Vivaldi |
| **Haydn** | Mozart (mutual influence), C.P.E. Bach (Sturm und Drang) |
| **Mozart** | Haydn (mutual influence), J.C. Bach (early influence) |
| **Beethoven (early)** | Haydn, Mozart — use Classical harmony/orchestration context |
| **Beethoven (middle)** | Beethoven's own profile is primary |
| **Beethoven (late)** | Schubert (harmonic freedom), Brahms (developing variation) |
| **Schubert** | Mozart (formal models), Beethoven (harmonic ambition) |
| **Chopin** | Liszt (contrast: public vs private), Bach (counterpoint influence) |
| **Schumann** | Schubert (Lied), Beethoven (form), Brahms (friendship/influence) |
| **Liszt** | Wagner (harmonic ally), Chopin (contrast), Berlioz (orchestral program) |
| **Wagner** | Liszt (thematic transformation), Beethoven (symphonic drama) |
| **Brahms** | Beethoven (formal rigor), Schumann (Romantic expression), Bach (counterpoint) |
| **Tchaikovsky** | Mozart (lyricism), Schumann (emotional directness) |
| **Dvořák** | Brahms (mentor), Smetana (Czech nationalism) |
| **Grieg** | Schumann (Romantic harmony), Norwegian folk tradition |
| **Mussorgsky** | No strong predecessor — original; but influenced Debussy |
| **Rimsky-Korsakov** | Mussorgsky (Russian school), Berlioz (orchestration) |
| **Sibelius** | Bruckner (symphonic scale), Tchaikovsky (early influence) |
| **Bruckner** | Wagner (harmony), Beethoven (symphonic form) |
| **Mahler** | Bruckner (symphonic scale), Wagner (orchestration), Schubert (song) |
| **R. Strauss** | Wagner (harmony/drama), Liszt (tone poem), Mozart (late opera clarity) |
| **Debussy** | Mussorgsky (modal freedom), Fauré (teacher), Wagner (early influence, later rejected) |
| **Ravel** | Fauré (teacher), Debussy (contrast), Mozart (classical clarity) |
| **Satie** | No strong models — proto-minimalist, influenced Debussy |
| **Fauré** | Saint-Saëns (teacher), Chopin (piano), Schumann (song) |
| **Stravinsky (Russian)** | Rimsky-Korsakov (teacher), Mussorgsky (raw power) |
| **Stravinsky (Neoclassical)** | Mozart, Haydn, Bach — use Classical context files |
| **Bartók** | Debussy (early), Hungarian/Romanian folk, Beethoven (quartet) |
| **Prokofiev** | Haydn (humor), Stravinsky (rhythm), Tchaikovsky (lyricism) |
| **Shostakovich** | Mahler (irony/symphony), Mussorgsky (Russian character), Bach (counterpoint) |
| **Copland** | Stravinsky (clarity), American folk, jazz |
| **Schoenberg (late Romantic)** | Wagner, Brahms — use late-romantic context |
| **Schoenberg (serial)** | Schoenberg's own profile is primary |
| **Messiaen** | Debussy (color), Stravinsky (rhythm), Catholic plainchant |
| **Webern** | Schoenberg (teacher), Bach (canon/counterpoint) |
| **Arvo Pärt** | Bach (tintinnabuli derives from triads), Orthodox chant |
| **Glass** | Ravi Shankar (Indian rhythm), Boulanger (training) |
| **Reich** | West African drumming, Balinese gamelan, Coltrane |
| **John Williams** | Korngold, R. Strauss, Stravinsky, Holst |
| **Hans Zimmer** | Morricone (space/silence), electronic music, Holst |
| **Morricone** | Stravinsky, Italian opera, jazz |

## How to Use This Map

### In the Wolfgang Orchestrator (plan.json)
When creating plan.json, include a `cross_influences` field derived from this map:

```json
{
  "style_influences": ["beethoven"],
  "era_qualifier": "early",
  "cross_influences": ["haydn", "mozart"],
  "genre": "classical",
  "notes": "Early Beethoven: use Classical harmony and orchestration context, consult Haydn for formal models and Mozart for melodic grace"
}
```

### In Downstream Skills
When a skill loads composer profiles from plan.json.style_influences, it should ALSO load profiles listed in `cross_influences`. These provide:
- **Contrast**: understanding what makes the target composer distinct from their influences
- **Shared vocabulary**: techniques borrowed from predecessors
- **Period context**: harmonic/formal norms of the era the composer was working in

### Period-Sensitive Genre Loading
| If style_influence is... | Load genre context for... |
|---|---|
| Beethoven (early) | `classical/` |
| Beethoven (middle/late) | `classical/` + `romantic/` |
| Schubert | `classical/` (form) + `romantic/` (harmony) |
| Wagner | `romantic/` + `late-romantic/` |
| Debussy | `impressionist/` (primary) + `romantic/` (early works) |
| Stravinsky (Russian) | `nationalistic/` + `modern/` |
| Stravinsky (Neoclassical) | `classical/` + `modern/` |
| Schoenberg (early) | `late-romantic/` |
| Schoenberg (serial) | `modern/` |
