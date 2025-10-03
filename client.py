import socket

def client_program():
    host = '127.0.0.1'  # The server's IP address
    port = 5000  # The server's port

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))  # Connect to server

    message = input("Enter message to send (type 'quit' to exit): ")

    while message.lower() != 'quit':
        client_socket.send(message.encode())  # Send message to server
        data = client_socket.recv(1024).decode()  # Receive echoed message
        print("Received from server:", data)
        message = input("Enter message to send (type 'quit' to exit): ")

    client_socket.close()

if __name__ == '__main__':
    client_program()
