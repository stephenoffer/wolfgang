# Famous Themes Index — w-novelty

Interval patterns for plagiarism checking. Supplements `FAMOUS_THEMES` in `novelty_checker.py`.

## Format Key

- **Intervals**: semitone deltas (positive=up, negative=down). `+2` = whole step up, `-1` = half step down
- **Parsons**: U=up, D=down, R=repeat (contour code, pitch direction only)
- **Rhythm**: approximate rhythmic profile (L=long, S=short, relative)

## Baroque (1600-1750)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 1 | Toccata opening | Bach | Toccata & Fugue BWV 565 | +0,-1,+1,-12 | R,D,U,D | S,S,L,L |
| 2 | Fugue subject BWV 565 | Bach | Toccata & Fugue BWV 565 | +0,-2,-2,-1,+5,-2,-1 | R,D,D,D,U,D,D | L,S,S,S,S,S,S |
| 3 | Air on G String | Bach | Orchestral Suite No.3 BWV 1068 | +0,+2,+2,+1,-1,-2,+2 | R,U,U,U,D,D,U | L,S,S,S,S,S,L |
| 4 | Hallelujah | Handel | Messiah HWV 56 | +0,+0,+0,+0,+4,-4,+4 | R,R,R,R,U,D,U | S,S,S,L,S,S,L |
| 5 | Spring allegro | Vivaldi | Four Seasons Op.8/1 RV 269 | +0,+2,+2,+1,+2,+2,-2,-2 | R,U,U,U,U,U,D,D | S,S,S,S,S,L,S,S |
| 6 | Winter allegro | Vivaldi | Four Seasons Op.8/4 RV 297 | +0,-1,+1,-1,+1,-1,+1,-1 | R,D,U,D,U,D,U,D | S,S,S,S,S,S,S,S |
| 7 | Canon | Pachelbel | Canon in D | +0,-2,-2,+2,+2,-2,-2 | R,D,D,U,U,D,D | L,L,L,L,L,L,L |
| 8 | La Rejouissance | Handel | Music for Royal Fireworks | +0,+4,+3,+0,-3,-4,+7 | R,U,U,R,D,D,U | S,S,S,S,S,S,L |
| 9 | Wachet Auf | Bach | BWV 140 Cantata | +0,+0,+4,+3,-3,+3,+2,-2 | R,R,U,U,D,U,U,D | L,S,S,S,S,S,S,L |
| 10 | Jesu Joy | Bach | BWV 147 Cantata | +0,+2,-2,+2,+2,+1,-1,-2,+2 | R,U,D,U,U,U,D,D,U | S,S,S,S,S,S,S,S,L |
| 11 | Arrival of Queen of Sheba | Handel | Solomon HWV 67 | +0,+4,-4,+4,-4,+7,-3 | R,U,D,U,D,U,D | S,S,S,S,S,S,S |
| 12 | Adagio | Albinoni | Adagio in G minor | +0,+2,+1,+2,+2,-2,-1 | R,U,U,U,U,D,D | L,L,S,S,L,S,L |

## Classical (1750-1820)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 13 | Symphony 40 opening | Mozart | Symphony No.40 K.550 | +0,+1,-1,+0,+1,-1,+0 | R,U,D,R,U,D,R | S,S,S,S,S,S,L |
| 14 | Eine Kleine mvt.1 | Mozart | Eine Kleine Nachtmusik K.525 | +0,+4,+0,+3,+0,-3,-4 | R,U,R,U,R,D,D | S,S,S,S,S,S,L |
| 15 | Fifth Symphony | Beethoven | Symphony No.5 Op.67 | +0,+0,-1,-3 | R,R,D,D | S,S,S,L |
| 16 | Ode to Joy | Beethoven | Symphony No.9 Op.125 | +0,+0,+2,+2,-2,-2,-2,+2,+2,+1,-1 | R,R,U,U,D,D,D,U,U,U,D | S,S,S,S,S,S,S,S,S,S,L |
| 17 | Moonlight mvt.1 | Beethoven | Sonata No.14 Op.27/2 | +0,+0,+1,+1,+1,-1 | R,R,U,U,U,D | L,L,S,S,L,L |
| 18 | Fur Elise | Beethoven | Bagatelle WoO 59 | +0,-1,+1,-1,+1,-1,-3,+5,-2 | R,D,U,D,U,D,D,U,D | S,S,S,S,S,S,S,S,S |
| 19 | Surprise Symphony | Haydn | Symphony No.94 | +0,+0,+4,-4,+0,+0,+5,-5 | R,R,U,D,R,R,U,D | S,S,S,S,S,S,S,L |
| 20 | Emperor Hymn | Haydn | String Quartet Op.76/3 | +0,+2,+2,+1,-1,+1,+2,-2 | R,U,U,U,D,U,U,D | L,S,S,S,S,S,L,L |
| 21 | Pathetique mvt.2 | Beethoven | Sonata No.8 Op.13 | +0,+2,+1,+2,-2,-1,+1,-1 | R,U,U,U,D,D,U,D | L,S,S,L,S,S,S,L |
| 22 | Turkish March | Mozart | Sonata No.11 K.331 | +0,+2,-1,+1,-2,+5,-2,-3 | R,U,D,U,D,U,D,D | S,S,S,S,S,S,S,S |
| 23 | Jupiter finale | Mozart | Symphony No.41 K.551 | +0,+2,+2,-2,+7,-5 | R,U,U,D,U,D | L,L,L,L,L,L |
| 24 | Waldstein mvt.1 | Beethoven | Sonata No.21 Op.53 | +0,+0,+0,+2,+0,+0,+0,+2 | R,R,R,U,R,R,R,U | S,S,S,S,S,S,S,S |

