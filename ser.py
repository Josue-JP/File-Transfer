import socket
import os
import sys

HOST = ''
PORT = 12345

def checkname(cli_file_name, directory):
    base, ext = os.path.splitext(cli_file_name)
    filename = cli_file_name
    counter = 1

    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1

    return os.path.join(directory, filename)

def receive_file(connection, directory):
    while True:
        try:
            # get the file SIZE



            size_buffer = b""
            while b"\n" not in size_buffer:
                size_buffer += connection.recv(1)
            filesize = int(size_buffer.decode().strip())

            cli_file_name_buffer = b""
            while b"\n" not in cli_file_name_buffer:
                cli_file_name_buffer += connection.recv(1)
            cli_file_name = cli_file_name_buffer.decode().strip()
            cli_file_name = os.path.basename(cli_file_name)


            file_location = checkname(cli_file_name, directory)


            received = 0

            with open(file_location, "wb") as f:
                while received < filesize:
                    chunk = connection.recv(min(1024, filesize - received))
                    if not chunk: break

                    f.write(chunk)
                    received += len(chunk)


            print(f"Saved {cli_file_name} as {file_location}")
        except KeyboardInterrupt:
            print("\nProgram ended by user")
            break
        except Exception as e:
            print(f"ERROR: {e}")

def sock():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(1)
        sock.settimeout(120)
        try:
            connection, address = sock.accept()
            with connection:
                confirmation_buffer = b""
                while b"\t" not in confirmation_buffer:
                    confirmation_buffer += connection.recv(1)
                connection.sendall(confirmation_buffer)

                directory = input("Specify the directory to save each file: ")
                os.makedirs(directory, exist_ok=True)

                receive_file(connection, directory)

        except socket.timeout:
            print("socket timeout")
        except Exception as e:
            print(f"Server Error: {e}")

def main():
    try:
        print("Press CTRL+C to exit, or wait for a clients response")
        sock()
    except Exception as e:
        print(f"ERROR: {e}")





if __name__ == "__main__":
    main()

