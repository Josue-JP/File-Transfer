import socket
import os
import sys
from cryptography.fernet import Fernet # imports Fernet (symmetric encryption)

HOST = ''
PORT = 12345
key_file = "key.ky"

args = sys.argv



def checkname(cli_file_name, directory):
    base, ext = os.path.splitext(cli_file_name)
    filename = cli_file_name
    counter = 1

    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1

    return os.path.join(directory, filename)

def receive_file(connection, directory, sock, fern_obj):
    while True:
        try:
            size_buffer = get_msg(fern_obj, connection)
            filesize = int(size_buffer.decode().strip())

            cli_file_name = get_msg(fern_obj, connection)
            cli_file_name = cli_file_name.decode()
            cli_file_name = os.path.basename(cli_file_name)

            file_location = checkname(cli_file_name, directory)


            received = 0

            with open(file_location, "wb") as f:
                while received < filesize:
                    chunk = connection.recv(min(1024, filesize - received))
                    if not chunk: break

                    f.write(chunk)
                    received += len(chunk)

            with open(file_location, "rb+") as file:
                conts = file.read()
                decrypted_conts = fern_obj.decrypt(conts)
                file.seek(0)
                file.truncate(0)
                file.write(decrypted_conts)

            print(f"Saved {cli_file_name} as {file_location}")
        except KeyboardInterrupt:
            print("\nProgram ended by user")
            break
        except socket.timeout:
            raise socket.timeout
        except ValueError:
            if size_buffer == b"END_CONNECTION":
                print("Client has ended connection!!!")
                break
            else:
                print("Client has not sent a valid number for the filesize")
                break


def get_key(): 
    if "-gk" in args:
        key = Fernet.generate_key()
        with open(key_file, "wb") as file: # To save the key in a file
            file.write(key)
    else:
        with open(key_file, "rb") as file:
            key = file.read()

    return Fernet(key)

def get_msg(fern_obj, connection):
    buffer = b""
    while b"\n" not in buffer:
        buffer += connection.recv(1)
    buffer = buffer.decode().strip('\n')
    try:
        return fern_obj.decrypt(buffer)
    except: 
        print(f"!!!The clients key is not compatible with the servers key!!!")
        exit()


def main():
    try:
        fern_obj = get_key()
    except ValueError:
        print(f"The key in {key_file} is not in a safe Fernet compatible format.\nConsider generating a new key.")
        exit()

    try:
        print("Press CTRL+C to exit, or wait for a client's response")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(15)
            sock.bind((HOST, PORT))
            sock.listen(1)

            try:
                connection, address = sock.accept()
                connection.settimeout(15)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            with connection:
                decrypted_txt = get_msg(fern_obj, connection)
                connection.sendall(fern_obj.encrypt(decrypted_txt))

                directory = input("Specify the directory to save each file: ").strip()
                os.makedirs(directory, exist_ok=True)

                receive_file(connection, directory, sock, fern_obj)

    except socket.timeout:
        print("Socket timeout!!!\nMore than 15 seconds have passed by.")
    except KeyboardInterrupt:
        print("\nProgram ended by user")





if __name__ == "__main__":
    main()