## Romantic (1820-1900)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 25 | Piano Concerto 2 | Rachmaninoff | PC No.2 Op.18 | +0,-2,-1,+3,-2,+2,-1,-1 | R,D,D,U,D,U,D,D | L,L,L,L,L,L,S,L |
| 26 | Piano Concerto 3 | Rachmaninoff | PC No.3 Op.30 | +0,+2,-2,+2,+2,-1,-2,+2,-2 | R,U,D,U,U,D,D,U,D | S,S,S,S,S,S,S,S,S |
| 27 | Rhapsody Paganini | Rachmaninoff | Rhapsody Op.43 Var.18 | +0,+2,+2,+1,-1,-2,+4,-2 | R,U,U,U,D,D,U,D | L,S,S,L,S,S,L,L |
| 28 | Piano Concerto 1 | Tchaikovsky | PC No.1 Op.23 | +0,+0,-2,-1,+3,-2,+2,-2 | R,R,D,D,U,D,U,D | L,L,S,S,S,S,S,L |
| 29 | Swan Lake theme | Tchaikovsky | Swan Lake Op.20 | +0,-2,-1,-2,+5,-2,-1 | R,D,D,D,U,D,D | L,S,S,L,L,S,L |
| 30 | Romeo & Juliet love | Tchaikovsky | Romeo & Juliet Overture | +0,+2,+2,+1,-1,+3,-3,-2 | R,U,U,U,D,U,D,D | L,L,L,S,S,L,S,L |
| 31 | Dance of Sugar Plum | Tchaikovsky | Nutcracker Op.71 | +0,-5,+1,+4,-5,+1 | R,D,U,U,D,U | S,S,S,S,S,S |
| 32 | 1812 Overture theme | Tchaikovsky | 1812 Overture Op.49 | +0,+2,+2,-2,-2,+5,-1,-2 | R,U,U,D,D,U,D,D | S,S,L,S,S,S,S,L |
| 33 | Ballade No.1 | Chopin | Ballade No.1 Op.23 | +0,-1,+3,-2,+2,+2,-2,-1 | R,D,U,D,U,U,D,D | L,S,L,S,S,L,S,L |
| 34 | Nocturne Op.9/2 | Chopin | Nocturne Op.9 No.2 | +0,+4,-2,+5,-3,-2,+2,-4 | R,U,D,U,D,D,U,D | L,S,S,L,S,S,S,L |
| 35 | Heroic Polonaise | Chopin | Polonaise Op.53 | +0,+0,+0,+0,+2,-2,+4,-4 | R,R,R,R,U,D,U,D | S,S,S,S,S,S,S,L |
| 36 | Minute Waltz | Chopin | Waltz Op.64/1 | +0,-1,-2,-2,-1,-2,+2,+2 | R,D,D,D,D,D,U,U | S,S,S,S,S,S,S,S |
| 37 | Liebestraum | Liszt | Liebestraum No.3 | +0,+2,+2,+1,-5,+7,-2 | R,U,U,U,D,U,D | L,S,S,L,S,L,L |
| 38 | Hungarian Rhapsody 2 | Liszt | Hungarian Rhapsody No.2 | +0,-2,+2,+3,-3,-2,+4,-2 | R,D,U,U,D,D,U,D | S,S,S,S,S,S,S,L |
| 39 | Symphony 1 finale | Brahms | Symphony No.1 Op.68 | +0,+2,+2,+1,+2,-2,-1,-2,+2 | R,U,U,U,U,D,D,D,U | L,S,S,S,L,S,S,S,L |
| 40 | Lullaby | Brahms | Wiegenlied Op.49/4 | +0,+0,+4,-2,-1,+5,-2 | R,R,U,D,D,U,D | S,S,L,S,S,L,L |
| 41 | Hungarian Dance 5 | Brahms | Hungarian Dance No.5 | +0,+0,-3,+3,+0,-3,+3,-2 | R,R,D,U,R,D,U,D | S,S,S,S,S,S,S,L |
| 42 | Traumerei | Schumann | Kinderszenen Op.15/7 | +0,+5,+2,+2,-2,+2,-2,-5 | R,U,U,U,D,U,D,D | L,S,S,L,S,S,S,L |
| 43 | Spring Symphony | Schumann | Symphony No.1 Op.38 | +0,+4,+3,-3,-4,+7,+0 | R,U,U,D,D,U,R | L,S,S,S,S,L,L |
| 44 | Wedding March | Mendelssohn | Midsummer Night's Dream | +0,+0,+0,+7,-3,-4,+0,+0 | R,R,R,U,D,D,R,R | S,S,S,L,S,S,S,L |
| 45 | Violin Concerto | Mendelssohn | Violin Concerto Op.64 | +0,+2,-2,+5,-3,+3,-5 | R,U,D,U,D,U,D | L,S,S,L,S,L,L |
| 46 | Ride of Valkyries | Wagner | Die Walkure | +0,+4,+3,-3,+3,+5,-5 | R,U,U,D,U,U,D | S,S,S,S,S,L,S |
| 47 | Tristan chord passage | Wagner | Tristan und Isolde | +0,+6,-2,-1,+6,-2 | R,U,D,D,U,D | L,L,S,S,L,L |
| 48 | Bridal Chorus | Wagner | Lohengrin | +0,+0,+5,-2,-3,+5,-2 | R,R,U,D,D,U,D | L,L,L,S,S,L,L |

