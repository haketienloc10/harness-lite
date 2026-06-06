Implement a small, well-tested function in this repository.

Create `src/password.py` defining:

    def password_strength(password: str) -> str

Scoring rules — award one point for each rule the password satisfies:

1. length is at least 8 characters
2. contains at least one lowercase letter
3. contains at least one uppercase letter
4. contains at least one digit
5. contains at least one symbol (any non-alphanumeric character)

Return value based on the total points:

- 0, 1 or 2 points  -> "weak"
- 3 or 4 points     -> "medium"
- 5 points          -> "strong"

An empty string returns "weak".

Add unit tests under `tests/` that cover the behavior thoroughly (each label
and the boundary cases). The code must be importable as `from password import
password_strength` (i.e. `src/` on the path).
