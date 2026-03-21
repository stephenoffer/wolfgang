# Research Template — w-research

## Profile Output Structure

Each researched composer/style produces two files in `workspace/<piece-id>/research/`:

```
workspace/<piece-id>/research/
  <composer-slug>.json        # Machine-readable parameters
  <composer-slug>.md          # Human-readable summary with ABC examples
```

## JSON Profile Schema

```json
{
  "composer": "Full Name",
  "slug": "last-name",
  "born": 1810,
  "died": 1849,
  "nationality": "Polish",
  "style_periods": ["romantic"],
  "active_period": "1829-1849",
  "biographical_summary": "2-3 sentences",
  "harmonic_language": {
    "primary_mode": "major/minor",
    "chord_vocabulary": ["triads", "dom7", "dim7", "aug6", "neapolitan"],
    "favorite_progressions": ["i-iv-V-i", "I-vi-IV-V"],
    "modulation_habits": ["chromatic mediant", "enharmonic pivot"],
    "modulation_frequency": "frequent|moderate|rare",
    "dissonance_level": "low|moderate|high|extreme",
    "chromaticism": "diatonic|moderate|highly-chromatic",
    "cadence_types": ["PAC", "HC", "deceptive", "plagal"],
    "pedal_use": "frequent|occasional|rare",
    "harmonic_rhythm": "slow|moderate|fast|variable"
  },
  "melodic_style": {
    "typical_range": "P8-P12",
    "phrase_lengths": [4, 8],
    "phrase_structure": "periodic|sentence|asymmetric|through-composed",
    "interval_preferences": ["stepwise", "3rds", "6ths"],
    "large_leaps": "rare|occasional|frequent",
    "ornamentation": "none|light|moderate|heavy",
    "ornament_types": ["turn", "trill", "mordent", "appoggiatura"],
    "motivic_development": "extensive|moderate|minimal",
    "sequence_use": "frequent|moderate|rare",
    "lyrical_quality": "singing|declamatory|instrumental"
  },
  "rhythmic_characteristics": {
    "common_meters": ["4/4", "3/4", "6/8"],
    "tempo_range": "largo-presto",
    "preferred_tempos": ["andante", "allegro"],
    "rhythmic_complexity": "simple|moderate|complex",
    "common_patterns": ["dotted rhythms", "triplets", "syncopation"],
    "rubato": "none|light|moderate|heavy",
    "polyrhythm": "none|occasional|frequent",
    "rhythmic_devices": ["hemiola", "augmentation", "diminution"]
  },
  "orchestration": {
    "preferred_ensembles": ["solo piano", "orchestra"],
    "favorite_instruments": ["piano", "violin", "cello"],
    "texture_types": ["homophonic", "melody+accompaniment"],
    "doubling_habits": "description",
    "dynamic_range": "pp-ff",
    "climax_technique": "description",
    "color_instruments": ["harp", "celesta"],
    "avoids": ["description of what composer avoids"]
  },
  "formal_characteristics": {
    "preferred_forms": ["sonata", "nocturne", "ballade"],
    "innovations": "description of formal innovations",
    "section_proportions": "balanced|front-loaded|climax-late",
    "coda_treatment": "brief|extended|transformative",
    "introduction_style": "none|brief|grand",
    "transitions": "smooth|abrupt|developmental"
  },
  "representative_works": [
    {
      "title": "Work Title",
      "opus": "Op. X",
      "key": "C minor",
      "year": 1835,
      "form": "sonata",
      "significance": "Brief description",
      "notable_features": ["feature1", "feature2"]
    }
  ],
  "abc_examples": {
    "typical_melody": "ABC notation string",
    "typical_accompaniment": "ABC notation string",
    "characteristic_progression": "ABC notation string"
  },
  "confidence": "high|medium|low",
  "sources": ["source1", "source2"]
}
```

## Required Fields by Priority

