from time import sleep
import socket, json 
import re


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
    print(f'This is the console for the Ground Station.')
    print(f'Making initial connection...\n')
    print(f'Enter commands in the form [action cmd]:[value]\n')

    exitB = False

    while exitB == False:

        msg = input()

        res = re.split(r'[:]',msg)

        if len(res) < 2:
            print(f'Enter commands in the form [action cmd]:[value]\n')
            continue

        action = res[0]
        value = res[1]

        print(f'You entered:\naction={action}\nvalue={value}')

        send_2sc(action = action, value = value)

        if action == 'exit':
            exitB = True

