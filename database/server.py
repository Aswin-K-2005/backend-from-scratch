import socket
import db
import json,time
import uuid
from urllib.parse import parse_qs
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(("127.0.0.1", 8080))
serversocket.listen(5)

def need_str(d, name):
    value = d.get(name)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value
        
def db_scan(prefix):
    result=[]
    for k,v in db.DB.items():
        if k.startswith(prefix):
            result.append(v)
    return result



while True:
    (clientsocket, address) = serversocket.accept()
    try:
        buffer = b""
        while True:

            data = clientsocket.recv(1024)
            buffer+=data
            if not data:
                break
            if b"\r\n\r\n" in buffer:
                break
        if not buffer:
            clientsocket.close()
            continue
        head,_,body = buffer.partition(b"\r\n\r\n")
        length = 0                                      
        for line in head.split(b"\r\n")[1:]:           
            name, _, val = line.partition(b":")         
            if name.strip().lower() == b"content-length":
                length = int(val.strip())              

        while len(body) < length:                      
            data = clientsocket.recv(1024)
            if not data:                                
                break
            body += data

        print("BODY:", body)   
        lines = buffer.split(b"\r\n")
        line = lines[0].decode()
        method,path,version = line.split(" ")
        path,_,query = path.partition("?")
        print(f"Method:{method}\n Path:{path} \n Version:{version}")
        if path == "/events" and method == "POST":
            event = json.loads(body.decode())
            if not isinstance(event,dict):
                raise ValueError("BODY must be json object")
            user_id = need_str(event,"user_id")
            if ":" in user_id:
                raise ValueError("Userid must not contain :")
            eventype=need_str(event,"type")
            details = event.get("details",{})
            if not isinstance(details,dict):
                raise ValueError("detail should be an object")
            session_id = event.get("session_id")
            if session_id is not None:
                if not isinstance(session_id,str):
                    raise ValueError("session_id shud be string")
                session = db.db_get(f"session:{user_id}:{session_id}")
                if not session:
                    raise ValueError("no session exists")
            clean = {"user_id":user_id,"type":eventype,"details":details,"session_id":session_id,"timestamp":time.time()}
            db.db_set(f"event:{user_id}:{time.time_ns()}",json.dumps(clean))
            status="201 Created"
            resp =json.dumps(clean).encode()
        elif path.startswith("/users/") and method == "GET":
            parts = path.split("/")
            user_id = parts[2]
            if len(parts)==4 and parts[3]=="events":
                raw = db_scan(f"event:{user_id}:")
                events = [json.loads(r) for r in raw]
                events.sort(key=lambda e: e["timestamp"])
                params = parse_qs(query)
                etype = params.get("type",[None])[0]
                start = params.get("from",[None])[0]
                end = params.get("to",[None])[0]

                if etype is not None:
                    events = [e for e in events if e["type"]==etype]
                if start is not None:
                    events = [e for e in events if e["timestamp"]>=float(start)]
                if end is not None:
                    events = [e for e in events if e["timestamp"] <= float(end)]
                status = "200 OK"
                resp = json.dumps(events).encode()
            elif len(parts)==4 and parts[3]== "sessions":
                raw = db_scan(f"session:{user_id}:")
                sessions = [json.loads(r) for r in raw]
                sessions.sort(key=lambda e: e["timestamp"])

                status = "200 OK"
                resp = json.dumps(sessions).encode()
            elif len(parts)==6 and parts[3]=="sessions" and parts[5]=="events":
                sid=parts[4]
                session = db.db_get(f"session:{user_id}:{sid}")
                if session is None:
                    status ="404 not found"
                    resp  = b"session not found"
                else:
                    raw = db_scan(f"event:{user_id}:")
                    events = [json.loads(r) for r in raw]
                    events.sort(key=lambda e: e["timestamp"])
                    events=[e for e in events if e.get("session_id")==sid]
                    status = "200 OK"
                    resp = json.dumps(events).encode()



            else:   
                raise ValueError("not a valid endpoint")
        elif path.startswith("/users/") and method == "POST":
            parts = path.split("/")
            if len(parts)!=4 or parts[3]!="sessions":
                raise ValueError("Missing Attributes")
            user_id = parts[2]
            if ":" in user_id or not user_id:
                raise ValueError("Invalid user_id")
            sid=uuid.uuid4().hex
            session={"session_id":sid,"user_id":user_id,"timestamp":time.time()}
            db.db_set(f"session:{user_id}:{sid}",json.dumps(session))
            status = "201 Created"
            resp = json.dumps(session).encode()
    




        else: 
            key = path[1:] 
            if method == "GET":
                result =db.db_get(key)
                if result is None:
                    status = "404 not Found" 
                    resp=b"key not Found"
                else:
                    status= "200 OK"
                    resp=result.encode()
            elif method == "PUT":
                status = "200 OK"
                db.db_set(key,body.decode())
                resp = b"OK"
            elif method == "PATCH":
                result = db.db_update(key,body.decode())
                if result:
                    status = "200 Ok"
                    resp = b"OK"
                else:
                    status ="404 not Found"
                    resp = b"parameter issue"
            elif method == "DELETE":
                result = db.db_delete(key)
                if result:
                    status = "200 Ok"
                    resp=b"OK"
                else:
                    status = "404 Not Found"
                    resp=b"Key not Found"

            else:
                status = "405 Method not allowed"
                resp=b"Not allowed method"
        headers=f"HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {len(resp)}\r\n\r\n".encode()
        clientsocket.sendall(headers+resp)

    except ConnectionError:
            pass
    except  ValueError:
            status = "400 Bad Request"
            resp = str(e).encode()
            headers=f"HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {len(resp)}\r\n\r\n".encode()
            clientsocket.sendall(headers+resp)

    clientsocket.close()
