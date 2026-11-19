"""Student scaffold. Implement rules from Lab 2; never print secret values."""
import re
import sys

# Non-privileged (registered + dynamic) TCP port range. Ports below 1024
# need root/admin rights, and 65535 is the highest valid TCP port.
PORT_MIN = 1024
PORT_MAX = 65535

# Plain ASCII digits only. int() on its own also accepts "+8080", "8_080",
# and non-ASCII digits, which we do not want in a production config.
_DIGITS = re.compile(r"[0-9]+")


def validate(values):
    """Return a list of error strings. An empty list means the config is valid.

    Error messages name the key and the problem. They never include the
    DB_PASSWORD value.
    """
    errors = []

    # APP_PORT must be a whole number in PORT_MIN..PORT_MAX.
    raw_port = values.get("APP_PORT", "").strip()
    if not raw_port:
        errors.append("APP_PORT: missing or empty (must be a whole number "
                      f"between {PORT_MIN} and {PORT_MAX})")
    else:
        try:
            if not _DIGITS.fullmatch(raw_port):
                raise ValueError("not a plain whole number")
            port = int(raw_port)
        except ValueError:
            errors.append(f"APP_PORT: {raw_port!r} is not a whole number "
                          f"(must be between {PORT_MIN} and {PORT_MAX})")
        else:
            if not PORT_MIN <= port <= PORT_MAX:
                errors.append(f"APP_PORT: {port} is out of range "
                              f"(must be between {PORT_MIN} and {PORT_MAX})")

    # DEBUG must be exactly "false". If it is missing, the app may fall
    # back to an unsafe default, so a missing DEBUG is also an error.
    if "DEBUG" not in values:
        errors.append("DEBUG: missing (must be exactly 'false')")
    elif values["DEBUG"] != "false":
        errors.append(f"DEBUG: {values['DEBUG']!r} is not allowed "
                      "(must be exactly 'false' for deployment)")

    # DB_HOST must be present and nonempty. The legacy 'dbhost' key does
    # not count.
    if not values.get("DB_HOST", "").strip():
        hint = " (legacy key 'dbhost' is not accepted)" if "dbhost" in values else ""
        errors.append(f"DB_HOST: missing or empty{hint}")

    # DB_PASSWORD must be present and nonempty. Never print its value.
    if "DB_PASSWORD" not in values:
        errors.append("DB_PASSWORD: missing")
    elif not values["DB_PASSWORD"].strip():
        errors.append("DB_PASSWORD: empty")

    return errors


def load(path):
    values = {}
    with open(path, encoding="utf8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if line and not line.startswith("#"):
                if "=" not in line:
                    # Do not echo the line: it could contain a secret.
                    raise ValueError(f"line {number} is not in KEY=value format")
                key, value = line.split("=", 1)
                values[key.strip()] = value.strip()
    return values


if __name__ == "__main__":
    # Exit codes: 0 = accepted, 1 = invalid configuration, 2 = could not read file.
    if len(sys.argv) != 2:
        print("Usage: python validator.py <path-to-env-file>", file=sys.stderr)
        sys.exit(2)

    try:
        issues = validate(load(sys.argv[1]))
    except FileNotFoundError:
        print(f"ERROR: file not found: {sys.argv[1]}", file=sys.stderr)
        sys.exit(2)
    except UnicodeDecodeError:
        print(f"ERROR: {sys.argv[1]} is not valid UTF-8 text", file=sys.stderr)
        sys.exit(2)
    except ValueError as exc:
        print(f"ERROR: could not parse {sys.argv[1]}: {exc}", file=sys.stderr)
        sys.exit(2)
    except OSError as exc:
        print(f"ERROR: could not read {sys.argv[1]}: {exc.strerror}", file=sys.stderr)
        sys.exit(2)

    print("\n".join(issues) if issues else "Configuration accepted")
    sys.exit(bool(issues))
