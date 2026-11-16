import json,os

if os.path.exists("data.json"):
    with open("data.json") as f:
        DB=json.load(f)
else:
    DB={}



def save():
    with open("temp.json","w") as f:
        json.dump(DB,f)
        f.flush()
        os.fsync(f.fileno())
    os.replace("temp.json","data.json")
    dirfd = os.open(".", os.O_RDONLY)
    os.fsync(dirfd)
    os.close(dirfd)

counter=0
broken = False
if os.path.exists("data.log"):
    with open("data.log") as f:
        for line in f:
            if not line.endswith("\n"):
                broken = True
                continue
            counter+=1
            line = line.rstrip("\n")
            parts=line.split(" ",2)
            cmd=parts[0]
            KEY=parts[1]
            if cmd !="delete":
                value=parts[2]
            if cmd in ("set","update"):
                DB[KEY]=value
            else:
                DB.pop(KEY,None)
if broken:
    save()
    open("data.log","w").close()
    counter=0
            
def check_key(KEY):
    if not KEY:
        raise ValueError("Key cannot be empty")
    if " " in KEY or "\n" in KEY:
        raise ValueError("Key cant have spaces or newline")

def check_value(value):
    if not value:
        raise ValueError("Value required")
    if "\n" in value:
        raise ValueError("value cant have newline")

def log(query):
    global counter
    with open("data.log","a") as f:
        f.write(query+"\n")
        f.flush()
        os.fsync(f.fileno())
    counter+=1
    if counter >=10:
        save()
        open("data.log","w").close()
        counter=0
def db_set(KEY,value):
        check_key(KEY)
        check_value(value)
        global DB
        DB[KEY]=value
        log(f"set {KEY} {value}")
def db_get(KEY):
    check_key(KEY)
    if KEY not in DB:
        return None
    return DB[KEY]
def db_update(KEY,value):
    check_key(KEY)
    check_value(value)
    if KEY not in DB:
        return False
    else:
        DB[KEY]=value
        log(f"update {KEY} {value}")
        return True

def db_delete(KEY):
    check_key(KEY)
    if KEY not in DB:
        return False
    else:
        DB.pop(KEY,None)
        log(f"delete {KEY}")
        return True

if __name__ == "__main__":
    while True :
        query = input("> ")
        try:
            parts = query.split(" ",2)
            cmd  = parts[0]
            if len(parts)>1:
                KEY= parts[1]
            if len(parts)>2:
                value = parts[2]
            if cmd == "set":
                if len(parts)>=3:
                    db_set(KEY,value) 
                    print("DONE")
                else:
                    print("Missing Attributes")
            elif cmd == "get":
                if len(parts)==2:
                    result=db_get(KEY)
                    if result == None:
                        print("KEY not found T-T")
                    else:
                        print(result)
                else:
                    print("PLs provide KEY")
            elif cmd == "update":
                if len(parts)>=3:
                    if not db_update(KEY,value):
                        print("KEY not found T-T")
                    else:
                        print("DONE!")
                else:
                    print("Missing Attributes")
                    
            elif cmd == "delete":
                if len(parts)>1:
                    if not db_delete(KEY):
                        print("KEY is NOT IN DB")
                    else:
                        print("DONE!")
                else:
                    print("Missing Attributes")
            elif cmd == "exit":
                save()
                open("data.log","w").close()
                break
            else:
                print("unknown command")        
        except ValueError as e:
            print(e)
