# MusicXML Structure Reference — w-assemble

## MusicXML 4.0 File Structure Overview

MusicXML is an XML-based format for representing Western musical notation. Version 4.0 (W3C Community Group, 2021) is the current standard. Two root element types exist:

| Root Element       | Description                              | Use Case                  |
|--------------------|------------------------------------------|---------------------------|
| `score-partwise`   | Organized by part, then measure          | Default for most software |
| `score-timewise`   | Organized by measure, then part          | Rarely used in practice   |

music21 always exports `score-partwise`. MuseScore, Finale, Dorico all prefer `score-partwise`.

## score-partwise Document Skeleton

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <work><work-title>Title</work-title></work>
  <identification>
    <creator type="composer">Composer Name</creator>
    <encoding><software>music21</software></encoding>
  </identification>
  <part-list>...</part-list>
  <part id="P1">...</part>
  <part id="P2">...</part>
</score-partwise>
```

## Part-List Structure

```xml
<part-list>
  <score-part id="P1">
    <part-name>Violin I</part-name>
    <part-abbreviation>Vln. I</part-abbreviation>
    <score-instrument id="P1-I1">
      <instrument-name>Violin</instrument-name>
    </score-instrument>
    <midi-instrument id="P1-I1">
      <midi-channel>1</midi-channel>
      <midi-program>41</midi-program>
    </midi-instrument>
  </score-part>
</part-list>
```

| Element              | Required | Notes                                        |
|----------------------|----------|----------------------------------------------|
| `part-name`          | Yes      | Full instrument name                         |
| `part-abbreviation`  | No       | Short name for subsequent systems            |
| `score-instrument`   | No       | Links to MIDI; music21 always generates      |
| `midi-instrument`    | No       | MIDI channel/program; needed for playback    |
| `part-group`         | No       | Brackets/braces for instrument families      |

### Part Groups (brackets/braces)

```xml
<part-group type="start" number="1">
  <group-symbol>bracket</group-symbol>
  <group-barline>yes</group-barline>
</part-group>
<!-- score-parts here -->
<part-group type="stop" number="1"/>
```

| Symbol    | Use                        |
|-----------|----------------------------|
| `bracket` | Orchestral families        |
| `brace`   | Piano/harp grand staff     |
| `line`    | Thin line grouping         |
| `none`    | Logical group, no symbol   |

## Measure Structure

Elements appear in this order within each `<measure>`:

| Order | Element        | Purpose                              | Required         |
|-------|----------------|--------------------------------------|------------------|
| 1     | `<print>`      | System/page breaks, staff layout     | First measure     |
| 2     | `<attributes>`  | Clef, key, time, divisions, staves  | First measure + changes |
| 3     | `<direction>`   | Tempo, dynamics, rehearsal marks    | As needed        |
| 4     | `<note>`        | Pitches, rests, durations, voices   | Yes              |
| 5     | `<forward>`/`<backup>` | Navigate between voices      | Multi-voice      |
| 6     | `<barline>`     | Special barlines (repeat, double)   | As needed        |

### Attributes Block

```xml
<attributes>
  <divisions>4</divisions>          <!-- divisions per quarter note -->
  <key><fifths>-3</fifths></key>    <!-- Eb major / C minor -->
  <time><beats>4</beats><beat-type>4</beat-type></time>
  <clef><sign>G</sign><line>2</line></clef>
</attributes>
```

| Key Signature `<fifths>` | Major | Minor |
|--------------------------|-------|-------|
| -7 to -1                 | Cb..F | Ab..D |
| 0                        | C     | A     |
| 1 to 7                   | G..C# | E..A# |

### Note Element

```xml
<note>
  <pitch><step>C</step><alter>1</alter><octave>4</octave></pitch>
  <duration>4</duration>
  <voice>1</voice>
  <type>quarter</type>
  <stem>up</stem>
  <staff>1</staff>
</note>
```

| Duration Type  | Divisions (div=4) | MusicXML `<type>` |
|----------------|--------------------|--------------------|
| Whole          | 16                 | whole              |
| Half           | 8                  | half               |
| Quarter        | 4                  | quarter            |
| Eighth         | 2                  | eighth             |
| 16th           | 1                  | 16th               |
| Dotted quarter | 6                  | quarter + `<dot/>` |

### Directions (dynamics, tempo, text)

```xml
<direction placement="below">
  <direction-type><dynamics><ff/></dynamics></direction-type>
  <sound dynamics="112"/>
</direction>
<direction placement="above">
  <direction-type><words font-style="italic">dolce</words></direction-type>
</direction>
<direction>
  <sound tempo="120"/>