## Late Romantic (1880-1920)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 49 | Adagietto | Mahler | Symphony No.5 | +0,+3,+4,-2,-2,+5,-3 | R,U,U,D,D,U,D | L,L,L,S,S,L,L |
| 50 | Symphony 1 mvt.3 | Mahler | Symphony No.1 | +0,-5,+5,-5,+3,+2,-7 | R,D,U,D,U,U,D | L,L,L,S,S,S,L |
| 51 | Symphony 2 resurrection | Mahler | Symphony No.2 | +0,+2,+2,-2,+2,+1,-1,-2 | R,U,U,D,U,U,D,D | L,S,S,S,L,S,S,L |
| 52 | Also Sprach opening | R. Strauss | Also Sprach Zarathustra | +0,+7,+5,+4,-4,-5 | R,U,U,U,D,D | L,L,L,L,S,L |
| 53 | Don Juan | R. Strauss | Don Juan Op.20 | +0,+4,+3,+5,-3,-4,-5 | R,U,U,U,D,D,D | S,S,S,L,S,S,L |
| 54 | Enigma theme | Elgar | Enigma Variations Op.36 | +0,-2,+4,-2,-2,+5,-3 | R,D,U,D,D,U,D | L,S,L,S,S,L,L |
| 55 | Pomp & Circumstance | Elgar | Pomp & Circumstance No.1 | +0,+2,+2,-2,+2,+2,+1,-1 | R,U,U,D,U,U,U,D | L,L,L,L,L,L,S,L |
| 56 | Nimrod | Elgar | Enigma Variations (IX) | +0,+2,+2,+1,+2,-2,-1,-2 | R,U,U,U,U,D,D,D | L,L,L,L,L,S,S,L |
| 57 | Prelude to Afternoon | Debussy | Prelude a l'apres-midi | +0,-1,-1,-1,+4,-1,-1 | R,D,D,D,U,D,D | L,S,S,S,S,S,L |
| 58 | Vocalise | Rachmaninoff | Vocalise Op.34/14 | +0,-2,+5,-3,+1,+2,-3 | R,D,U,D,U,U,D | L,L,L,S,S,L,L |
| 59 | In the Hall Mountain King | Grieg | Peer Gynt Suite | +0,+2,+1,+2,+1,-1,-2,-1 | R,U,U,U,U,D,D,D | S,S,S,S,S,S,S,S |

