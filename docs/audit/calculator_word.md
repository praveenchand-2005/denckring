# calculator_word

*Audited 2026-09-19. The 2026-08-31 pass's source text is not preserved in the repository; this pass uses a freshly chosen ordinary text.*

| | |
|---|---|
| kind | `both` |
| family | `letter` |
| checkability | `self` |
| generator | yes |
| requires | `fold_diacritics`, `lexicon.words`, `tokens` |
| declares | en, de, fr |
| runs in | en, de, fr |

**Verdict: refused the probe.**

## Checked against an ordinary text

- **en** — satisfied: `False`, score `0.0`, violations: `wrong_word_count`, `undisplayable_letter`, `undisplayable_letter`, `undisplayable_letter` (103 total)
- **de** — satisfied: `False`, score `0.0`, violations: `wrong_word_count`, `undisplayable_letter`, `undisplayable_letter`, `undisplayable_letter` (110 total)
- **fr** — satisfied: `False`, score `0.0`, violations: `wrong_word_count`, `undisplayable_letter`, `undisplayable_letter`, `undisplayable_letter` (99 total, including 2 `not_a_word`)

An ordinary paragraph is neither one word nor writable on a seven-segment display, so this is the expected shape of failure, not a finding.

## Generated from it

`apply` reads the positional text itself as the digit string to decode (`digits` defaults to `"7353"` only when no text is given), so handing it an ordinary paragraph is a direct, honest probe rather than an invented parameter.

- **en** — refused: `InvalidParams: Invalid parameters for procedure 'calculator_word': the text to apply must be a string of digits`
- **de** — refused: `InvalidParams: Invalid parameters for procedure 'calculator_word': the text to apply must be a string of digits`
- **fr** — refused: `InvalidParams: Invalid parameters for procedure 'calculator_word': the text to apply must be a string of digits`

## Findings

Refused the probe honestly rather than failing: the text does not suit this generator, and the refusal names why.

- en: apply raised InvalidParams
- de: apply raised InvalidParams
- fr: apply raised InvalidParams
