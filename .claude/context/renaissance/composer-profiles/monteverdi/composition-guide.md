# Monteverdi — Composition Guide

## Fingerprints
Any section claiming Monteverdi's style needs ≥3 of these 5 present.

1. **The words choose the notes** — Text expression outranks contrapuntal propriety, and Monteverdi said so in print when he was attacked for it. A harsh word gets a harsh interval; "sospiro" gets a rest that breaks the line mid-word. If a passage would be equally good with different text under it, it is not in this style.
2. **Unprepared dissonance for expressive effect** — The *seconda pratica* keeps Renaissance technique as the default and breaks it deliberately: an unprepared seventh or a dissonant leap where the meaning demands it. The rule-breaking only registers because everything around it observes the rule.
3. **Declamatory, speech-shaped rhythm** — Repeated notes on one pitch following the natural stresses of the line, then a sudden melisma where a single word opens out. The rhythm is closer to heightened speech than to a tune.
4. **Abrupt textural contrast between phrases** — A homorhythmic block of all voices declaiming together, then a single voice alone, then paired imitation. The changes are sudden and align with the sense of the text rather than with a formal scheme.
5. **Chromatic inflection at the moment of feeling** — A raised or lowered third, a cross-relation between voices, a shift toward the flat side for grief. Used at one specific word, not as a general colouring.

---

## What separates him from Palestrina

Monteverdi has the older technique fully in hand and departs from it *on purpose*, at chosen moments. Write the Renaissance idiom correctly and then break exactly one rule where the text asks for it — not several rules everywhere, which is merely incompetent counterpoint, and not none, which is Palestrina.

## See also
- [../../renaissance-harmony.md](../../renaissance-harmony.md)
- [../palestrina/composition-guide.md](../palestrina/composition-guide.md) — the practice this one departs from

---

## Composing a madrigal phrase: step by step

The procedure is Palestrina's, run until one word demands that it break. Write
the Renaissance idiom correctly, then break exactly one rule where the text asks
— not several everywhere, which is merely incompetent counterpoint, and not
none, which is Palestrina.

### Step 1 — Speak the line and mark the stresses

The rhythm comes from the words before any pitch is chosen. Repeated notes on
one pitch carry the unstressed syllables; the stressed one gets length or
height, never both by accident.

```json
"declamation": [
  {"p": "A4", "d": "q"},
  {"p": "A4", "d": "q"},
  {"p": "A4", "d": "q"},
  {"p": "C5", "d": "h"},
  {"p": "B4", "d": "q"},
  {"p": "A4", "d": "h"}
]
```

Three repeated A4s are the unstressed syllables; C5 is the accented one. If the
passage would be equally good under different words, it is not in this style.

### Step 2 — Set the whole phrase correctly first

Prepared dissonance, stepwise recovery from leaps, arch shape. Everything
Palestrina would accept. The rule-breaking in Step 4 only registers because
everything around it observes the rule.

### Step 3 — Find the ONE word that hurts

*Dolore*, *morte*, *sospiro*, *crudele*. One per phrase. Mark it before writing
the harmony.

### Step 4 — Break the rule at that word, and only there

An unprepared seventh, struck without preparation and left by step:

```json
"unprepared_seventh": [
  {"p": "G4", "d": "h"},
  {"p": "F5", "d": "h", "dyn": "mf"},
  {"p": "E5", "d": "h"},
  {"p": "D5", "d": "w"}
]
```

The F5 arrives as a seventh over a G in the bass with nothing preparing it. In
Palestrina this is an error; here it is the meaning of the word.

Or a rest that breaks the line mid-word, for *sospiro* — a sigh:

```json
"broken_sigh": [
  {"p": "E5", "d": "q"},
  {"p": "rest", "d": "e"},
  {"p": "D5", "d": "e"},
  {"p": "C5", "d": "h"}
]
```

### Step 5 — Change the texture at the sense, not at a bar line

Homorhythmic block for a line of collective statement, one voice alone for a
personal one, paired imitation for dialogue. The changes are sudden and align
with the text.

```json
"homorhythmic_block": [
  {"p": ["D4", "F4", "A4", "D5"], "d": "h"},
  {"p": ["C4", "E4", "G4", "C5"], "d": "h"},
  {"p": ["D4", "F4", "A4", "D5"], "d": "w"}
]
```

### Step 6 — Colour the third at the moment of feeling

A raised or lowered third, or a cross-relation between two voices, on one word.
Grief moves toward the flat side. Used at one specific word, never as a general
wash.

---

## Checking a finished phrase

- Could you name the one word the music is about?
- Is there exactly one broken rule, and does it fall on that word?
- Does the rhythm follow the spoken stresses, or a musical pattern?
- Does the texture change where the sense changes, or where the bar line falls?
