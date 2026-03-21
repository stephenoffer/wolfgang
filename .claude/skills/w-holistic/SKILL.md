---
name: w-holistic
description: "Perform full-piece or movement-level coherence review for a Wolfgang composition. Checks thematic, tonal, and structural integrity."
argument-hint: "<piece-id> <'mini-review'|'movement-N'|'full-review'>"
---

# /w-holistic -- Coherence Review at Multiple Scales

You are performing a structural and thematic coherence review of a Wolfgang composition. Parse the arguments to extract the piece-id and review level. The review level is one of: `mini-review`, `movement-N` (where N is the movement number), or `full-review`.

---

## Review Level 1: mini-review

Trigger: invoked as `mini-review`, typically after every 10 sections of composition.

### Procedure

1. **Read state files:**
   - `workspace/<piece-id>/continuity.json` -- current compositional state
   - `workspace/<piece-id>/narrative-arc.json` -- planned intensity/emotional arc
   - `workspace/<piece-id>/themes.json` -- theme definitions and usage plan

2. **Check intensity arc:**
   - Compare the current intensity level (from continuity.json) against where the narrative-arc.json says it should be at this point
   - Is the piece tracking the planned arc, or has it drifted? (e.g., climax arriving too early, insufficient contrast)

3. **Check thematic usage:**
   - Which themes have been used so far vs. the usage_plan?
   - Are any themes overused (appearing too frequently, reducing their impact)?
   - Are any themes neglected that should have appeared by now?

4. **Check harmonic coverage:**
   - What key areas have been visited?
   - Are any regions over-visited (stuck in one key area too long)?
   - Is the tonal journey providing sufficient variety and direction?

5. **Output: 2-3 bullet points** with concise assessment. Keep it brief -- this is a checkpoint, not a deep analysis.

6. **Determine the current section number** from continuity.json and write to:
   `workspace/<piece-id>/holistic-reviews/mini_after_<section>.json`

   Format:
   ```json
   {
     "piece_id": "<piece-id>",
     "review_type": "mini-review",
     "after_section": <N>,
     "timestamp": "<ISO>",
     "intensity_arc": {
       "expected": "<descriptor or value>",
       "actual": "<descriptor or value>",
       "on_track": true|false,
       "note": "..."
     },
     "thematic_usage": {
       "on_track": true|false,
       "overused": ["theme_X"],
       "underused": ["theme_Y"],
       "note": "..."
     },
     "harmonic_coverage": {
       "regions_visited": ["I", "V", "vi", "IV"],
       "over_visited": [],
       "note": "..."
     },
     "bullets": [
       "Intensity arc is tracking well; approaching climax zone as planned.",
       "Theme B has not appeared since section 4; consider reintroducing.",
       "Harmonic variety is good; vi region used effectively for contrast."
     ],
     "action_items": []
   }
   ```

---

## Review Level 2: movement-N

Trigger: invoked as `movement-1`, `movement-2`, etc., after a complete movement is composed.

### Procedure

1. **Read ALL composed ABC files** for movement N. Gather every section file under `workspace/<piece-id>/abc/` that belongs to movement N.

2. **Read state and plan files:**
   - `workspace/<piece-id>/continuity.json`
   - `workspace/<piece-id>/themes.json`
   - `workspace/<piece-id>/narrative-arc.json`
   - `workspace/<piece-id>/plan.json` (for form and structure expectations)

3. **Thematic coherence check:**
   - Are all themes that should appear in this movement present?
   - Are themes presented consistently (same intervals, recognizable transformations)?
   - In sonata form: does the recapitulation reference exposition themes faithfully? Are they transposed to the home key?
   - In rondo form: does each refrain return match the original within acceptable tolerance (transposition, ornamentation, but core intervals preserved)?
   - In variation form: is the theme still recognizable in each variation?

