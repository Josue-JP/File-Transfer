# File-Transfer

Easy way to transfer files inside the local network!

***This project is still a work in beta!!!***

### Steps for use:

1. When connecting to another device, please specify the correct `SERVER_IP` and `PORT` address located on lines 6 & 7 of the *cli.py* file.
2. Now start the **ser.py** file on the device that will receive the files — i.e., the server device.
3. After the receiving device initiates the connection, start the **cli.py** file on the client host that will send the files.

### Examples

Client's perspective using the *cli.py* file:

```bash
Connected to 127.0.0.1:12345
Specify the file to send: text.txt
```

Server's perspective using the *ser.py* file:

```bash
Press CTRL+C to exit, or wait for a client's response
Specify the directory to save each file: test
Saved text.txt as test/text.txt
```
