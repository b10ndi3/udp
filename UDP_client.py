#!/usr/bin/env python3
import sys, socket

USAGE = "Usage: python UDP_client.py HELLO Server_IP Server_Port ConnectionID"
RECV_TIMEOUT = 60.0
MAX_TRIES = 3

def attempt(server_ip, server_port, conn_id):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(RECV_TIMEOUT)
    try:
        sock.sendto(f"HELLO {conn_id}".encode(), (server_ip, server_port))
        data, _ = sock.recvfrom(4096)
        parts = data.decode(errors="ignore").strip().split()

        if len(parts) >= 2 and parts[0].upper() == "RESET" and parts[1] == conn_id:
            print(f"Connection Error {conn_id}")
            return False

        if len(parts) >= 2 and parts[0].upper() == "OK" and parts[1] == conn_id:
            if len(parts) >= 4:
                ip, port = parts[2], parts[3]
            else:
                ip, port = sock.getsockname()[0], str(sock.getsockname()[1])
            print(f"Connection established {conn_id} {ip} {port}")
            return True

        print(f"Connection Error {conn_id}")
        return False

    except (socket.timeout, ConnectionResetError, OSError):
        print(f"Connection Error {conn_id}")
        return False
    finally:
        sock.close()

def main():
    if len(sys.argv) != 5 or sys.argv[1] != "HELLO":
        print(USAGE)
        return

    server_ip = sys.argv[2]
    server_port = int(sys.argv[3])
    conn_id = sys.argv[4]

    tries = 0
    while tries < MAX_TRIES:
        if attempt(server_ip, server_port, conn_id):
            return
        tries += 1

    print("Connection Failure")

if __name__ == "__main__":
    main()
