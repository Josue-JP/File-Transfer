# s = client_socket
import socket
import os
import sys

SERVER_IP = '127.0.0.1'    # The remote host
PORT = 12345              # The same port as used by the server

args = sys.argv


def check(text):
    user_input = input(text)
    if user_input.lower() == "q":
        print("Quitting")
        sys.exit()
    return user_input



def send_file(s, file_location):
    try:
        if os.path.isfile(file_location):
            with open(file_location, "rb") as f:
                file_contents = f.read()

            filesize = len(file_contents)
            filename = os.path.basename(file_location) # gets the name of the file without the full path

            s.sendall(f"{filesize}\n".encode())
            s.sendall(f"{filename}\n".encode())
            s.sendall(file_contents)
        else:
            print("Please Enter A Valid File Path")

    except KeyboardInterrupt:
        print("Program ended by user")
    except BrokenPipeError:
        print("Server has closed the connection!!!")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    path = input("Enter the directory/path you want to send: ")
    files = []
    for i in os.listdir(path):
        full_path = os.path.join(path, i)
        if os.path.isdir(full_path):
            print(f"The following directory was not sent: {full_path}")
        else:
            files.append(full_path)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15)
            s.connect((SERVER_IP, PORT))
            message = f"Connected to {SERVER_IP}:{PORT}\t".encode()
            s.sendall(message)
            data = s.recv(1024)
            print(data.decode())
            for i in files:
                send_file(s, i)

    except (BrokenPipeError, ConnectionResetError):
        print("Server has closed the connection!!!")

    except socket.timeout:
        print("Socket timeout!!!")

    except ConnectionRefusedError:
        print("Refused Connection!!!\nCheck if ser.py is running on the server machine.")


if __name__ == "__main__":
    main()

