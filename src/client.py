import socket
import time
import sys

from config import SERVER_IP, SERVER_PORT, SEND_INTERVAL, DELIMITER
from metrics import get_system_metrics, get_top_processes
from security import *


def create_packet(node_id, metrics):

    processes = get_top_processes()

    process_strings = []

    for p in processes:
        proc_str = f"{p['pid']}:{p['name']}:{p['cpu_percent']}:{round(p['memory_percent'],2)}:{p['read_kb']}:{p['write_kb']}"
        process_strings.append(proc_str)

    process_data = ",".join(process_strings)

    packet = DELIMITER.join([
        node_id,
        str(metrics["cpu"]),
        str(metrics["mem"]),
        str(metrics["disk"]),
        str(metrics["timestamp"]),
        process_data
    ])

    return packet


def perform_key_exchange(sock):

    private = generate_private_key()
    public = compute_public_key(private)

    # Send HELLO
    sock.sendto(f"HELLO|{public}".encode(), (SERVER_IP, SERVER_PORT))

    # Receive HELLO_ACK
    data, _ = sock.recvfrom(4096)
    msg = data.decode()

    if not msg.startswith("HELLO_ACK"):
        raise Exception("Key exchange failed")

    _, server_public = msg.split("|")
    server_public = int(server_public)

    shared_key = compute_shared_key(server_public, private)

    print("[KEY EXCHANGE COMPLETE]")

    return shared_key


def start_client(node_id):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[STARTED] UDP Client {node_id}")

    try:
        # Phase 1: Key exchange
        shared_key = perform_key_exchange(sock)

        # Phase 2: Monitoring loop
        while True:

            metrics = get_system_metrics()
            packet = create_packet(node_id, metrics).encode()

            signature = create_hmac(shared_key, packet)

            final_packet = signature + packet

            sock.sendto(final_packet, (SERVER_IP, SERVER_PORT))

            print(f"[SENT] {node_id}")

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("\nClient stopped gracefully.")


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python client.py <client_id>")
        sys.exit()

    node_id = sys.argv[1]

    start_client(node_id)