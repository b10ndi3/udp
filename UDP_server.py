#!/usr/bin/env python3
import sys, socket, time

USAGE = "Usage: python3 UDP_server.py Server_IP Server_Port"

def main():
    if len(sys.argv) != 3:
        print(USAGE); return
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((server_ip, server_port))
    sock.settimeout(1.0)  # poll once per second

    in_use = {}  # conn_id -> timestamp when reserved
    last_req_time = time.time()

    def cleanup_ids(now):
        # remove IDs older than 60 seconds
        expired = [cid for cid, ts in in_use.items() if now - ts > 60]
        for cid in expired:
            del in_use[cid]

    while True:
        now = time.time()
        cleanup_ids(now)

        # Exit if idle for 5 minutes
        if now - last_req_time > 300:
            break

        try:
            data, addr = sock.recvfrom(4096)
        except socket.timeout:
            continue

        last_req_time = time.time()
        try:
            msg = data.decode().strip()
        except UnicodeDecodeError:
            continue

        parts = msg.split()
        if len(parts) != 2 or parts[0] != "HELLO":
            continue  # ignore malformed

        conn_id = parts[1]
        client_ip, client_port = addr[0], addr[1]

        if conn_id in in_use:
            reply = f"RESET {conn_id}"
        else:
            in_use[conn_id] = time.time()
            reply = f"OK {conn_id} {client_ip} {client_port}"

        sock.sendto(reply.encode(), addr)

    sock.close()

if __name__ == "__main__":
    main()