4. **Tonal journey check:**
   - Map the key areas visited across the movement
   - Does the tonal plan follow convention for the form? (e.g., sonata: I -> V in exposition, tonal exploration in development, I throughout recap)
   - Are modulations prepared and resolved, or are there jarring unprepared key changes?
   - Does the movement end in the expected key?

5. **Intensity arc check:**
   - Plot the dynamic/textural intensity across the movement
   - Does it match the planned arc for this movement?
   - Is there a clear climax? Is it placed appropriately for the form?
   - Is there sufficient contrast between sections?

6. **Orchestral balance check:**
   - Are all instruments/voices given meaningful material?
   - Is any instrument silent for too long or overworked?
   - Are doublings used effectively or creating muddiness?

7. **Pacing check:**
   - Are any sections disproportionately long or short relative to the form?
   - Does the development feel rushed or drawn out?
   - Are transitions smooth or abrupt?

8. **Structural integrity check:**
   - Does the formal structure match the plan? (correct number of sections, themes in right places)
   - Are repeats, codas, and cadences where expected?

9. **Assign a coherence score: 1-10**
   - 9-10: Publishable quality, no issues
   - 7-8: Minor issues, easily addressed
   - 5-6: Notable issues that should be revised
   - 3-4: Significant structural problems
   - 1-2: Fundamental coherence failure

10. **Write to** `workspace/<piece-id>/holistic-reviews/movement_<N>.json`:

    ```json
    {
      "piece_id": "<piece-id>",
      "review_type": "movement-review",
      "movement": <N>,
      "timestamp": "<ISO>",
      "coherence_score": 8,
      "thematic_coherence": {
        "score": 8,
        "themes_present": ["A", "B", "closing"],
        "themes_missing": [],
        "issues": [],
        "notes": "Recapitulation faithfully returns Theme A in tonic. Theme B transposed correctly."
      },
      "tonal_journey": {
        "score": 7,
        "key_areas": ["Bb major", "F major", "G minor", "Bb major"],
        "issues": ["Modulation to G minor in development is slightly abrupt at bar 67"],
        "notes": "Overall tonal plan follows sonata convention."
      },
      "intensity_arc": {
        "score": 9,
        "climax_location": "development, bars 78-85",
        "issues": [],
        "notes": "Strong climax with effective build. Good contrast in recapitulation."
      },
      "orchestral_balance": {
        "score": 7,
        "issues": ["Violas have very little independent material in exposition"],
        "notes": "Good woodwind solos in development."
      },
      "pacing": {
        "score": 8,
        "issues": [],
        "notes": "Proportions well-balanced. Coda is perhaps slightly long."
      },
      "structural_integrity": {
        "score": 8,
        "form": "sonata",
        "sections_verified": true,
        "issues": [],
        "notes": "All expected sections present and correctly placed."
      },
      "recommendations": [
        "Consider adding a brief viola melody in the exposition transition.",
        "Smooth the modulation to G minor with a pivot chord at bar 66.",
        "Consider trimming the coda by 4 bars."
      ]
    }
    ```

---

## Review Level 3: full-review

Trigger: invoked as `full-review`, after all movements of the piece are complete.

### Procedure

1. **Read the full compositional state:**
   - `workspace/<piece-id>/continuity.json`
   - `workspace/<piece-id>/themes.json`
   - `workspace/<piece-id>/narrative-arc.json`
   - `workspace/<piece-id>/plan.json`
   - All previous holistic reviews in `workspace/<piece-id>/holistic-reviews/`

2. **Cross-movement thematic coherence:**
   - If a connecting motif or motto theme was planned, verify it appears in every movement
   - Check that thematic transformations across movements are audible and logical
   - Verify that any cyclical elements (themes returning in later movements) are present

3. **Cross-movement tonal journey:**
   - Map the key of each movement. Does the overall tonal plan make sense?
   - For multi-movement works: is there tonal variety between movements?
   - Does the final movement resolve to a satisfying tonal conclusion?
   - Standard patterns to verify:
     - Symphony in X major: check that final movement ends in X major
     - Minor-key works: does it end in minor (tragic) or major (triumphant)? Is this consistent with the narrative arc?