## Nationalistic (1850-1920)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 60 | New World Largo | Dvorak | Symphony No.9 Op.95 | +0,+5,-2,-1,+1,-2,+4 | R,U,D,D,U,D,U | L,L,S,S,S,S,L |
| 61 | New World mvt.1 | Dvorak | Symphony No.9 Op.95 | +0,+2,+1,-1,+5,-2,-3 | R,U,U,D,U,D,D | S,S,S,S,L,S,L |
| 62 | Slavonic Dance 8 | Dvorak | Slavonic Dances Op.46/8 | +0,+2,+2,-2,+2,-2,-2 | R,U,U,D,U,D,D | S,S,S,S,S,S,L |
| 63 | Grieg PC opening | Grieg | Piano Concerto Op.16 | +0,-1,-2,-1,-2,-1,-2,-1 | R,D,D,D,D,D,D,D | L,S,S,S,S,S,S,L |
| 64 | Morning Mood | Grieg | Peer Gynt Suite | +0,+2,+2,+1,-1,-2,-2,+4 | R,U,U,U,D,D,D,U | L,L,S,S,S,S,S,L |
| 65 | Sibelius 2 finale | Sibelius | Symphony No.2 Op.43 | +0,+2,+1,+2,+2,-2,-1,-2 | R,U,U,U,U,D,D,D | L,L,L,L,L,S,S,L |
| 66 | Finlandia hymn | Sibelius | Finlandia Op.26 | +0,+2,+2,-2,+2,+2,-2,-2 | R,U,U,D,U,U,D,D | L,L,L,L,L,L,L,L |
| 67 | Valse Triste | Sibelius | Valse Triste Op.44 | +0,-2,-1,+3,-3,+1,+2 | R,D,D,U,D,U,U | L,S,S,L,S,S,L |
| 68 | Moldau | Smetana | Ma Vlast | +0,+2,+2,+1,+2,-2,-1,-2 | R,U,U,U,U,D,D,D | S,S,S,S,L,S,S,L |
| 69 | Polovtsian Dances | Borodin | Prince Igor | +0,+2,+1,+2,-2,+2,-1,-2 | R,U,U,U,D,U,D,D | L,L,S,L,S,L,S,L |
| 70 | Pictures Promenade | Mussorgsky | Pictures at Exhibition | +0,+2,+3,-2,+4,-3,-2,+2 | R,U,U,D,U,D,D,U | L,S,S,S,L,S,S,L |

## Impressionist (1890-1930)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 71 | Clair de Lune | Debussy | Suite Bergamasque | +0,+2,+1,-1,+3,-2,-1 | R,U,U,D,U,D,D | L,S,L,S,L,S,L |
| 72 | Arabesque No.1 | Debussy | Deux Arabesques | +0,+2,+2,+1,+2,-2,-1,-2 | R,U,U,U,U,D,D,D | S,S,S,S,S,S,S,S |
| 73 | La Mer opening | Debussy | La Mer | +0,+5,-5,+7,-2,-5 | R,U,D,U,D,D | L,S,S,L,S,L |
| 74 | Reverie | Debussy | Reverie | +0,-2,+4,-2,+3,-1,-2 | R,D,U,D,U,D,D | L,S,L,S,L,S,L |
| 75 | Bolero | Ravel | Bolero | +0,+2,-2,+2,+1,-3,+2,+2,-2 | R,U,D,U,U,D,U,U,D | S,S,S,S,S,S,S,S,L |
| 76 | Pavane | Ravel | Pavane pour une infante defunte | +0,-2,-2,+4,-2,+2,-2 | R,D,D,U,D,U,D | L,S,L,S,S,L,L |
| 77 | Daphnis sunrise | Ravel | Daphnis et Chloe Suite 2 | +0,+2,+2,+1,+2,+2,+1 | R,U,U,U,U,U,U | L,S,S,S,S,S,L |
| 78 | Gymnopedies No.1 | Satie | Trois Gymnopedies | +0,-3,-4,+5,+2,-3,-2 | R,D,D,U,U,D,D | L,L,L,L,L,L,L |

## Modern (1900-1975)

