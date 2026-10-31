import socket, json 


print(f'This is the console for the Ground Station\n')


host = "127.0.0.1"
port = 8080

client  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

action = 'get_status'
value = None

payload = {
    "action": "set_target",
    "value": [1.0, 0.0, 0.0]
}

payload = {
    "action": "exit"
    #"value": [1.0, 0.0, 0.0]
}


client.sendall(json.dumps(payload).encode())
response = client.recv(4096).decode()
client.close()
#output = json.loads(response)

print(f'output = {response}\n')

