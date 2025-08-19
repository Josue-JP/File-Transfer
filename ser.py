import socket
import os
import sys

HOST = ''
PORT = 12345

times_to_repeat = 0

def check(text):
    user_input = input(text)
    if user_input.lower() == "q":
        print("Quitting")
        sys.exit()
    return user_input

def receive_file(connection):
    global times_to_repeat
    try:
        repeat_buffer = b""
        while b"\n" not in repeat_buffer:
            repeat_buffer += connection.recv(1)
        repeat = int(repeat_buffer.decode().strip())
        times_to_repeat += repeat

        # get the file SIZE
        size_buffer = b""
        while b"\n" not in size_buffer:
            size_buffer += connection.recv(1)
        filesize = int(size_buffer.decode().strip())

        cli_file_name_buffer = b""
        while b"\n" not in cli_file_name_buffer:
            cli_file_name_buffer += connection.recv(1)
        cli_file_name = cli_file_name_buffer.decode().strip()

        file_location = check(f"Enter the path to save {cli_file_name}: ")


        received = 0

        with open(file_location, "wb") as f:
            while received < filesize:
                chunk = connection.recv(min(1024, filesize - received))
                if not chunk: break

                f.write(chunk)
                received += len(chunk)


        print(f"Saved {cli_file_name} as {file_location}")
    except Exception as e:
        print(f"ERROR: {e}")

def sock():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen(1)
        sock.settimeout(3)
        while True:
            try:
                connection, address = sock.accept()
                with connection:
                    receive_file(connection)
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                print("\nProgram ended by user")
                break
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
