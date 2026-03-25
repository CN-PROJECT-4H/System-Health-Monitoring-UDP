import socket
import threading

from config import SERVER_IP, SERVER_PORT
from alert_engine import check_alerts
from security import *


client_keys = {}   # addr → shared_key


def parse_packet(packet):

    parts = packet.split("|")

    node_id = parts[0]
    cpu = float(parts[1])
    mem = float(parts[2])
    disk = float(parts[3])
    timestamp = int(parts[4])

    processes = []

    if len(parts) > 5 and parts[5]:

        process_list = parts[5].split(",")

        for p in process_list:
            try:
                pid, name, cpu_p, mem_p, read_kb, write_kb = p.split(":")

                processes.append({
                    "pid": pid,
                    "name": name,
                    "cpu": float(cpu_p),
                    "mem": float(mem_p),
                    "read": float(read_kb),     #  now KB
                    "write": float(write_kb)    #  now KB
                })

            except:
                continue

    return node_id, cpu, mem, disk, timestamp, processes


def print_process_table(processes):

    print("\n{:<8} {:<20} {:<8} {:<8} {:<12} {:<12}".format(
    "PID", "Process Name", "CPU%", "MEM%", "READ(KB)", "WRITE(KB)"))
    print("-" * 50)

    for p in processes:
        name = p['name'] if p['name'] else "Unknown"

        print("{:<8} {:<20} {:<8} {:<8} {:<12} {:<12}".format(
            p['pid'],
            name,
            p['cpu'],
            p['mem'],
            p['read'],
            p['write']
        ))

    print("-" * 50)


def process_packet(data, addr, server_socket):

    # Phase 1: Handle key exchange
    if data.startswith(b"HELLO"):

        try:
            _, client_public = data.decode().split("|")
            client_public = int(client_public)

            private = generate_private_key()
            public = compute_public_key(private)

            # Send HELLO_ACK
            server_socket.sendto(f"HELLO_ACK|{public}".encode(), addr)

            shared_key = compute_shared_key(client_public, private)

            client_keys[addr] = shared_key

            print(f"[KEY ESTABLISHED] {addr}")

        except Exception as e:
            print(f"[ERROR] Key exchange failed: {e}")

        return

    # Phase 2: Verify HMAC
    key = client_keys.get(addr)

    if not key:
        print(f"[WARNING] No key for {addr}")
        return

    received_hmac = data[:32]
    payload = data[32:]

    if not verify_hmac(key, payload, received_hmac):
        print(f"[DROP] Tampered packet from {addr}")
        return

    try:
        packet = payload.decode()

        node_id, cpu, mem, disk, timestamp, processes = parse_packet(packet)

        print(f"\nClient: {node_id} ({addr})")
        print(f"CPU Usage: {cpu}%")
        print(f"Memory Usage: {mem}%")
        print(f"Disk Usage: {disk}%")

        print_process_table(processes)

        metrics = {"cpu": cpu, "mem": mem, "disk": disk}
        check_alerts(node_id, metrics)

    except Exception as e:
        print(f"[ERROR] Processing packet failed: {e}")


def start_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f"UDP Secure Server running on {SERVER_IP}:{SERVER_PORT}")

    while True:
        data, addr = server_socket.recvfrom(4096)

        # Thread per packet
        thread = threading.Thread(
            target=process_packet,
            args=(data, addr, server_socket)
        )
        thread.start()


if __name__ == "__main__":
    start_server()