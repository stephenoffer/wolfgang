# Baroque Period Forms Reference

> Dense reference for AI composition agents. Covers formal structures c. 1600-1750.

---

## 1. Fugue

The pinnacle of Baroque contrapuntal form.

### Fugue Anatomy

| Component | Description | Location |
|---|---|---|
| Subject | Main theme; defines the fugue | Opening voice, alone |
| Answer | Subject in dominant key (real or tonal) | Second voice entry |
| Countersubject | Counterpoint against the answer; may recur | Accompanies answer |
| Exposition | All voices enter with subject/answer | Beginning |
| Episode | Non-subject material; sequential, modulatory | Between subject entries |
| Middle entries | Subject returns in various keys | After exposition |
| Stretto | Overlapping subject entries | Climactic section |
| Pedal point | Sustained tonic or dominant | Near end |
| Final entry | Subject in tonic, definitive | Conclusion |

### Real vs Tonal Answer

| Type | Description | When to Use |
|---|---|---|
| Real answer | Exact transposition to dominant | Subject stays within key |
| Tonal answer | Modified to preserve tonic-dominant relationship | Subject begins ^1-^5 or ^5-^1 |

### Tonal Answer Rule

| Subject begins | Answer begins |
|---|---|
| ^1 | ^5 |
| ^5 | ^1 (NOT ^2) |
| ^1-^5 | ^5-^1 |
| ^5-^1 | ^1-^5 |

### Episode Techniques

| Technique | Description |
|---|---|
| Sequence of subject fragment | Most common |
| Invertible counterpoint | Swap upper/lower voices |
| Free counterpoint | Non-thematic, transitional |
| Modulating sequence | Drives to next key area |

### ABC Example: Fugue exposition (2 voices)
```abc
X:1
M:4/4
L:1/8
K:C
V:1
%% Subject
C2 DE FG Ac | B2 AG FE D2 |
%% Countersubject against answer
E2 FG AB cB | AG FE D2 C2 |
V:2
%% Rests during subject
z8 | z8 |
%% Answer (dominant)
G2 AB cd ge | f2 ed cB A2 |
```

### Fugue Voice Count

| Voices | Common In | Difficulty |
|---|---|---|
| 2 (bicinium) | Keyboard, didactic | Moderate |
| 3 | Keyboard, chamber | Standard |
| 4 | Choral, organ, orchestral | Standard |
| 5 | Choral, grand organ | Complex |
| 6+ | Rare; showpiece | Very complex |

## 2. Ritornello Form

Primary form for Baroque concerto fast movements.

### Structure

| Section | Key | Content | Forces |
|---|---|---|---|
| Ritornello 1 | I | Full theme | Tutti |
| Episode 1 | I -> V | Solo, new/derived material | Solo + continuo |
| Ritornello 2 | V | Full or partial theme | Tutti |
| Episode 2 | V -> vi or other | Solo development | Solo + continuo |
| Ritornello 3 | vi or other | Partial theme | Tutti |
| Episode 3 | -> I | Solo, virtuosic return | Solo + continuo |
| Ritornello 4 | I | Full theme, conclusive | Tutti |

### Ritornello Principles

| Principle | Description |
|---|---|
| Modular theme | Ritornello has distinct segments that can appear separately |
| Key confirms | Each ritornello confirms a key |
| Episodes modulate | Solo episodes drive to new keys |
| Shortening | Later ritornellos often use only fragments |
| Solo virtuosity | Episodes showcase soloist |
| Framework | Ritornello returns provide structural pillars |

## 3. Da Capo Aria (ABA)

Standard vocal form; also used instrumentally.

| Section | Key | Content | Marking |
|---|---|---|---|
| A section | I (with modulation to V) | Main text/music, ritornello-based | Written out |
| B section | Contrasting key (relative, iv, etc.) | New text, contrasting affect | Written out |
| A section (da capo) | I | Repeat of A with ornamentation | "Da Capo" instruction |

### Da Capo Conventions

| Convention | Description |
|---|---|
| A section repeat | Singer ornaments melody on return |
| B section contrast | Shorter, different affect/key/texture |
| Opening ritornello | Orchestra introduces A material |
| Closing ritornello | Orchestra closes A section |
| Improvised cadenza | Singer adds cadenza before final cadence of A |

## 4. Binary Dance Forms

The building blocks of the Baroque suite.

### Binary Form Structure

| Section | Key Plan (Major) | Key Plan (Minor) | Repeats |
|---|---|---|---|
| A | I -> V | i -> III | :double-bar: |
| B | V -> (sequence) -> I | III -> (sequence) -> i | :double-bar: |

### The Suite (Ordre, Partita)

| Movement | Meter | Tempo | Character | Rhythm Pattern |
|---|---|---|---|---|
| Allemande | 4/4 | Moderate | Serious, flowing | Upbeat start, continuous 16ths |
| Courante (French) | 3/2 or 6/4 | Moderate | Stately, hemiola | Cross-rhythms, 3/2 vs 6/4 |
| Corrente (Italian) | 3/4 | Fast | Running, light | Continuous running notes |
| Sarabande | 3/4 | Slow | Stately, expressive | Stress on beat 2, dotted rhythms |
| Gigue | 6/8 or 12/8 | Fast | Lively, closing | Compound meter, fugal opening |