</direction>
```

## music21 MusicXML Export Conventions

| Behavior                         | Detail                                                |
|----------------------------------|-------------------------------------------------------|
| Divisions                        | Defaults to 10080 (LCM of common durations)           |
| Part IDs                         | Sequential: P1, P2, P3...                             |
| Voice numbering                  | Starts at 1; each staff gets separate voices           |
| Beam export                      | Automatic beaming based on time signature              |
| Tie notation                     | Both `<tie>` (sound) and `<tied>` (notation) emitted  |
| Tuplets                          | `<time-modification>` + `<tuplet>` notation            |
| Grand staff                      | Single part with `<staves>2</staves>` in attributes   |
| Default tempo                    | 120 BPM if none specified                             |
| Instrument names                 | From music21 instrument class names                    |

## Common music21 MusicXML Issues

| Issue                              | Cause                                  | Fix / Validation                         |
|------------------------------------|----------------------------------------|------------------------------------------|
| Missing `<divisions>` in measure 1 | Stream not properly configured         | Ensure `makeNotation()` called           |
| Voice conflicts                    | Overlapping offsets in same voice       | Run `makeVoices()` before export         |
| Duration overflow                  | Notes exceed measure duration           | Run `makeMeasures()` to split            |
| Missing clefs                      | Parts without explicit clef assignment  | Set clef on first measure of each part   |
| Incorrect enharmonics              | music21 default spelling               | Call `makeAccidentals()` post-assembly   |
| Empty measures                     | Rests not explicitly written            | `makeRests(fillGaps=True)`              |
| Key sig not propagating            | Key set mid-stream but not at start    | Ensure key sig in measure 1 attributes   |
| Slur/tie orphans                   | Start without stop or vice versa       | Post-validate with `validate_musicxml.py`|
| Excessive divisions value          | music21 default 10080                  | Acceptable; MuseScore handles fine       |

## Compressed MXL Format

MXL is a ZIP archive containing the MusicXML file plus metadata.

```
archive.mxl (ZIP)
├── META-INF/
│   └── container.xml
└── score.musicxml
```

### container.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<container>
  <rootfiles>
    <rootfile full-path="score.musicxml"
              media-type="application/vnd.recordare.musicxml+xml"/>
  </rootfiles>
</container>
```

music21 export: `score.write('mxl', fp='output.mxl')` handles this automatically.

## MuseScore Import Considerations

| Consideration              | Detail                                                    |
|----------------------------|-----------------------------------------------------------|
| Preferred format           | .mxl (compressed) or .musicxml                           |
| Part name display          | Uses `<part-name>` for first system, `<part-abbreviation>` thereafter |
| Dynamics placement         | Respects `placement="below"` attribute                    |
| Rehearsal marks            | Must be `<rehearsal>` inside `<direction-type>`           |
| Page/system breaks         | Honored from `<print new-system="yes">`                  |
| Multi-voice rendering      | Stem direction from voice number (1=up, 2=down)          |
| Transposing instruments    | Needs `<transpose>` in attributes for correct display     |
| Percussion                 | Requires `<clef><sign>percussion</sign></clef>`          |
| Grace notes                | `<grace/>` element before `<pitch>`; slash attribute      |
| Articulations              | Inside `<notations><articulations>` — MuseScore renders all standard types |

## Assembly Pipeline: Sections to Full Score

### Step 1: Validate Section ABCs
```
For each section ABC file:
  → validate_abc.py section.abc
  → Check part count matches orchestration plan
  → Verify key/time signatures match structure plan
```

### Step 2: Convert Sections to music21 Streams
```
For each section:
  → abc_to_musicxml.py → music21.converter.parse()
  → Returns music21.stream.Score object
  → Verify measure count matches expected duration
```

### Step 3: Concatenate Sections into Movements
```
For each movement:
  → Ordered section list from structure.json
  → Append each section's measures to movement stream
  → Insert double barlines at section boundaries
  → Handle key/time/tempo changes at boundaries
  → Add rehearsal marks at section starts
```

### Step 4: Assemble Movements into Full Score
```
For multi-movement works:
  → Each movement = separate music21.Score
  → Final barline at movement end
  → System break between movements
  → Reset measure numbering per movement (optional)
```

### Step 5: Post-Assembly Cleanup
```
score.makeNotation()          # Fix beaming, accidentals
score.makeAccidentals()       # Proper enharmonic spelling
score.makeRests(fillGaps=True) # Fill empty voice gaps
range_checker.py              # Verify instrument ranges
validate_musicxml.py          # Schema validation
```

## Post-Assembly Validation Checklist

| Check                          | Tool                    | Pass Criteria                          |
|--------------------------------|-------------------------|----------------------------------------|
| XML well-formed                | lxml.etree.parse()      | No parse errors                        |
| Schema valid                   | validate_musicxml.py    | Validates against MusicXML 4.0 DTD     |
| All parts present              | Count `<part>` elements | Matches orchestration plan             |
| Measure counts consistent      | Compare across parts    | All parts same number of measures      |
| Duration consistency           | Sum durations/measure   | Each measure sums to time signature    |
| Instrument ranges              | range_checker.py        | No notes outside instrument range      |
| Key signatures propagated      | Check `<attributes>`    | Present in measure 1 of every part     |
| Time signatures propagated     | Check `<attributes>`    | Present in measure 1 of every part     |
| No orphaned ties/slurs         | Scan start/stop pairs   | Every start has matching stop          |
| Dynamics present               | Scan `<dynamics>`       | At least one per section per part      |
| Tempo markings present         | Scan `<sound tempo>`    | At section starts per structure plan   |
| Final barline                  | Last measure `<barline>`| `<bar-style>light-heavy</bar-style>`   |
| MuseScore test import          | Open in MuseScore       | No import warnings                     |

## Workspace File Paths

```
workspace/<piece-id>/
  sections/
    m1_expo_pt.abc          # Section ABC files
    m1_expo_st.abc
  movements/
    movement_1.musicxml     # Assembled movement
  output/
    score.musicxml          # Final uncompressed
    score.mxl               # Final compressed
  assembly_log.json         # Assembly report + validation results
```
