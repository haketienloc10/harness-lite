Implement a small arithmetic expression evaluator in this repository.

Create `src/calculator.py` defining:

    def evaluate(expression: str) -> float

It evaluates an infix arithmetic expression and returns the result as a float.

Grammar / behavior:

- Operators: `+`, `-`, `*`, `/` with standard precedence (`*` and `/` bind
  tighter than `+` and `-`) and left associativity.
- Parentheses `(` `)` group sub-expressions to arbitrary depth.
- Unary minus is supported (e.g. `-3`, `2 * -4`, `-(1 + 2)`).
- Operands are non-negative integer or decimal literals (e.g. `3`, `3.5`,
  `.5`, `10.`). Whitespace between tokens is insignificant.
- Examples: `"1 + 2 * 3"` -> `7.0`; `"(1 + 2) * 3"` -> `9.0`;
  `"-2 + 4 / 2"` -> `0.0`; `"2 * (3 + -1)"` -> `4.0`.

Errors:

- Division by zero must raise `ZeroDivisionError`.
- Any malformed input must raise `ValueError` — this includes an empty or
  whitespace-only string, an unknown character, an unbalanced parenthesis, a
  missing operand, or trailing/garbage tokens.

Add unit tests under `tests/` that thoroughly cover the behavior, including
precedence, parentheses, unary minus, decimals, and **every error path**. The
code must be importable as `from calculator import evaluate` (i.e. `src/` on the
path).
