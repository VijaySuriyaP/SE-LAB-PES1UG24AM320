# Lab 5 – Issues found in `society_dues.py`

Line numbers refer to the **original** file. Raw reports: `reports/before/` and `reports/after/`.

| Score | Pylint | Bandit | Flake8 |
|-------|--------|--------|--------|
| Before | 5.81/10 | 3 issues (1 Low, 2 Medium) | 5 issues |
| After | 10.00/10 | 0 issues | 0 issues |

## Issue table (high/medium severity first)

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 1 | SQL injection (Bandit B608, CWE-89, Medium) | Security | 9 | `addDue` builds the INSERT with an f-string, so a flat name like `X'); DROP TABLE dues;--` is executed as SQL. (`collect` was already parameterized, so the code was inconsistent.) | Use `?` placeholders: `conn.execute("INSERT INTO dues VALUES (?, ?, ?, 0)", (flat, month, amount))`. |
| 2 | Use of `eval` (Bandit B307 / Pylint W0123, Medium) | Security | 21 | `penalty(rule)` runs `eval()` on caller-supplied text, so `__import__('os').system(...)` would run arbitrary commands. | Replace with an `ast`-based evaluator (`_safe_eval`) that only accepts numbers and `+ - * / // %`. `penalty("50 * 2")` still returns 100; anything else returns 0. `**` is deliberately excluded so `2**9999999` can't hang the program. |
| 3 | Mutable default argument (Pylint W0102) | Bug | 8 | `history=[]` is created once and shared by every call that omits it, so entries leak between unrelated calls. | Default to `None`; create a new list inside the function. Verified two calls now return different lists. |
| 4 | Broad exception caught (Pylint W0718) | Bug / Style | 22 | `except Exception` hides every error, including real bugs. | Catch only what the evaluator can raise: `SyntaxError, ValueError, TypeError, ArithmeticError, AttributeError, RecursionError`. |
| 5 | Hardcoded password (Bandit B105, CWE-259, Low) | Security | 5 | `TREASURER_PASSWORD = "flat#101"` is committed to source control. | Read it from the environment: `os.environ.get("TREASURER_PASSWORD", "")`. (The constant is currently unused by the program.) |
| 6 | Inconsistent return (Pylint R1710) | Bug | 12-16 | `collect` returns the amount when the due exists but falls off the end (implicit `None`) otherwise. | Add an explicit `return None` and document it in the docstring. |
| 7 | Comparison to `None` with `!=` (Pylint C0121 / Flake8 E711) | Style | 29 | `rows != None` should use identity. The check is also dead code: `fetchall()` always returns a list. | Removed the check and return the list comprehension directly. |
| 8 | Function name not snake_case (Pylint C0103) | Style | 8 | `addDue` violates PEP 8 naming. | Renamed to `add_due` and updated the call sites in `main()`. |
| 9 | Missing docstrings (Pylint C0114, C0116) | Style | 1, 8, 12, 19, 27, 34 | Module and all functions undocumented. | Added a module docstring and a docstring per function. |
| 10 | Line too long (Flake8 E501 / Pylint C0301) | Style | 4, 13, 15 | Lines of 87, 104 and 92 characters exceed the 79-character limit. | Wrapped the SQL statements and call arguments across lines. |
| 11 | Missing blank lines (Flake8 E302) | Style | 12 | No blank lines between `addDue` and `collect`. | Added two blank lines. |
| 12 | Demo runs on import (found by reading, not reported by the tools) | Bug | 42 | `main()` was called at module level, so importing the module ran the demo. | Wrapped in `if __name__ == "__main__":`. |

All 12 rows were fixed (the handout requires at least 4). Every finding from Bandit, Pylint and Flake8 is resolved.

## Commits

1. `Fix Bandit findings` – rows 1, 2, 4, 5
2. `Fix Pylint findings` – rows 3, 6, 7, 8, 9, 12
3. `Fix Flake8 findings` – rows 10, 11
