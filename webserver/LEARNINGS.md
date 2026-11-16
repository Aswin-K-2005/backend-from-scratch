# Web Server from Scratch: What I Learned

**Task:** build an HTTP web server in Python with no framework, and understand how TCP connections and acknowledgements work.
**Code:** `webserver.py` (raw `socket` module only, with no `http.server`, `socketserver` or Flask)

---

## 1. What the server does now

- Listens on `127.0.0.1:8080`
- Reads a full HTTP request (it buffers until `\r\n\r\n`)
- Parses the request line into method, path and version
- Responds with proper HTTP status codes:

| Request | Response |
|---|---|
| `GET /` or `GET /hello` | `200 OK` |
| `GET /anything-else` | `404 Not Found` |
| `POST`, `PUT`, ... | `405 Method Not Allowed` |
| Malformed or garbage request | `400 Bad Request` |

- Survives bad input (empty requests, garbage, invalid UTF-8) without crashing
- Restarts instantly thanks to `SO_REUSEADDR`

## 2. How it was built (milestones)

1. **TCP echo server**: the socket lifecycle, from create to close
2. **Watched TCP with `tcpdump`**: handshake, seq/ack numbers, RST
3. **Parsed a real HTTP request** sent by curl
4. **Sent real HTTP responses**: status line, headers, body, status codes

---

## 3. Sockets

The Python `socket` module is a thin wrapper over the C BSD socket API (the same one used for Unix sockets in C).

| Step | Python call | Notes |
|---|---|---|
| Create | `socket.socket(socket.AF_INET, socket.SOCK_STREAM)` | `AF_INET` = IPv4, `SOCK_STREAM` = TCP |
| Option | `setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` | Must come **before** `bind` |
| Bind | `bind(("127.0.0.1", 8080))` | |
| Listen | `listen(5)` | 5 = how many finished connections can wait in the queue |
| Accept | `conn, addr = serversocket.accept()` | Returns a **new** socket for that one client |
| Receive | `data = conn.recv(1024)` | Up to 1024 bytes; `b''` means the client closed |
| Send | `conn.sendall(data)` | Loops internally until every byte is sent |
| Close | `conn.close()` | |

**Lessons from mistakes along the way:**
- **Ports below 1024 need root.** Binding to port 80 gave `PermissionError`.
- **`socket.gethostname()` binds to the LAN IP**, not localhost. Use `127.0.0.1` so that only your own machine can connect.
- **Two loops are needed:** an outer loop with one pass per *client* (`accept`) and an inner loop with one pass per *message* (`recv`). A `break` only exits the innermost loop.
- **One `recv` is not one message.** TCP is a byte stream, so data must be buffered until a delimiter (here `\r\n\r\n`) shows up.

## 4. TCP: what the kernel does for you

**The kernel handles all of TCP, not the program.** The handshake, ACKs, retransmissions, FIN and RST all happen in the kernel. The program only sees a stream of bytes through `recv` and `sendall`.

Evidence from my own captures:
- The kernel sent an **RST** for an IPv6 connection attempt that my program never saw.
- The **ACK** for incoming data was sent *before* my Python code even ran. The echo came about 0.1 ms later as a separate packet.
- The handshake finishes before `accept()` is called. `accept()` only takes an already-finished connection from the queue.

### The 3-way handshake
```
client → server   [S]    SYN       "I want to connect"
server → client   [S.]   SYN-ACK   "OK, me too"
client → server   [.]    ACK       "Connected"
```

### Sequence and ACK numbers
- TCP gives **every byte** a number.
- `seq A:B` means bytes A to B−1. The end is exclusive, like Python's `range`.
- **ack = the next byte expected = start seq + length.**
  Example: client sends `seq 2050199446:2050199449` (3 bytes, `hi\n`), and the server replies `ack 2050199449`.
- **SYN and FIN each count as 1** sequence number even though they carry no data.
- If no ACK arrives, the sender's kernel **resends** the data. This is what makes TCP reliable.

### tcpdump flags

| Flag | Meaning |
|---|---|
| `[S]` | SYN |
| `[S.]` | SYN-ACK |
| `[.]` | ACK |
| `[P.]` | Data (PSH-ACK) |
| `[F.]` | FIN, closing |
| `[R]` / `[R.]` | RST: "no such connection" |

Command: `sudo tcpdump -i lo -nn -S port 8080`

### Closing, TIME-WAIT and `SO_REUSEADDR`
- **The side that closes first** enters **TIME-WAIT** for about 60 s on Linux. This protects against a lost final ACK and against stray delayed packets landing in a new connection.
- In the echo server the client closed first, so TIME-WAIT was on the client's port. In the HTTP server, the **server** closes first after each response, so TIME-WAIT is on **port 8080**.
- Without `SO_REUSEADDR`, restarting the server during TIME-WAIT fails with `Address already in use`.
- `SO_REUSEADDR` allows the bind despite TIME-WAIT. It does **not** allow two servers listening on the same port.

