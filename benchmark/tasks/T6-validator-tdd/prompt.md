Implement a small, well-tested function in this repository.

Create `src/username.py` defining:

    def normalize_username(raw: str) -> str

Normalization rules, applied in order:

1. Strip leading and trailing whitespace.
2. Convert to lowercase.
3. Replace any run of internal whitespace with a single underscore (`_`).
4. Drop every character that is not a lowercase letter, a digit, or `_`.
5. Collapse any run of consecutive underscores into one, then strip leading and
   trailing underscores.

Validation (raise `ValueError` with a clear message):

- If the result is empty, raise `ValueError`.
- If the result is longer than 30 characters, raise `ValueError`.

Examples:

- `"  Alice Smith "` -> `"alice_smith"`
- `"Bob__99!!"`       -> `"bob_99"`
- `"   "`             -> raises `ValueError`

Add unit tests under `tests/` that cover each rule, both error cases, and the
boundary at 30 characters. The code must be importable as
`from username import normalize_username` (i.e. `src/` on the path).
