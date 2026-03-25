# System Health Monitoring over UDP

A secure, multi-client system health monitoring tool built with Python and UDP sockets. Clients run on remote machines and periodically collect CPU, memory, and disk metrics along with top running processes — similar to Task Manager — and send cryptographically signed packets to a central aggregation server every 3 seconds. The server displays live metrics, process tables, and raises alerts when thresholds are exceeded.

---

## Architecture

```
Client 1 (Node A) ──┐
Client 2 (Node B) ──┼──► UDP Socket ──► Aggregation Server ──► Alert Engine
Client 3 (Node C) ──┘                        │
                                             ▼
                                     Console Dashboard
```

Each client is an independent monitoring agent. The server handles multiple clients concurrently using threads — one thread per incoming packet.

---

## Security

Communication is secured using a two-phase mechanism before any metrics are transmitted:

### Phase 1 — Diffie-Hellman Key Exchange
When a client connects, it sends a `HELLO` message with its public DH key. The server responds with its own public key (`HELLO_ACK`). Both sides independently compute the same shared secret without ever transmitting it over the network. The shared secret is then hashed with SHA-256 to produce the session key.

### Phase 2 — HMAC-SHA256 Packet Authentication
Every metrics packet is signed using the session key via HMAC-SHA256. The 32-byte HMAC is prepended to each packet. The server verifies the signature on every received packet — any tampered or forged packet is silently dropped.

```
[ 32-byte HMAC ] + [ Payload ]
       ↓
  Server verifies HMAC before processing payload
```

> **Note:** The DH parameters (`P=23, G=5`) in `dh_params.py` are intentionally small for demonstration purposes. In production, use RFC 3526 group parameters (2048-bit or larger primes).

---

## Project Structure

```
System-Health-Monitoring-UDP/
├── src/
│   ├── server.py          # UDP aggregation server with per-packet threading
│   ├── client.py          # Monitoring agent — collects and sends metrics
│   ├── metrics.py         # psutil-based CPU, memory, disk, process collection
│   ├── alert_engine.py    # Threshold-based alert logic
│   ├── config.py          # Network settings and alert thresholds
│   ├── security.py        # DH key exchange + HMAC-SHA256 utilities
│   └── dh_params.py       # Public DH parameters (P, G)
└── README.md
```

---

## Requirements

- Python 3.7+
- `psutil` library

---

## Setup & Installation

### Linux / macOS

```bash
# Clone the repository
git clone https://github.com/CN-PROJECT-4H/System-Health-Monitoring-UDP.git
cd System-Health-Monitoring-UDP/src

# Install dependency
pip3 install psutil
```

### Windows

```cmd
git clone https://github.com/CN-PROJECT-4H/System-Health-Monitoring-UDP.git
cd System-Health-Monitoring-UDP\src

pip install psutil
```

### Using a Virtual Environment (recommended for all platforms)

```bash
# Create and activate venv — Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Create and activate venv — Windows
python -m venv venv
venv\Scripts\activate

# Install
pip install psutil
```

---

## Running the Project

> All commands assume you are inside the `src/` directory.

### Step 1 — Start the Server

**Linux / macOS**
```bash
python3 server.py
```

**Windows**
```cmd
python server.py
```

Expected output:
```
UDP Secure Server running on 127.0.0.1:9999
```

---

### Step 2 — Start One or More Clients

Open a new terminal for each client.

**Linux / macOS**
```bash
python3 client.py client1
```

**Windows**
```cmd
python client.py client1
```

For multiple clients, open additional terminals:
```bash
python3 client.py client2
python3 client.py client3
```

Expected output on client:
```
[STARTED] UDP Client client1
[KEY EXCHANGE COMPLETE]
[SENT] client1
[SENT] client1
...
```

Expected output on server:
```
[KEY ESTABLISHED] ('127.0.0.1', 54321)

Client: client1 (('127.0.0.1', 54321))
CPU Usage: 23.4%
Memory Usage: 61.2%
Disk Usage: 45.0%

PID      Process Name         CPU%     MEM%     READ(KB)     WRITE(KB)
--------------------------------------------------
1234     chrome               12.3     4.5      102.5        50.2
...
```

---

## Configuration

Edit `config.py` to change network settings or alert thresholds:

```python
SERVER_IP = "127.0.0.1"   # Change to server's IP for remote monitoring
SERVER_PORT = 9999
SEND_INTERVAL = 3          # Seconds between each metrics packet

CPU_THRESHOLD    = 80      # Alert if CPU    > 80%
MEMORY_THRESHOLD = 90      # Alert if Memory > 90%
DISK_THRESHOLD   = 85      # Alert if Disk   > 85%
```

To monitor across machines on the same network, set `SERVER_IP` to the server machine's local IP address (e.g. `192.168.1.10`) in `config.py` on each client machine.

---

## Alert Thresholds

| Metric | Default Threshold | Configurable |
|--------|-------------------|--------------|
| CPU    | > 80%             | Yes          |
| Memory | > 90%             | Yes          |
| Disk   | > 85%             | Yes          |

When a threshold is exceeded, the server prints:
```
[ALERT] client1 CPU usage = 91.2% (Threshold 80%)
```
