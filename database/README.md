# Database + HTTP API from Scratch

A key-value database (`db.py`) with an HTTP API in front of it (`server.py`), both written with only the Python standard library. Events and activity sessions are built on top of the same key-value store.

## How the database works (`db.py`)

- **In memory:** a Python dict `DB` holds every key and value.
- **Append-only log:** every write is appended to `data.log` (`set k v`, `update k v`, `delete k`) and `fsync`ed before the call returns.
- **Startup:** load the snapshot `data.json`, then replay `data.log` on top of it.
- **Compaction:** every 10 writes (and on `exit`) the dict is written to `temp.json`, `fsync`ed, atomically renamed to `data.json` (`os.replace` + directory fsync), and the log is cleared.
- **Crash safety:** a last log line without `\n` (a write torn by a crash) is skipped, and the DB compacts at startup.
- **Validation:** keys can't be empty or contain spaces or newlines, and values can't contain newlines (this prevents log injection).

REPL: `python3 db.py`
```
> set name aswin
> get name
> update name kumar
> delete name
> exit
```

## HTTP API (`server.py`, port 8080)

### Key-value
| Request | Result |
|---|---|
| `GET /<key>` | 200 + value, or 404 |
| `PUT /<key>` (body = value) | creates or replaces → 200 |
| `PATCH /<key>` (body = value) | updates an existing key → 200, or 404 |
| `DELETE /<key>` | 200, or 404 |

### Events
| Request | Result |
|---|---|
| `POST /events` `{"user_id", "type", "details"?, "session_id"?}` | 201 + the stored event (the server adds `timestamp`) |
| `GET /users/<id>/events?type=&from=&to=` | the user's events sorted by time, optionally filtered by type and a unix-time range |

### Sessions
| Request | Result |
|---|---|
| `POST /users/<id>/sessions` | 201 + `{"session_id", "user_id", "timestamp"}` |
| `GET /users/<id>/sessions` | the user's sessions |
| `GET /users/<id>/sessions/<sid>/events` | the events in that session, or 404 |

An event's `session_id` must belong to the same user, otherwise the server returns 400.

### Example
```bash
curl -X POST localhost:8080/users/u1/sessions                       # copy the session_id
curl -X POST localhost:8080/events -d '{"user_id":"u1","type":"article_viewed","session_id":"<sid>"}'
curl localhost:8080/users/u1/sessions/<sid>/events
```

## Storage layout

Everything is one key-value store. Key prefixes separate the kinds of data:
```
event:<user_id>:<time_ns>      → event JSON
session:<user_id>:<session_id> → session JSON
<anything else>                → plain key-value data
```
Prefix scans (`event:u1:`) find one user's data, and the trailing `:` keeps `u1` and `u10` apart. Because a session key includes its user, a session ID used with the wrong user simply isn't found.

## Known limitations

- One client at a time (no threads).
- Prefix scans read every key, with no index.
- Only a torn **last** log line is detected. A corrupted line in the middle isn't (real databases add a checksum per record and stop replay at the first bad one).
- No authentication: anyone can send any `user_id`.
- No URL decoding.
