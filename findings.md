# Class 2 — Findings

## Configuration contract (the four rules)

| Key | Rule |
|---|---|
| `APP_PORT` | Whole number between **1024 and 65535**, inclusive (non-privileged port range) |
| `DEBUG` | Must be exactly `false` |
| `DB_HOST` | Must be present and nonempty |
| `DB_PASSWORD` | Must be present and nonempty; its value is **never displayed** |

## Defects in `messy.env`

```ini
dbhost=localhost
DB_HOST=db
APP_PORT=hello
DEBUG=true
DB_PASSWORD=
```

1. **Invalid data type:** `APP_PORT=hello` is text, not a whole number, so it is not a valid port.
2. **Debug policy violation:** `DEBUG=true`. Debug mode must be off for deployment because it can expose
   stack traces, internals, and interactive debuggers.
3. **Empty required setting:** `DB_PASSWORD=` is present but empty.
4. **Duplicate concept / wrong spelling:** `dbhost` and `DB_HOST` both describe the database host.
   The contract requires `DB_HOST`. `dbhost` is a legacy key that the validator ignores; it does
   **not** satisfy the `DB_HOST` requirement.

`DB_HOST=db` is valid, so the validator should report three errors for this file:
`APP_PORT`, `DEBUG`, and `DB_PASSWORD`.
