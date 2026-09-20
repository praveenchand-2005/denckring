# 44. Third-party language packs are upgrade-only, not a new-language mechanism

## Context

An external review (docs/feedback/DENCKRING_CODE_REVIEW.md, P2-04) noted a real
tension: `Lang = Literal["en", "de", "fr"]` closes the type system to three
languages, while the README promises the `denckring.lang` entry-point group
stays stable "so an installed third-party pack keeps working" — a promise a
reader could take as "third-party packs can add new languages."

That reading was never quite what the mechanism does. Every existing entry
point (`denckring-de-data`, `denckring-fr-data` and friends) replaces or
upgrades one of the three built-in defaults (`lang/__init__.py`'s
`_DEFAULTS`); none registers a language outside `Lang`. `Meta.names`,
`Meta.definitions`, `Meta.languages` and `Description.runs_in` are all typed
or built against the closed `Lang` literal (`describe.py`'s `get_args(Lang)`),
so a fourth language's pack could load via the entry-point group (`get_pack`
takes a bare `str`) but could not appear in any typed catalogue surface — it
would be reachable and functionally inert everywhere that matters to a
caller.

## Decision

Third-party language packs are **upgrade-only**: an entry point in the
`denckring.lang` group may replace or extend the data behind `en`, `de` or
`fr`, and nothing else. `Lang` stays a closed three-member `Literal`. This is
not a new restriction — it is what the mechanism has always actually done —
but it is now a decision on record rather than an implicit fact a reader had
to reverse-engineer from the type signature.

The alternative (open language plugins: a validated string type, `runs_in`
built from `installed_languages()` rather than `get_args(Lang)`) was
considered and rejected for this pass. It is a larger API surface — every
typed field carrying `Lang` today would need to become a runtime-validated
string, and every caller relying on `Lang`'s closed set for exhaustiveness
(the CLI's language options, `Description.runs_in`, the catalogue's
`names`/`definitions` mappings) would need re-auditing. Nothing in the
current catalogue asks for a fourth language; building the open mechanism
before a caller asks is the mistake ADR 0015 already names.

## Consequences

**The README's promise is now scoped in words, not only in behavior.**
`README.md`'s "What is stable" section names the `denckring.lang`
entry-point group and "the capability names a pack declares" as stable, and
now says explicitly that a third-party pack replaces or extends one of the
three shipped languages rather than registering a new one.

**A fourth language is still possible, later, as a real decision.** If a
caller asks for one, ADR 0028's own closing note on German's
`lexicon.graded_words` gap already establishes the pattern: an open question
gets its own ADR when someone needs it, not preemptively. Revisiting this
decision means the larger refactor sketched above, not a config flag.

**`get_pack()` itself is unchanged and stays permissive.** It accepts any
`str`, so a plugin author who registers `"es"` today gets no error at
install or discovery time — only silence everywhere the closed `Lang` type
gates a typed surface. That asymmetry (loadable but functionally invisible)
is the cost of not validating at the entry-point boundary; closing it means
either rejecting unknown language ids at `register_pack`/`_install`, which
this decision does not do, or the open-plugin redesign above.