| Priority | Field                    | Fallback if Missing                          |
|----------|--------------------------|----------------------------------------------|
| Critical | composer, style_periods  | Cannot proceed without                       |
| Critical | harmonic_language        | Default to period norms                      |
| Critical | melodic_style            | Default to period norms                      |
| High     | rhythmic_characteristics | Default to period norms                      |
| High     | representative_works     | Use period exemplars                         |
| High     | formal_characteristics   | Use standard forms for period                |
| Medium   | orchestration            | Use period standard orchestration            |
| Medium   | biographical_summary     | Skip; not musically critical                 |
| Low      | abc_examples             | Generate from parameters                     |

## Search Query Templates

### Biographical Context
```
"<composer name>" biography musical style
"<composer name>" compositional technique characteristics
```

### Harmonic Language
```
"<composer name>" harmony harmonic language
"<composer name>" chord progressions modulation
"<composer name>" chromaticism tonal language
"<composer name>" cadence harmonic rhythm
```

### Melodic Style
```
"<composer name>" melodic style melody writing
"<composer name>" phrase structure thematic
"<composer name>" ornamentation embellishment
"<composer name>" motivic development
```

### Rhythmic Characteristics
```
"<composer name>" rhythm tempo rhythmic patterns
"<composer name>" meter time signature
"<composer name>" rubato rhythmic freedom
```

### Orchestration
```
"<composer name>" orchestration instrumentation
"<composer name>" scoring texture
"<composer name>" favorite instruments ensemble
```

### Formal Innovations
```
"<composer name>" musical form structure
"<composer name>" sonata form innovation
"<composer name>" formal structure analysis
```

### Representative Works
```
"<composer name>" most important works masterpieces
"<composer name>" best known compositions analysis
```

### Style Period Context (when composer is unknown)
```
"<style period>" musical characteristics harmony
"<style period>" compositional techniques orchestration
"<style period>" representative composers works
```

## Validating and Cross-Referencing

### Reliability Tiers

| Source Type                    | Reliability | Use                              |
|--------------------------------|------------|----------------------------------|
| Academic music analysis papers | High       | Harmonic/formal details          |
| Published music dictionaries   | High       | Biographical, works list         |
| University course materials    | Medium     | General style characteristics    |
| Music theory websites          | Medium     | Cross-reference only             |
| General encyclopedias          | Medium     | Biographical context             |
| Blog posts / forums            | Low        | Anecdotal; verify independently  |

### Cross-Reference Rules

1. **Harmonic claims** — verify with at least 2 sources; check against score excerpts if available
2. **Biographical dates** — cross-reference born/died/active with at least 2 sources
3. **Style period** — confirm against known period boundaries:

| Period          | Approximate Dates | Key Characteristics               |
|-----------------|--------------------|-----------------------------------|
| Baroque         | 1600-1750          | Basso continuo, counterpoint      |
| Classical       | 1750-1820          | Balanced phrases, clarity         |
| Romantic        | 1820-1900          | Chromaticism, expression          |
| Late Romantic   | 1880-1920          | Extended tonality, large forces   |
| Nationalistic   | 1850-1920          | Folk elements, national identity  |
| Impressionist   | 1890-1930          | Color, whole-tone, parallelism    |
| Modern          | 1900-1975          | Atonality, serialism, new sounds  |
| Minimalist      | 1960-present       | Repetition, gradual process       |
| Film Score      | 1930-present       | Eclectic, dramatic, functional    |

4. **Orchestration claims** — verify against known instrumentation of major works
5. **"Favorite" or "typical"** — must appear in multiple works, not just one

## Extracting Musical Parameters from Descriptive Text

### Mapping Descriptive Language to Parameters