### Optional Movements (Galanteries, inserted between Sarabande and Gigue)

| Movement | Meter | Character |
|---|---|---|
| Minuet | 3/4 | Elegant, moderate |
| Bourree | 2/2 | Brisk, upbeat start |
| Gavotte | 2/2 | Moderate, half-bar upbeat |
| Passepied | 3/8 | Quick, light minuet |
| Polonaise | 3/4 | Stately, rhythmic |
| Air | Various | Lyrical, songlike |
| Loure | 6/4 | Slow gigue, dotted |

### ABC Example: Sarabande character (stress on beat 2)
```abc
X:2
M:3/4
L:1/4
K:Dm
D3/2 E/ F | G2 F | E3/2 F/ G | A2 z |
%% Note: dotted rhythm and emphasis on beat 2
```

### ABC Example: Gigue opening (compound meter, fugal)
```abc
X:3
M:6/8
L:1/8
K:D
V:1
D2 F AFA | G2 B d3 |
V:2
z6 | z6 |
%% Voice 2 enters next bar with answer
```

## 5. Ground Bass / Basso Ostinato

| Feature | Description |
|---|---|
| Structure | Short bass pattern (4-8 bars) repeats continuously |
| Variations | Upper voices provide continuous variation |
| Harmonic | Bass implies fixed harmonic progression |
| Length | Can be extended indefinitely |

### Famous Ground Bass Patterns

| Pattern | Description |
|---|---|
| Descending tetrachord | ^1-^7-b^7-^6-b^6-^5 (chromatic lament) |
| Diatonic descent | ^1-^7-^6-^5 |
| Ascending pattern | ^1-^2-^3-^4-^5 |
| Repeated chords | Fixed harmonic sequence as ostinato |

## 6. Passacaglia and Chaconne

| Feature | Passacaglia | Chaconne |
|---|---|---|
| Bass | Fixed bass pattern, repeating | Harmonic pattern, bass may vary |
| Meter | Triple (3/4) | Triple (3/4) |
| Tempo | Slow to moderate | Slow to moderate |
| Variations | Above the bass | More freely over harmonic scheme |
| Key | Often minor | Often minor |
| Length | Extended | Extended |
| Climax | Builds intensity over variations | Same |

### Note: The distinction between passacaglia and chaconne is debated. In practice, treat both as variation sets over a repeating bass/harmonic pattern.

## 7. Toccata

| Feature | Description |
|---|---|
| Character | Improvisatory, virtuosic, free |
| Sections | Alternating free (scale runs, arpeggios) and strict (fugal) |
| Instrument | Organ or harpsichord |
| Purpose | Display instrument and player capabilities |
| Harmony | Exploratory; establishes key through exploration |
| Pairing | Often paired with fugue (Toccata and Fugue) |

## 8. Prelude

| Type | Description |
|---|---|
| Improvisatory | Free, arpeggiated, exploratory (WTC preludes) |
| Inventive | Single motif developed continuously |
| Dance-like | Structured, rhythmic (some WTC preludes) |
| Chorale prelude | Based on chorale melody (organ) |
| Pairing | Before fugue, suite, or liturgical piece |

## 9. French Overture

| Section | Tempo | Character | Texture |
|---|---|---|---|
| A (slow) | Grave, lent | Majestic, dotted rhythms | Homophonic, full |
| B (fast) | Allegro | Fugal, energetic | Imitative |
| A' (optional) | Slow return | Brief, closing | Homophonic |

### ABC Example: French overture dotted rhythm
```abc
X:4
M:4/4
L:1/8
K:D
!f! D3 E F2 G2 | A3 B A2 G2 | F3 G A4 |
%% Double-dotting convention: dotted rhythms played MORE dotted
```

## 10. Italian Overture (Sinfonia)

| Section | Tempo | Character |
|---|---|---|
| I | Allegro | Homophonic, energetic |
| II | Adagio | Brief, lyrical, transitional |
| III | Allegro | Dance-like (often minuet/gigue) |

## 11. Concerto Forms

### Solo Concerto (Vivaldi model, 3 movements)

| Movement | Tempo | Form |
|---|---|---|
| I | Allegro | Ritornello |
| II | Adagio/Largo | Binary, through-composed, or ABA |
| III | Allegro/Presto | Ritornello (shorter, lighter) |

### Concerto Grosso (Corelli model)

| Type | Movements | Description |
|---|---|---|
| Chiesa (church) | Slow-Fast-Slow-Fast | Serious, contrapuntal |
| Camera (chamber) | Suite-like dance movements | Dance-based |

## 12. Form-Function Quick Reference

| If generating... | Use this form |
|---|---|
| Concerto fast movement | Ritornello form |
| Concerto slow movement | Binary, ABA, or arioso |
| Vocal aria | Da capo (ABA) |
| Keyboard prelude | Improvisatory or inventive |
| Keyboard fugue | Fugue (3-4 voices) |
| Dance movement | Binary form with suite conventions |
| Ground bass piece | Passacaglia/chaconne |
| Orchestral opening | French or Italian overture |
| Chorale setting | 4-part homophonic + passing tones |
| Organ prelude | Toccata, prelude, or chorale prelude |
| Chamber music | Trio sonata or solo sonata in 3-4 movements |
