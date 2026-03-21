---
name: w-research
description: "Research unknown composers or styles via web search. Build temporary composer profiles for Wolfgang composition."
argument-hint: "<piece-id> <composer-name>"
---

# /w-research -- Build Composer Profile from Web Research

You are researching a composer to build a compositional profile that the Wolfgang pipeline can use during generation. Parse the arguments to extract the piece-id and composer-name.

## Step 1: Initial Research

Use WebSearch to gather comprehensive information about the composer. Run multiple searches:

1. **"[composer-name] compositional style analysis"** -- for overviews of their approach
2. **"[composer-name] harmonic language techniques"** -- for harmony specifics
3. **"[composer-name] orchestration"** -- for instrumentation preferences
4. **"[composer-name] most important works list"** -- for representative pieces
5. **"[composer-name] musical innovations contributions"** -- for signature devices
6. **"[composer-name] biography musical education influences"** -- for context and influences

If the composer is very obscure and initial searches return little, broaden:
- Search for the composer's nationality/era + "composers" to find them in lists
- Search for specific works if known
- Search music encyclopedia entries

## Step 2: Build the Profile

Construct a composer profile in dense, tabular format matching the existing profiles in `.claude/context/`. The profile should be approximately 150-200 lines and follow this structure:

```markdown
# [Composer Full Name] ([Birth Year]-[Death Year]) -- Composer Profile

## Quick Reference
| Attribute | Value |
|-----------|-------|
| Era | [Baroque/Classical/Romantic/Modern/etc.] |
| Nationality | [Country] |
| Active Period | [Year range] |
| Primary Forms | [Symphony, Opera, Chamber, etc.] |
| Harmonic Language | [Brief descriptor] |
| Melodic Character | [Brief descriptor] |
| Rhythmic Character | [Brief descriptor] |
| Key Influences | [Names] |
| Influenced | [Names] |

## Harmonic Language
[Dense paragraph on harmonic practices: preferred progressions, cadential patterns,
chromaticism level, modulation habits, use of dissonance, pedal tones, etc.]

| Technique | Usage | Example Context |
|-----------|-------|-----------------|
| [e.g., Augmented sixths] | [Frequency/context] | [Which works] |
| ... | ... | ... |

## Melodic Style
[Dense paragraph on melodic construction: phrase lengths, contour preferences,
interval preferences, ornamentation, sequence usage, etc.]

### Characteristic Intervals and Contours
| Pattern | Frequency | Context |
|---------|-----------|---------|
| [e.g., Rising 4th opening] | Common | Heroic themes |
| ... | ... | ... |

## Rhythmic Characteristics
[Paragraph on rhythmic practices: preferred meters, rhythmic motifs,
syncopation usage, tempo relationships, rubato, etc.]

## Orchestration / Instrumentation
[Paragraph on orchestral palette: preferred instruments, doublings,
solo writing, texture preferences, dynamic range habits]

| Instrument/Section | Typical Role | Signature Usage |
|--------------------|-------------|-----------------|
| [e.g., Horns] | [Harmonic fill, heroic calls] | [Specific technique] |
| ... | ... | ... |

## Formal Innovations
[How the composer treats form: adherence to convention vs. innovation,
preferred structures, transition techniques, development strategies]

## Representative Works
| Work | Form | Key Features | Good Reference For |
|------|------|-------------|-------------------|
| [Title] | [Symphony/Sonata/etc.] | [Notable aspects] | [What to study it for] |
| ... | ... | ... | ... |

(List 8-12 representative works spanning their career)

## Signature Devices
[Bullet list of 5-10 distinctive compositional fingerprints that
distinguish this composer from contemporaries]

- **[Device name]**: [Description and context]
- ...

## ABC Notation Examples
Where possible, provide short ABC snippets illustrating characteristic patterns:

X:1
T:[Composer] - Characteristic melodic pattern
M:4/4
L:1/8
K:[key]
[4-8 bars illustrating a typical melodic gesture]

X:2
T:[Composer] - Characteristic harmonic progression
M:4/4
L:1/4
K:[key]
[Short chord progression in ABC]

(Include 2-4 ABC examples if enough information is available to construct them
accurately. If not enough detail is known, omit rather than fabricate.)

## Style Summary for Generation
[A concise paragraph that a composition engine can use as a prompt:
"When composing in the style of [composer], prioritize X, Y, Z.
Avoid A, B, C. The texture should tend toward... The harmonic rhythm
typically moves at... Melodies characteristically..."]
```

## Step 3: Save the Profile

1. Ensure the directory `workspace/<piece-id>/research/` exists.
2. Write the profile to `workspace/<piece-id>/research/<composer-name>.md` (use lowercase, hyphens for spaces in filename).

## Step 4: Offer Permanent Save

Ask the user:

> "Composer profile for [Name] saved to workspace/<piece-id>/research/. Would you like to save this permanently to the context library? If so, which genre directory should it go in?"

If the user confirms, determine the appropriate genre directory from the existing structure under `.claude/context/` and copy the profile to `.claude/context/<genre>/composer-profiles/<composer-name>.md`.

## Quality Standards

- **Accuracy over completeness**: Only include information that WebSearch actually found. Do not fabricate compositional details. If information is sparse, note gaps explicitly: "Limited information available on orchestration preferences."
- **Dense tables**: Prefer tabular format over long prose. Tables are faster to scan during generation.
- **ABC examples**: Only include ABC notation if you have enough concrete information (specific themes, known progressions) to write them accurately. A shorter, accurate profile is better than a longer one with guesses.
- **Cross-reference**: If the composer is known to have influenced or been influenced by composers already in the context library, note those connections.
- **Target length**: 150-200 lines. Shorter is acceptable for obscure composers with limited available information. Do not pad with speculation.

## Report

Print a summary:
- Composer name and era
- How much information was found (rich / moderate / sparse)
- Key stylistic takeaways (3-5 bullets)
- File location
- Whether permanent save was offered
