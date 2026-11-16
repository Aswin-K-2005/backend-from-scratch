# Backend from Scratch

Learning projects that build backend basics by hand, in plain Python with no frameworks, so I understand what tools like Flask, Redis or FastAPI do for me before I use them.

| # | Project | Folder | What I learned |
|---|---|---|---|
| 1 | HTTP web server on raw sockets | [`webserver/`](webserver/) | the socket lifecycle, TCP (handshake, seq/ack, RST, TIME-WAIT), HTTP/1.1 format, status codes, never trusting the client |
| 2 | Key-value database | [`database/`](database/) | an append-only log, replay on startup, fsync, atomic snapshots (compaction), handling a torn last line |
| 3 | REST API on the database | [`database/`](database/) | GET / PUT / PATCH / DELETE, reading `Content-Length` bodies, validation, 400 vs 404 vs 405 |
| 4 | Event tracking | [`database/`](database/) | events stored as `event:<user>:<time_ns>` keys, prefix scans, filtering by type and time range |
| 5 | Activity sessions | [`database/`](database/) | uuid session IDs, grouping events into sessions, ownership through the key layout |

Only the Python standard library is used (`socket`, `json`, `os`, `uuid`, `urllib.parse`).

## Running

```bash
# project 1
cd webserver && python3 webserver.py          # http://127.0.0.1:8080

# projects 2-5
cd database && python3 db.py                  # interactive REPL: set / get / update / delete / exit
cd database && python3 server.py              # HTTP API on http://127.0.0.1:8080
```

Each folder has its own README / LEARNINGS file with details.
