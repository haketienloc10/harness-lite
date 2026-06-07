Implement a semantic-version range matcher in this repository.

Create `src/semver.py` defining:

    def satisfies(version: str, range_spec: str) -> bool

It returns `True` when `version` falls inside the set described by
`range_spec`, following (a practical subset of) the semver range grammar.

Versions:

- A version is `MAJOR.MINOR.PATCH` (e.g. `1.2.3`), optionally with a
  pre-release suffix (`1.2.3-alpha.1`) and/or build metadata (`1.2.3+build.5`).
- Build metadata is ignored for all comparisons.
- Ordering is the usual semver ordering, including pre-release precedence
  (`1.2.3-alpha` < `1.2.3-alpha.2` < `1.2.3-beta` < `1.2.3`).

Range grammar (whitespace between tokens is insignificant):

- Comparators: `>`, `>=`, `<`, `<=`, `=` (or a bare version, meaning `=`).
- Caret `^1.2.3` allows changes that do not modify the left-most non-zero
  component (`^1.2.3` := `>=1.2.3 <2.0.0`; `^0.2.3` := `>=0.2.3 <0.3.0`;
  `^0.0.3` := `>=0.0.3 <0.0.4`).
- Tilde `~1.2.3` := `>=1.2.3 <1.3.0`; `~1.2` := `>=1.2.0 <1.3.0`;
  `~1` := `>=1.0.0 <2.0.0`.
- X-ranges: `*` (or empty string) matches any version; `1.x` / `1.*` :=
  `>=1.0.0 <2.0.0`; `1.2.x` := `>=1.2.0 <1.3.0`. Partial versions like `1` and
  `1.2` behave as the matching x-range.
- Hyphen ranges: `1.2.3 - 2.3.4` := `>=1.2.3 <=2.3.4`.
- Space-separated comparators are ANDed; ` || ` separates ORed alternatives,
  e.g. `^1.0.0 || >=2.5.0 <3.0.0`.

Return value is a plain `bool`. Invalid input must raise `ValueError` — this
includes a malformed `version` and a malformed `range_spec`.

Examples:

- `satisfies("1.2.3", ">=1.0.0 <2.0.0")` -> `True`
- `satisfies("1.2.3", "^1.0.0")` -> `True`
- `satisfies("2.0.0", "^1.0.0")` -> `False`
- `satisfies("1.2.3", "1.x")` -> `True`
- `satisfies("1.2.3", "1.2.3 - 2.0.0")` -> `True`
- `satisfies("3.0.0", "^1.0.0 || >=2.5.0 <3.0.0")` -> `False`

Add unit tests under `tests/` that thoroughly cover the behaviour, including
the parts that are easy to overlook. The code must be importable as
`from semver import satisfies` (i.e. `src/` is on the path).
