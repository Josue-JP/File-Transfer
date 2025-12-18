import socket
import os
import sys
import ssl
from inputimeout import inputimeout, TimeoutOccurred

HOST = ''
PORT = 12345

args = sys.argv

def checkname(cli_file_name, directory):
    base, ext = os.path.splitext(cli_file_name)
    filename = cli_file_name
    counter = 1

    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base}_{counter}{ext}"
        counter += 1

    return os.path.join(directory, filename)

def receive_file(connection, directory, sock):
    def get_msg(connection):
        buffer = b""
        while b"\n" not in buffer:
            buffer += connection.recv(1)
        return buffer.decode().strip()

    while True:
        try:
            size_buffer = get_msg(connection)
            filesize = int(size_buffer)

            cli_file_name = os.path.basename(get_msg(connection))
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
        except socket.timeout:
            raise socket.timeout
        except ValueError:
            if size_buffer == "END_CONNECTION":
                print("Client has ended connection!!!")
                break
            else:
                print("Client has not sent a valid number for the filesize")
                break



def main():
    try:


        print("Press CTRL+C to exit, or wait for a client's response")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(15)
            sock.bind((HOST, PORT))
            sock.listen(1)


            if "-gkc" in args:
                import gen_key_and_cert

            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # Creates a tls server object to later use
            context.load_cert_chain('tls_info/certificate.pem', 'tls_info/key.pem')

            with context.wrap_socket(sock, server_side=True) as stls: # Wraps the socket with tls, while also confirming that this device is the socket
                try:
                    connection, address = stls.accept()
                    connection.settimeout(15)
                except KeyboardInterrupt:
                    raise KeyboardInterrupt
                with connection:
                    confirmation_buffer = b""
                    while b"\t" not in confirmation_buffer:
                        confirmation_buffer += connection.recv(1)
                    connection.sendall(confirmation_buffer)

                    directory = inputimeout(prompt='Specify the directory to save each file: ', timeout=20)
                    os.makedirs(directory, exist_ok=True)

                    receive_file(connection, directory, stls)

    except socket.timeout:
        print("Socket timeout!!!\nMore than 15 seconds have passed by.")
    except KeyboardInterrupt:
        print("\nProgram ended by user")
    except FileNotFoundError as e:
        print(f"One or both of the following files are missing:\ncertificate.pem\nkey.pem")
    except TimeoutOccurred:
        print("You took to long, respond faster next time when asked for an input.")
    except ssl.SSLError:
        print("The key or certificate are not in a compatible format.\nConsider using the '-gkc' flag to generate a new key and certificate.")





if __name__ == "__main__":
    main()