4. **Cross-movement emotional arc:**
   - Map the emotional trajectory across all movements
   - Is the overall arc satisfying? (e.g., tension-release-tension-resolution for 4 movements)
   - Is there sufficient contrast between movements in tempo, mood, and character?
   - Does the finale feel like a genuine conclusion, not just another movement?

5. **Consistency checks:**
   - Are instrument ranges consistent across movements?
   - Is the overall duration balanced? (No single movement disproportionately long)
   - Is the stylistic voice consistent? (No jarring shifts in harmonic language between movements)

6. **Compile previous review scores** from movement reviews. Note any issues that were flagged but not addressed.

7. **Final recommendations:**
   - Priority-ordered list of changes that would most improve the piece
   - Note which issues are critical vs. nice-to-have
   - Identify the strongest aspects to preserve

8. **Write to** `workspace/<piece-id>/holistic-reviews/full_review.json`:

    ```json
    {
      "piece_id": "<piece-id>",
      "review_type": "full-review",
      "timestamp": "<ISO>",
      "movements_reviewed": 4,
      "movement_scores": [8, 7, 9, 8],
      "overall_coherence_score": 8,
      "cross_movement_thematic": {
        "score": 8,
        "connecting_motif_present": true,
        "movements_with_motif": [1, 2, 3, 4],
        "cyclical_elements_verified": true,
        "issues": [],
        "notes": "Motto theme appears in all movements with appropriate transformation."
      },
      "cross_movement_tonal": {
        "score": 8,
        "movement_keys": ["Bb major", "Eb major", "G minor", "Bb major"],
        "tonal_arc_satisfying": true,
        "issues": [],
        "notes": "Traditional key relationships. Final movement resolves to tonic."
      },
      "cross_movement_emotional": {
        "score": 9,
        "arc_description": "Heroic opening -> Lyrical contrast -> Dark scherzo -> Triumphant finale",
        "contrast_sufficient": true,
        "finale_conclusive": true,
        "issues": [],
        "notes": "Strong emotional trajectory with effective contrast."
      },
      "consistency": {
        "instrument_ranges": "consistent",
        "duration_balance": "well-balanced",
        "stylistic_voice": "consistent",
        "issues": []
      },
      "previous_issues_unresolved": [
        "Movement 2: viola material still sparse in exposition"
      ],
      "final_recommendations": [
        {
          "priority": "high",
          "movement": 2,
          "recommendation": "Add independent viola line in exposition transition"
        },
        {
          "priority": "medium",
          "movement": 1,
          "recommendation": "Smooth G minor modulation in development"
        }
      ],
      "strengths": [
        "Excellent thematic unity across movements",
        "Strong emotional arc with satisfying finale",
        "Effective orchestral color throughout"
      ],
      "summary": "A well-constructed 4-movement work with strong thematic unity and emotional arc. Minor orchestration adjustments recommended in Movement 2. Overall coherence score: 8/10."
    }
    ```

---

## General Rules

- Ensure `workspace/<piece-id>/holistic-reviews/` directory exists before writing.
- Always use the current state of the piece, not assumptions about what should be there.
- If a required file (continuity.json, themes.json, etc.) is missing, report the gap and work with what is available. Do not fabricate data.
- Be specific in recommendations: cite section numbers, bar numbers (if available), theme names, and key areas.
- Keep mini-reviews concise (under 1 minute of reading). Save detailed analysis for movement and full reviews.

## Report

Print a summary appropriate to the review level:
- **mini-review**: The 2-3 bullet points plus any action items
- **movement-N**: Coherence score, top 3 issues, top 3 strengths
- **full-review**: Overall score, cross-movement assessment, prioritized recommendations
