# Progress: backend from scratch (YeStack learning tasks)

## Tasks
- [x] 1. HTTP web server on raw sockets (`webserver/`)
- [x] 2. Key-value database: log, replay, fsync, compaction (`database/`)
- [x] 3. REST API on the database: GET / PUT / PATCH / DELETE
- [x] 4. Event tracking API
- [x] 5. Activity sessions
- [x] 6. Stage 1: reusable CRUD system (`crud/`)
  - [x] SQLite by hand (`try_sqlite.py`): 4 statements, `?`, injection demo
  - [x] Classes and inheritance (`try_classes.py`)
  - [x] `database.py`: connection, row_factory, foreign keys, tables
  - [x] `CrudBase`: allow-list, find, find_page, insert, update, delete
  - [x] `insert` accepts a list
  - [x] Repositories: UserRepository, EventRepository
  - [x] Services: UserService, EventService
  - [x] `main.py` demo
  - [x] Answer the 5 "check your understanding" questions (all right; Q1/Q5 skipped the "what if not" / "what doesn't change" half)

## Quiz log
✅ right · 🟡 half · ❌ wrong

| Date | Topic | Question | Result | Notes |
|---|---|---|---|---|
| 2026-11-18 | sql | why `?` stops injection but can't be a table name | ✅ | parse first, then bind; names are needed to build the plan |
| 2026-11-18 | sql | `lastrowid` / when `rowcount` is 0 | ✅ | |
| 2026-11-18 | sql | insert an event for user 999 without `PRAGMA foreign_keys` | ❌ | said it fails; SQLite silently ignores the FK and inserts an orphan |
| 2026-11-20 | crud | update/delete with an empty where; updates before `commit()` | 🟡 | everything gets changed ✅; knew but forgot to answer that uncommitted changes roll back on exit |
| 2026-11-20 | crud | why SET values come before WHERE values in params | ✅ | `?`s fill left to right |
| 2026-11-20 | crud | `find_page(3, 10)`: LIMIT, OFFSET, rows, why ORDER BY | 🟡 | LIMIT 10 OFFSET 20 ✅; skipped rows 21–30 and why ORDER BY (no order → pages overlap) |

**Quiz scores:** 11-18 2/3 · 11-20 2/3 (both halves count)

**Pattern:** remembers *what* the code does, sometimes skips the "what happens if not" part. Answer every part of the question.
