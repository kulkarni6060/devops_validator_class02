"""Run validator.py against every test case and check the exit code.

Usage (from the repository root):
    python run_tests.py        # macOS/Linux: python3 run_tests.py, Windows: py run_tests.py

Each case lists the file and the exit code we expect:
    0 = configuration accepted
    1 = configuration rejected (validation errors)
    2 = file could not be read or parsed
The runner also fails a case if the dummy password appears in the output.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DUMMY_PASSWORD = "example-only-placeholder"

CASES = [
    # (file, expected exit code, what it tests)
    ("valid.env.example", 0, "all four rules satisfied"),
    ("test-cases/good-port-min-1024.env.example", 0, "lowest allowed port"),
    ("test-cases/good-port-max-65535.env.example", 0, "highest allowed port"),
    ("test-cases/good-quoted-values.env.example", 0, "quoted values are unquoted"),
    ("messy.env", 1, "supplied broken file (port, debug, password)"),
    ("test-cases/bad-port.env.example", 1, "port 80 is privileged"),
    ("test-cases/bad-port-1023.env.example", 1, "one below the minimum"),
    ("test-cases/bad-port-65536.env.example", 1, "one above the maximum"),
    ("test-cases/bad-port-text.env.example", 1, "port is not a number"),
    ("test-cases/bad-port-negative.env.example", 1, "negative port"),
    ("test-cases/bad-port-decimal.env.example", 1, "decimal port"),
    ("test-cases/bad-port-empty.env.example", 1, "empty port"),
    ("test-cases/bad-port-missing.env.example", 1, "APP_PORT key missing (peer review)"),
    ("test-cases/bad-debug-true.env.example", 1, "DEBUG=true"),
    ("test-cases/bad-debug-capital-false.env.example", 1, "DEBUG=False is not exactly false"),
    ("test-cases/bad-debug-missing.env.example", 1, "DEBUG key missing"),
    ("test-cases/bad-db-host-legacy-only.env.example", 1, "only legacy dbhost key"),
    ("test-cases/bad-db-host-empty.env.example", 1, "DB_HOST empty"),
    ("test-cases/bad-db-host-empty-quotes.env.example", 1, "DB_HOST='' (peer review)"),
    ("test-cases/bad-db-host-quoted-spaces.env.example", 1, "DB_HOST=\"  \""),
    ("test-cases/bad-password-missing.env.example", 1, "DB_PASSWORD key missing"),
    ("test-cases/bad-password-empty.env.example", 1, "DB_PASSWORD empty"),
    ("test-cases/bad-password-empty-quotes.env.example", 1, "DB_PASSWORD=\"\" (peer review)"),
    ("test-cases/bad-malformed-line.env.example", 2, "line without '='"),
    ("test-cases/does-not-exist.env", 2, "file not found"),
]


def main():
    failures = 0
    for name, expected, purpose in CASES:
        result = subprocess.run(
            [sys.executable, str(ROOT / "validator.py"), name],
            cwd=ROOT, capture_output=True, text=True,
        )
        output = (result.stdout + result.stderr).strip()
        leaked = DUMMY_PASSWORD in output
        ok = result.returncode == expected and not leaked
        failures += not ok
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] exit={result.returncode} (expected {expected})  {name}  -- {purpose}")
        for line in output.splitlines():
            print(f"         {line}")
        if leaked:
            print("         !! password value appeared in output")

    total = len(CASES)
    print(f"\n{total - failures}/{total} cases behaved as expected")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
