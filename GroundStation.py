from time import sleep
import socket, json 

host = "127.0.0.1"
port = 8080

def send_2sc(action = "set_target", value = None):
    client  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    payload = {
    "action": action, #"set_target",
    "value": value #[1.0, 0.0, 0.0]
    }

    client.sendall(json.dumps(payload).encode())
    response = client.recv(1024).decode()
    print(f"Server response: {response}")
    client.close()

if __name__ == "__main__":
    print(f'This is the console for the Ground Station\n')
    
    
    send_2sc(action = "set_target",value = [1.0, 0.0, 0.0])

    #sleep(5)

    send_2sc(action = "exit",value = None) 
