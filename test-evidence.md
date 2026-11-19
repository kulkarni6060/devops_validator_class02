# Class 2 — Test evidence

Run date: 2026-11-19 · Python 3.10.11 · Windows 11 (PowerShell)

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Configuration accepted |
| `1` | Configuration rejected (one or more rules broken) |
| `2` | File missing, unreadable, or not in `KEY=value` format |

## How a peer can reproduce the tests

From the repository root, run all 20 cases with one command:

```bash
python3 run_tests.py      # Windows: py run_tests.py
```

Every line should say `PASS`, ending with `25/25 cases behaved as expected`.
`PASS` means the validator gave the **expected** result. For a bad file, that means
it was rejected with exit code 1 or 2. The runner also fails a case if the dummy
password `example-only-placeholder` ever appears in the output.

To run a single negative test by hand:

```powershell
# PowerShell
py validator.py test-cases/bad-port.env.example
$LASTEXITCODE        # expect 1
```

```bash
# bash
python3 validator.py test-cases/bad-port.env.example
echo "Exit code: $?"   # expect 1
```

To see a test fail on purpose, edit `test-cases/bad-port.env.example` and set
`APP_PORT=8080`. The validator now accepts it (exit 0), so `run_tests.py` reports
`FAIL` for that case.

## Manual run (PowerShell): 1 success, 4 failures

```text
PS> py validator.py valid.env.example
Configuration accepted
Exit code: 0

PS> py validator.py messy.env
APP_PORT: 'hello' is not a whole number (must be between 1024 and 65535)
DEBUG: 'true' is not allowed (must be exactly 'false' for deployment)
DB_PASSWORD: empty
Exit code: 1

PS> py validator.py test-cases/bad-port.env.example
APP_PORT: 80 is out of range (must be between 1024 and 65535)
Exit code: 1

PS> py validator.py test-cases/bad-debug-true.env.example
DEBUG: 'true' is not allowed (must be exactly 'false' for deployment)
Exit code: 1

PS> py validator.py test-cases/bad-db-host-legacy-only.env.example
DB_HOST: missing or empty (legacy key 'dbhost' is not accepted)
Exit code: 1
```

## Full test run (`python run_tests.py`)

| File | What it tests | Expected | Actual | Result |
|---|---|---:|---:|---|
| `valid.env.example` | all four rules satisfied | 0 | 0 | PASS |
| `test-cases/good-port-min-1024.env.example` | lowest allowed port | 0 | 0 | PASS |
| `test-cases/good-port-max-65535.env.example` | highest allowed port | 0 | 0 | PASS |
| `test-cases/good-quoted-values.env.example` | `APP_PORT="8080"` etc. are unquoted | 0 | 0 | PASS |
| `messy.env` | supplied broken file | 1 | 1 | PASS |
| `test-cases/bad-port.env.example` | port 80 (privileged) | 1 | 1 | PASS |
| `test-cases/bad-port-1023.env.example` | one below the minimum | 1 | 1 | PASS |
| `test-cases/bad-port-65536.env.example` | one above the maximum | 1 | 1 | PASS |
| `test-cases/bad-port-text.env.example` | `8080abc` | 1 | 1 | PASS |
| `test-cases/bad-port-negative.env.example` | `-8080` | 1 | 1 | PASS |
| `test-cases/bad-port-decimal.env.example` | `8080.5` | 1 | 1 | PASS |
| `test-cases/bad-port-empty.env.example` | empty port | 1 | 1 | PASS |
| `test-cases/bad-port-missing.env.example` | no `APP_PORT` key (peer review) | 1 | 1 | PASS |
| `test-cases/bad-debug-true.env.example` | `DEBUG=true` | 1 | 1 | PASS |
| `test-cases/bad-debug-capital-false.env.example` | `DEBUG=False` | 1 | 1 | PASS |
| `test-cases/bad-debug-missing.env.example` | no `DEBUG` key | 1 | 1 | PASS |
| `test-cases/bad-db-host-legacy-only.env.example` | only `dbhost` | 1 | 1 | PASS |
| `test-cases/bad-db-host-empty.env.example` | `DB_HOST=` | 1 | 1 | PASS |
| `test-cases/bad-db-host-empty-quotes.env.example` | `DB_HOST=''` (peer review) | 1 | 1 | PASS |
| `test-cases/bad-db-host-quoted-spaces.env.example` | `DB_HOST="  "` | 1 | 1 | PASS |
| `test-cases/bad-password-missing.env.example` | no `DB_PASSWORD` key | 1 | 1 | PASS |
| `test-cases/bad-password-empty.env.example` | `DB_PASSWORD=` | 1 | 1 | PASS |
| `test-cases/bad-password-empty-quotes.env.example` | `DB_PASSWORD=""` (peer review) | 1 | 1 | PASS |
| `test-cases/bad-malformed-line.env.example` | line without `=` | 2 | 2 | PASS |
| `test-cases/does-not-exist.env` | file not found | 2 | 2 | PASS |

**Result: 25/25** (20 original cases + 5 added after peer review). The password value did not appear in any output.

## Secret handling

- Password errors say only `DB_PASSWORD: missing` or `DB_PASSWORD: empty`. The value is never printed.
- Parse errors report the line number only, not the line's content, because that line could hold a secret.
- Only `*.example` files with dummy values are committed. No real `.env` file is in the repository.

## Peer review

- **Reviewer:** itz-sajjad
- **Date:** 2026-11-19 (comment on PR #1)
- **Negative tests reproduced:** `test-cases/bad-port.env.example` and `messy.env`, both exit code `1`.
  `run_tests.py` gave 20/20, and `DB_PASSWORD` was never printed.
- **Comment (summary):**
  1. `DB_PASSWORD=""` or `DB_HOST=""` (empty quotes) is accepted with exit code 0. `.strip()`
     removes only whitespace, so the value stays as the two-character string `""`.
  2. Add a `bad-port-missing.env.example` test for a missing `APP_PORT` key, to match the
     missing-key tests for `DEBUG` and `DB_PASSWORD`.
- **Confirmed before fixing:** the original validator printed `Configuration accepted` (exit 0)
  for `DB_PASSWORD=""`.
- **My response (follow-up commit):**
  - `load()` now removes one pair of matching surrounding quotes (`"x"` or `'x'` becomes `x`).
    Empty quoted values are therefore rejected, and correctly quoted values such as
    `APP_PORT="8080"` are accepted.
  - Added tests: `bad-password-empty-quotes`, `bad-db-host-empty-quotes`,
    `bad-db-host-quoted-spaces`, `bad-port-missing` (all exit 1) and `good-quoted-values` (exit 0).
  - After the fix, `DB_PASSWORD=""` gives `DB_PASSWORD: empty` with exit code 1. Result: 25/25.
