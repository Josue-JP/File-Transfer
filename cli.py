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

def get_directory():
    path = check("Enter the directory/path you want to send: ")
    files = []
    message_sent = False
    for i in os.listdir(path):
        full_path = os.path.join(path, i)
        if os.path.isdir(full_path):
            if message_sent == False:
                print(f"Directory traversal is not supported.")
                message_sent = True
        else:
            files.append(full_path)

    return files

def send_info(s, file_location):
    if os.path.isfile(file_location):
        with open(file_location, "rb") as f:
            file_contents = f.read()

        filesize = len(file_contents)
        filename = os.path.basename(file_location) # gets the name of the file without the full path

        s.sendall(f"{filesize}\n".encode())
        s.sendall(f"{filename}\n".encode())
        s.sendall(file_contents)
        return 0

    else:
        print("INVALID FILE_LOCATION")
        return 1


def send_file(s, file_location = None):
    try:
        if file_location == None:
            failed_attempts = 0
            while True:
                file_location = check("Specify the file to send: ")
                return_value = send_info(s, file_location)

                if return_value == 1:
                    failed_attempts += 1
                elif return_value == 0:
                    failed_attempts = 0
                    
                if failed_attempts == 3:
                    print("Three attepts tried.")
                    return

        elif type(file_location) == list:
            for i in file_location:
                send_info(s, i)

    except KeyboardInterrupt:
        print("Program ended by user")
        s.sendall("END_CONNECTION\n".encode())
    except BrokenPipeError:
        print("Server has closed the connection!!!")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15)
            s.connect((SERVER_IP, PORT))
            message = f"Connected to {SERVER_IP}:{PORT}\t".encode()
            s.sendall(message)
            data = s.recv(1024)
            print(data.decode())

            if len(args) == 1:
                send_file(s)
            elif args[1] == "-d":
                files = get_directory()
                send_file(s, files)
            else:
                raise ValueError("INVALID ARGUMENT")
            

    except (BrokenPipeError, ConnectionResetError):
        print("Server has closed the connection!!!")

    except socket.timeout:
        print("Socket timeout!!!")

    except ConnectionRefusedError:
        print("Refused Connection!!!\nCheck if ser.py is running on the server machine.")


if __name__ == "__main__":
    main()
