# Remote System Health Monitoring Service

A secure, multi-client system health monitoring tool built with Python and UDP sockets.  
Clients periodically send system metrics to a central server, which aggregates data,  
displays process-level details, and raises alerts when thresholds are exceeded.

---

## Architecture
```
Client 1 ──┐
Client 2 ──┼──► UDP ──► Aggregation Server ──► Alert Engine
Client 3 ──┘
```

Each client collects CPU, memory, and disk usage along with top running processes  
(similar to Task Manager) and sends signed packets to the server every 3 seconds.

---

## Security

Communication is secured using a two-phase mechanism:

1. **Diffie-Hellman Key Exchange** — Client and server negotiate a shared secret  
   without transmitting the key over the network.
2. **HMAC-SHA256 Authentication** — Every packet is signed with the shared key.  
   The server verifies the signature before processing; tampered packets are dropped.

---

## Project Structure
```
health_monitor_project/
├── server.py          # UDP aggregation server with threading
├── client.py          # Monitoring agent
├── metrics.py         # psutil-based system & process data collection
├── alert_engine.py    # Threshold-based alert logic
├── config.py          # Network settings and thresholds
├── security.py        # DH key exchange + HMAC utilities
└── dh_params.py       # Public DH parameters
```

---

## Setup
```bash
pip install psutil cryptography
python server.py
python client.py client1   # run in separate terminals
python client.py client2
```

---

## Alert Thresholds (configurable in config.py)

| Metric | Threshold |
|--------|-----------|
| CPU    | > 80%     |
| Memory | > 90%     |
| Disk   | > 85%     |
