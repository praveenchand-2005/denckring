# paronomasia

*Audited 2026-09-19. The 2026-08-31 pass's source text is not preserved in the repository; this pass uses a freshly chosen ordinary text.*

| | |
|---|---|
| kind | `both` |
| family | `word` |
| checkability | `source` |
| generator | yes |
| requires | `phonemes`, `tokens` |
| declares | en, de, fr |
| runs in | en, de, fr |

**Verdict: clean.**

## Checked against an ordinary text

`source` is required and cannot be invented from a single ordinary text the way a self-contained row can; following the same construction the original pass used for other `checkability: source` rows whose only required field is `source` (`n_plus_7`, `s_plus_7`, `diastic`, `cut_up`, `mathews_algorithm`), the chosen text was checked against itself as its own `source`.

- **en** — satisfied: `False`, score `0.0`, violations: `no_displacement`
- **de** — satisfied: `False`, score `0.0`, violations: `no_displacement`
- **fr** — satisfied: `False`, score `0.0`, violations: `no_displacement`

An unmodified text displaces no word of itself, so `no_displacement` is the honest, expected outcome of this construction — it matches the row's own catalogued `unchanged-phrase-states-no-pun` example exactly.

## Generated from it

`apply`'s positional text is bound to `source` automatically (no `--source` needed), so the generator was run directly against the chosen text with no other parameters invented.

- **en** — 10 result(s) (truncated); first: `... under a heavy gray sky ...` (displaces `grey` → `gray`, distance 0.0)
  - round trip: checking the first result against the original as `source` — satisfied `True`, score `1.0`
- **de** — 10 result(s) (truncated); first: `... in Richtung der Küsste ...` (displaces `Küste` → `Küsste`, distance 0.0)
  - round trip: checking the first result against the original as `source` — satisfied `True`, score `1.0`
- **fr** — 10 result(s) (truncated); first: `Le train a quitter la gare ...` (displaces `quitté` → `quitter`, distance 0.0)
  - round trip: checking the first result against the original as `source` — satisfied `True`, score `1.0`
