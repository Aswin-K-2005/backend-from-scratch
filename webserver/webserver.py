import socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(("127.0.0.1", 8080))
serversocket.listen(5)
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
        print(f"Method:{method}\n Path:{path} \n Version:{version}")
        
        if method != "GET":
            status = "405 Method Not Allowed"
            body = b"This method is not available T-T"
        elif path == "/" or path == "/hello":
            status = "200 OK"
        else:
            status = "404 Not Found"
            body="Wrong page :)".encode()
        headers=f"HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n".encode()
        clientsocket.sendall(headers+body)

    except ConnectionError:
            pass
    except  ValueError:
            status = "400 Bad Request"
            body = b"Request not Allowed"
            headers=f"HTTP/1.1 {status}\r\nContent-Type: text/plain\r\nContent-Length: {len(body)}\r\n\r\n".encode()
            clientsocket.sendall(headers+body)

    clientsocket.close()
