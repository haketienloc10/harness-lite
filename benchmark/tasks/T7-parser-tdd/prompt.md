Implement a small, well-tested function in this repository.

Create `src/duration.py` defining:

    def parse_duration(text: str) -> int

Parse a compact duration string into a total number of **seconds**. The string
is a sequence of `<number><unit>` segments with no spaces, where unit is one of:

- `h` — hours   (3600 seconds)
- `m` — minutes (60 seconds)
- `s` — seconds (1 second)

Rules:

- Segments may appear in any order and a unit may appear at most once.
- The match is case-insensitive (`"1H30M"` is valid).
- Examples: `"1h30m"` -> `5400`, `"45s"` -> `45`, `"2h"` -> `7200`.

Validation (raise `ValueError` with a clear message):

- Empty string, or a string that does not fully match the grammar.
- A unit repeated more than once (e.g. `"1h1h"`).

Add unit tests under `tests/` that cover each unit, mixed segments,
case-insensitivity, and both error cases. The code must be importable as
`from duration import parse_duration` (i.e. `src/` on the path).
