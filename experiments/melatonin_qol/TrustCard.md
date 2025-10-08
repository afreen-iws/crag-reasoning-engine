# CRAG Trust Card

**Question:** Does melatonin improve quality of life of cancer patients?
**Studies analyzed:** 10

## Evidence Summary
- **Counts** → pro: 6, contra: 0, mixed: 1, unclear: 3
- **Balance** → pro: 0.6, contra: 0.0, mixed: 0.1, unclear: 0.3

**Representative PMIDs**
- **Pro**: PMID 40790573, PMID 40391256, PMID 38927992
- **Contra**: —
- **Mixed**: PMID 40625889

## Conclusion
Overall **weakly pro**: several studies report benefits, but conflicting or mixed evidence remains.

**Confidence:** 0.55

## Evidence Stability Metric (ESM)
- **Baseline conclusion:** Overall **weakly pro**: several studies report benefits, but conflicting or mixed evidence remains.
- **Baseline bucket:** mixed
- **Tests:** 6  |  **Flips:** 0  |  **ESM:** 1.0

**Counterfactual Scenarios**
- `drop_top3_pro` → bucket=mixed | n=7 | counts={'unclear': 3, 'pro': 3, 'mixed': 1, 'contra': 0}
- `drop_top3_mixed` → bucket=mixed | n=9 | counts={'pro': 6, 'unclear': 3, 'contra': 0, 'mixed': 0}
- `drop_all_pro` → bucket=mixed | n=4 | counts={'unclear': 3, 'mixed': 1, 'pro': 0, 'contra': 0}
- `drop_all_mixed` → bucket=mixed | n=9 | counts={'pro': 6, 'unclear': 3, 'contra': 0, 'mixed': 0}
- `drop_random3` → bucket=mixed | n=7 | counts={'pro': 4, 'unclear': 3, 'contra': 0, 'mixed': 0}
- `drop_random5` → bucket=mixed | n=5 | counts={'pro': 3, 'mixed': 1, 'unclear': 1, 'contra': 0}

_Generated: 2025-10-08 12:11:54 _