| # | Theme | Composer | Work | Intervals | Parsons | Rhythm |
|---|-------|----------|------|-----------|---------|--------|
| 79 | Rite of Spring | Stravinsky | Rite of Spring | +0,+2,-2,+2,+2,-2,-2 | R,U,D,U,U,D,D | S,S,S,S,L,S,S |
| 80 | Firebird finale | Stravinsky | Firebird Suite | +0,+2,+2,+1,-1,+1,+2,-2 | R,U,U,U,D,U,U,D | L,L,S,S,S,S,L,L |
| 81 | Peter's theme | Prokofiev | Peter and the Wolf | +0,+2,+2,+1,+2,-2,-5 | R,U,U,U,U,D,D | S,S,S,S,L,S,L |
| 82 | Dance of Knights | Prokofiev | Romeo & Juliet Op.64 | +0,-5,+5,+0,-5,+5,+2 | R,D,U,R,D,U,U | L,S,S,S,S,S,L |
| 83 | Piano Concerto 3 | Prokofiev | PC No.3 Op.26 | +0,+2,-2,+4,-2,-2,+5 | R,U,D,U,D,D,U | S,S,S,S,S,S,L |
| 84 | Rhapsody in Blue | Gershwin | Rhapsody in Blue | +0,+2,+2,+3,+5,+2,-2 | R,U,U,U,U,U,D | S,S,S,S,L,S,L |
| 85 | Appalachian Spring | Copland | Appalachian Spring | +0,+4,+3,-3,+5,-2,-3 | R,U,U,D,U,D,D | L,S,S,S,L,S,L |
| 86 | Fanfare Common Man | Copland | Fanfare for Common Man | +0,+7,+5,-5,+3,+2 | R,U,U,D,U,U | L,L,L,S,S,L |
| 87 | Planets Mars | Holst | The Planets - Mars | +0,+0,+0,+3,+2,-5,+3 | R,R,R,U,U,D,U | S,S,S,S,S,S,L |
| 88 | Planets Jupiter | Holst | The Planets - Jupiter | +0,+2,+2,-2,+2,+2,-2,-2 | R,U,U,D,U,U,D,D | L,L,L,L,L,L,L,L |
| 89 | Carmina Burana | Orff | O Fortuna | +0,+0,+2,-2,+0,+0,-2,+2 | R,R,U,D,R,R,D,U | S,S,S,S,S,S,S,L |
| 90 | Adagio for Strings | Barber | Adagio for Strings Op.11 | +0,+2,+1,+2,-1,+3,-2,-3 | R,U,U,U,D,U,D,D | L,L,L,L,S,L,S,L |

## Matching Criteria

### Plagiarism Detection Thresholds

| Match Type             | Threshold       | Action                              |
|------------------------|-----------------|--------------------------------------|
| Exact interval match   | 6+ consecutive  | Flag as potential plagiarism         |
| Parsons contour match  | 8+ consecutive  | Flag for review                      |
| Transposed match       | 6+ intervals    | Flag (same intervals, different key) |
| Rhythmic + contour     | 5+ simultaneous | High confidence flag                 |
| Inverted match         | 7+ intervals    | Note as possible unconscious quote   |
| Retrograde match       | 8+ intervals    | Low concern; note for reference      |

### Comparison Algorithm

```
For each candidate theme:
  1. Extract interval sequence (semitone deltas)
  2. Extract Parsons code (U/D/R contour)
  3. Sliding window comparison against all indexed themes:
     a. Interval match: count consecutive matches
     b. Contour match: count consecutive U/D/R matches
     c. Allow +/-1 semitone tolerance for "near match"
  4. Check all 12 transpositions
  5. Check inversion and retrograde
  6. Report matches exceeding thresholds
```

### Safe Modifications to Avoid Matches

| Technique                  | Effect on Interval Sequence           |
|----------------------------|---------------------------------------|
| Change one interval        | Breaks consecutive match              |
| Alter rhythm               | Different character despite intervals |
| Add passing tones          | Inserts new intervals in sequence     |
| Octave displacement        | Changes specific intervals by +/-12   |
| Chromatic alteration       | Shifts intervals by +/-1             |
| Reorder phrase segments    | Breaks window match                   |
| Change mode (major/minor)  | Alters 3rd/6th/7th intervals         |

## Usage Notes

- This index covers the most recognizable openings and main themes
- Inner themes, secondary themes, and development motifs are not indexed
- Rhythmic profile is approximate; exact rhythm matching uses separate logic
- Index should be updated as new famous works enter common knowledge
- For living composers' works, copyright applies regardless of melodic similarity
