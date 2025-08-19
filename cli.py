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


def send_file(s):
    file_location = check("Specify the file to send: ")
    if os.path.isfile(file_location):
        with open(file_location, "rb") as f:
            file_contents = f.read()

        filename = os.path.basename(file_location)
        filesize = len(file_contents)
    else:
        print("Please Enter A Valid File Path")

    s.sendall(f"{repeat}\n".encode())
    s.sendall(f"{filesize}\n".encode())
    s.sendall(f"{filename}\n".encode())
    s.sendall(file_contents)



def sock():
    for i in range(repeat):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, PORT))
            print(f"Connected to {SERVER_IP}:{PORT}")
            send_file(s)


def parse_repeat_arg():
    repeat_count = 1
    if len(args) > 2 and args[1] == "-r":
        try:
           repeat_count = int(args[2])
        except ValueError:
           print(f"Error: The -r option requires a number associatied with it\nExample: {args[0]} -r 3")
           sys.exit(1)

    elif len(args) > 1 and args[1] != "-r":
           print(f"Unkown option: {args[1]}")
           sys.exit(1)

    return repeat_count

def main():
    global repeat
    repeat = parse_repeat_arg()
    print(repeat)
    sock()



if __name__ == "__main__":
    main()

