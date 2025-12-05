import socket
import os
import sys
from cryptography.fernet import Fernet # imports Fernet (symmetric encryption)

SERVER_IP = '127.0.0.1'    # The remote host
PORT = 12345              # The same port as used by the server
key_file = "key.ky"

args = sys.argv



def check(text, s, fern_obj):
    user_input = input(text)
    if user_input.lower() == "q":
        print("Quitting")
        s.sendall(encrypt_text("END_CONNECTION", fern_obj) + b'\n')
        exit()
    return user_input

def get_directory(s, fern_obj):
    path = check("Enter the directory/path you want to send: ", s, fern_obj)
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

def encrypt_text(txt, fern_obj):
    return fern_obj.encrypt(str(txt).encode())

def send_info(s, file_location, fern_obj):
    if os.path.isfile(file_location):
        with open(file_location, "rb") as f:
            file_contents = f.read()

        f_conts_encrypted = fern_obj.encrypt(file_contents)

        filesize = len(f_conts_encrypted)
        filename = os.path.basename(file_location) # gets the name of the file without the full path
        s.sendall(encrypt_text(filesize, fern_obj) + b'\n')
        s.sendall(encrypt_text(filename, fern_obj) + b'\n')
        s.sendall(f_conts_encrypted)
        return 0  

    else:
        print("INVALID FILE_LOCATION")
        return 1


def send_file(s, fern_obj, file_location = None):
    try:
        if file_location == None:
            failed_attempts = 0
            while True:
                file_location = check("Specify the file to send: ", s, fern_obj)
                return_value = send_info(s, file_location, fern_obj)

                if return_value == 1:
                    failed_attempts += 1
                elif return_value == 0:
                    failed_attempts = 0
                    
                if failed_attempts == 3:
                    print("Three attepts tried.")
                    s.sendall(encrypt_text("END_CONNECTION", fern_obj) + b'\n')
                    return

        elif type(file_location) == list:
            for i in file_location:
                send_info(s, i, fern_obj)

    except KeyboardInterrupt:
        print("Program ended by user")
        s.sendall(encrypt_text("END_CONNECTION", fern_obj) + b'\n')
    except BrokenPipeError:
        print("Server has closed the connection!!!")
        print(f"{file_location} was not saved!!!")
    except Exception as e:
        print(f"ERROR: {e}")


def main():
    try:
        with open(key_file, "rb") as file:
            key = file.read()
            fern_obj = Fernet(key)
    except ValueError:
        print(f"!!!The key in {key_file} is not in a safe Fernet compatible format.\nConsider retrieving the correct key!!!")
        exit()


    try:
        print("Attempting a connection to the server...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15)
            s.connect((SERVER_IP, PORT))
            encrypted_txt = fern_obj.encrypt(f"Connected to {SERVER_IP}:{PORT}".encode())
            s.sendall(encrypted_txt + b'\n')
            data = s.recv(1024)
            try:
                decrypted_txt = fern_obj.decrypt(data)
                print(decrypted_txt.decode())
            except:
                print(f"!!!The key inside {key_file} does not match the servers key!!!")
                exit()

            if len(args) == 1:
                send_file(s, fern_obj)
            elif args[1] == "-d":
                files = get_directory(s, fern_obj)
                send_file(s, fern_obj, files)
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