| Descriptive Term              | Musical Parameter                          | Value                    |
|-------------------------------|--------------------------------------------|--------------------------|
| "lyrical", "singing"         | melodic_style.lyrical_quality              | singing                  |
| "angular", "jagged"          | melodic_style.interval_preferences         | large leaps frequent     |
| "lush", "rich"               | orchestration.texture_types                | thick homophonic         |
| "sparse", "austere"          | orchestration.texture_types                | thin, exposed            |
| "chromatic", "colorful"      | harmonic_language.chromaticism             | highly-chromatic         |
| "diatonic", "simple"         | harmonic_language.chromaticism             | diatonic                 |
| "driving", "relentless"      | rhythmic_characteristics.rhythmic_devices  | ostinato, motor rhythm   |
| "flexible", "free"           | rhythmic_characteristics.rubato            | heavy                    |
| "monumental", "grand"        | orchestration.dynamic_range                | pp-fff, large forces     |
| "intimate", "delicate"       | orchestration.preferred_ensembles          | chamber, solo            |
| "contrapuntal", "polyphonic" | orchestration.texture_types                | polyphonic               |
| "bold", "dramatic"           | orchestration.climax_technique             | tutti, brass-heavy       |
| "pastoral"                   | harmonic_language.primary_mode             | major, modal mixtures    |
| "dark", "brooding"           | harmonic_language.primary_mode             | minor, low register      |
| "virtuosic", "brilliant"     | melodic_style.ornamentation                | heavy, fast passages     |
| "folk-like"                   | melodic_style.phrase_structure             | periodic, modal scales   |

### Ambiguous Terms — Require Context

| Term           | Possible Meanings                                      |
|----------------|--------------------------------------------------------|
| "Classical"    | Period (1750-1820) OR general art music                |
| "Modern"       | 20th-century OR contemporary                           |
| "Complex"      | Harmonically OR rhythmically OR texturally             |
| "Simple"       | Texture OR harmony OR form                             |
| "Heavy"        | Orchestration OR rhythm OR emotional weight            |
| "Light"        | Texture OR dynamic OR character                        |

## Markdown Profile Output Format

```markdown
# Composer Name (born-died)

## Style Summary
Period: [period]. 2-3 sentence overview.

## Harmonic Language
- Primary mode: [major/minor/modal]
- Chord vocabulary: [list]
- Characteristic progressions: [with ABC examples]
- Modulation: [habits]

## Melodic Style
- Range: [typical range]
- Phrase structure: [type, typical lengths]
- Characteristic intervals: [list]
- Example:
X:1
T:Typical Melody
M:4/4
K:Cmaj
[ABC notation]

## Rhythmic Profile
- Preferred meters: [list]
- Tempo range: [range]
- Characteristic patterns: [with ABC]

## Orchestration
- Preferred ensembles: [list]
- Texture: [description]
- Special techniques: [list]

## Formal Approach
- Preferred forms: [list]
- Innovations: [description]

## Representative Works
1. **Title** (Op. X, year) - key, form. Significance.
2. ...

## Confidence Assessment
[high/medium/low] - [reasoning]
Sources: [list]
```

## Handling Unknown or Obscure Composers

| Scenario                           | Strategy                                         |
|------------------------------------|--------------------------------------------------|
| Composer found in databases        | Full profile as above                            |
| Composer partially documented      | Fill gaps with period/regional defaults           |
| Composer very obscure              | Research contemporaries; use regional style       |
| Composer fictional / not found     | Report to user; suggest period-based approach     |
| Style description, no composer     | Build style profile from period norms             |
| Living composer                    | Research published analyses; note copyright       |

## Output Checklist

Before finalizing a research profile, verify:

- [ ] All critical fields populated (or defaults noted)
- [ ] At least 3 representative works listed with key details
- [ ] Harmonic vocabulary matches claimed style period
- [ ] ABC examples parse without errors
- [ ] No contradictory claims (e.g., "diatonic" + "highly chromatic")
- [ ] Confidence level honestly assessed
- [ ] Sources documented
- [ ] JSON validates against schema
- [ ] Markdown renders correctly