### Connection errors
- **RST**: sent when a packet arrives for a connection that doesn't exist, for example after the server process died.
- **Broken pipe (`EPIPE`)**: writing to a connection the other side has already reset.
- In Python these appear as `BrokenPipeError` and `ConnectionResetError`, both subclasses of `ConnectionError`.
- A restarted server is a new process, so old client connections never carry over and clients must reconnect.

Useful command: `ss -tan | grep 8080` shows LISTEN, ESTAB, CLOSE-WAIT and TIME-WAIT.

## 5. Bytes vs strings

- Sockets carry **bytes**, never text. In Python that means `b'...'` values of type `bytes`.
- `bytes → str`: `data.decode("utf-8")`, and `str → bytes`: `text.encode("utf-8")`
- You can't send a `str`: `sendall("hi")` raises `TypeError`.
- **`Content-Length` counts bytes, not characters** (`"é"` is 1 character but 2 bytes), so measure `len()` **after** encoding.

## 6. HTTP

HTTP is **just text sent over TCP**. That's why `nc` (netcat, a raw TCP tool) can speak HTTP if you type the request yourself.

### Request
```
GET /hello HTTP/1.1\r\n          ← method, path, version
Host: localhost:8080\r\n         ← headers: "Name: value"
User-Agent: curl/8.18.0\r\n
Accept: */*\r\n
\r\n                             ← empty line = end of headers
```

### Response
```
HTTP/1.1 200 OK\r\n              ← version, status code, reason phrase
Content-Type: text/plain\r\n
Content-Length: 20\r\n
\r\n
You asked for /hello             ← body
```

### Rules learned the hard way
- **Line endings are `\r\n` (CRLF)**, not `\n`. CR (`\r`, ASCII 13) returns to the start of the line and LF (`\n`, ASCII 10) moves down a line. Internet protocols standardised on CRLF back in the teletype era.
- **Every header must be `Name: value`.** A header without a colon makes curl reject the response with "Header without colon".
- **No space before the colon.** `Content-Length : 20` is silently ignored, so curl doesn't know the body size.
- **The status line must start with `HTTP/1.1`.** Echoing the request back made curl say "Received HTTP/0.9".
- **`Content-Length` is how the client knows where the body ends.** Without it, the client can only wait for the connection to close.
- `localhost` resolves to IPv6 `::1` first. If the server only binds IPv4, clients try `::1`, get an RST, and then fall back to `127.0.0.1`.

### Status codes used

| Code | Meaning |
|---|---|
| 200 OK | Success |
| 400 Bad Request | Malformed request |
| 404 Not Found | Path doesn't exist |
| 405 Method Not Allowed | Method not supported |

## 7. Never trust the client

Anyone can connect and send anything. **One bad client must never crash the server for everyone.**

- An empty request (`b''`) → `"".split(" ")` returns `[""]` → `ValueError` when unpacking into 3 variables. Fix: catch it and reply 400.
- Invalid UTF-8 → `UnicodeDecodeError`, which is a subclass of `ValueError`, so one `except ValueError` covers both.
- A `try` only protects the lines **inside** it.
- An exception raised **inside** an `except` block is not caught by the other `except` blocks next to it.

---

## 8. Known limitations (not finished)

| Issue | Effect | Fix |
|---|---|---|
| Handles one client at a time | A client that connects and never sends anything blocks everyone else | Timeouts and threads/`selectors` |
| No buffer size limit | Endless data without `\r\n\r\n` grows memory without bound | Cap the buffer size |
| Plain-text routes only | Doesn't serve files | Static files, with path-traversal protection |
| No keep-alive | One request per connection | Keep connections open |

Fixed later: `try:` now starts right after `accept()` (a client RST no longer crashes the server), empty requests are closed without a reply, and request bodies are read using `Content-Length`.

## 9. Tools used

| Tool | Use |
|---|---|
| `nc localhost 8080` | Raw TCP client: type bytes, see bytes |
| `curl -v` / `curl -i` | HTTP client that shows headers |
| `curl -X POST` | Send a different method |
| `tcpdump -i lo -nn -S port 8080` | Watch the packets |
| `ss -tan` | See connection states |
| `print(repr(data))` | Show hidden `\r` and `\n` characters |

## 10. Resources
- Python Socket Programming HOWTO: https://docs.python.org/3/howto/sockets.html
- RFC 9112: HTTP/1.1 message syntax
- RFC 9293: TCP, section 3.5 (opening and closing connections)
- Kurose & Ross, *Computer Networking: A Top-Down Approach*, chapters 2–3
- MDN: "An overview of HTTP"
