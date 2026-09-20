# portmanteau

*Audited 2026-09-19. The 2026-08-31 pass's source text is not preserved in the repository; this pass uses a freshly chosen ordinary text.*

| | |
|---|---|
| kind | `both` |
| family | `word` |
| checkability | `source` |
| generator | yes |
| requires | `lexicon.words`, `phonemes`, `tokens` |
| declares | en, de, fr |
| runs in | en, de, fr |

**Verdict: refused the probe.**

## Checked against an ordinary text

`check` requires both `source` and `splice`. Unlike rows whose only required field is `source` (which the original pass exercised by checking a text against itself), `splice` names a specific word to look for inside the text and has no honest self-supplied value — inventing one would be tuning the probe rather than running it against ordinary prose. Not exercised.

- **en** — not exercised: needs ['source', 'splice'].
- **de** — not exercised: needs ['source', 'splice'].
- **fr** — not exercised: needs ['source', 'splice'].

## Generated from it

`apply`'s positional text is bound to `source` automatically (no `--source` needed, and no `splice` is required for `apply`), so this generator was run directly against the chosen text with no domain vocabulary supplied — the same "no extra parameter invented" rule used above.

- **en** — refused: `InvalidParams: Invalid parameters for procedure 'portmanteau': nothing to splice in; pass \`domain\` or \`domain_words\``
- **de** — refused: `InvalidParams: Invalid parameters for procedure 'portmanteau': nothing to splice in; pass \`domain\` or \`domain_words\``
- **fr** — refused: `InvalidParams: Invalid parameters for procedure 'portmanteau': nothing to splice in; pass \`domain\` or \`domain_words\``

## Findings

Refused the probe honestly rather than failing: the text does not suit this generator, and the refusal names why.

- en: apply raised InvalidParams
- de: apply raised InvalidParams
- fr: apply raised InvalidParams

**A documentation/behaviour mismatch, found and not fixed here.** The row's own catalogue notes (`uv run denckring show portmanteau --json` → `meta.notes`) state: *"`apply` is deliberately not shipped though `kind` says `both`. Generating a blend is choosing where to splice, which is Deri and Knight's multitape-FST problem and its own piece of work; `describe_procedure` will still report `both`, and the module docstring says so."* That is no longer accurate: `src/denckring/procedures/portmanteau.py`'s own module docstring documents a working generator ("`apply` generates by proposing splices and letting `check` dispose... the real name comes back first for 10 of 12 hosts"), and running `apply` above did execute that search — it reached the domain-vocabulary check inside `produce()` rather than failing as unimplemented or raising `NotConstructive`. The catalogue's `notes` field appears to predate the generator's implementation and was not updated. This is outside this task's scope (docs/audit backfill only) and is not corrected here; it is reported as a finding for the controller.
