# InfraETL1: Distributed ETL Pipeline

This repository contains a secure, distributed Extract, Transform, and Load (ETL) pipeline designed to process user data from the **RandomUser API**. The system distributes workload across two separate Linux Virtual Machines (VMs) and delivers the final statistical dashboard via a web server.

## Architecture & Design Philosophy

The project adheres to the principle of **Separation of Concerns** by dividing the workload based on computational requirements (I/O vs. CPU).

| Component | Responsibility | Location | Workload Type | Key Files |
| :--- | :--- | :--- | :--- | :--- |
| **Extractor** | Fetch data from API, filter by country, check for nulls, and **encrypt the output**. | **VM1 (Ubuntu)** | I/O Bound (Network Waiting) | `extractor.py`, `run_extract_only.py` |
| **Transformer & Loader** | Decrypt data, validate content, calculate statistics, audit passwords, and **generate dashboard files**. | **VM2 (Ubuntu)** | CPU Bound (Processing/Calculations) | `transformer.py`, `loader.py`, `run_transform_load.py` |
| **Orchestrator** | Coordinates execution, manages SSH connections, transfers files (VM1 → VM2), and starts the web server. | **Host Machine (Your Laptop)** | Control/Management | `run_remote.sh` |
| **Delivery** | Hosts the final results for easy access. | **VM2 (HTTP Server)** | Network Serving | `dashboard_template.html` |

### Security Model (Shared Secret)

To maintain security while transferring data, the system uses a **Shared Secret Key** stored as an environment variable (`ETL_ENCRYPTION_KEY`) on both VM1 and VM2. The encryption key **is never** stored in the repository or sent across the network.

-----

## Project Structure

| File / Folder | Role | Purpose |
| :--- | :--- | :--- |
| `run_remote.sh` | **MAIN ENTRY POINT** | Executes the entire pipeline sequence from the host, managing SSH, file transfer, and server deployment. |
| `run_extract_only.py` | VM1 Execution Script | Starts the Extractor, loads the secure key, and saves the encrypted CSV. |
| `run_transform_load.py` | VM2 Execution Script | Loads the secure key, runs the Transformer, Auditor, and Loader, and merges statistics. |
| `pipeline.py` | Local Execution | Legacy file used for local testing (not used in the distributed pipeline). |
| `extractor.py` | ETL Phase 1 (Core) | Handles API calls, multi-threading, geo-filtering, and initial validation. |
| `transformer.py` | ETL Phase 2 (Core) | Decrypts data, performs data cleaning, and calculates descriptive statistics. |
| `loader.py` | ETL Phase 3 (Core) | Saves final results to JSON, generates `dashboard.html`, and handles chart data injection. |
| `passwordauditor.py` | Helper Class | Specialized class to calculate password complexity, entropy, and detect personal info usage. |
| `CSVHelper.py` | Helper Class | Manages data serialization (flattening/unflattening) and the Fernet encryption/decryption process. |
| `validator.py` | Helper Class | Contains static methods for checking for nulls, data types, and strange characters. |
| `templates/` | Assets | Holds the `dashboard_template.html` used by the Loader. |

-----

## How to Execute the Pipeline

This pipeline requires two Linux VMs (e.g., Ubuntu Server on QEMU/KVM or similar) reachable by SSH from your host machine.

### Phase 1: VM Setup (One-Time)

You must configure the following on both VMs:

1.  **Software Installation:** Install prerequisites (`git`, `python3-pip`, `python3-venv`).
2.  **SSH Trust (Host to VMs):** Set up passwordless SSH from your Host to both VM1 and VM2 using `ssh-copy-id`.
3.  **SSH Trust (VM2 to VM1):** Set up passwordless SSH from **VM2 to VM1** for direct file transfer (`scp`).
4.  **Security Key:** Define your secret key on both machines in the `~/.profile` file:
    ```bash
    # IMPORTANT: The key must be identical on both VMs.
    export ETL_ENCRYPTION_KEY="PASTE_YOUR_44_CHARACTER_FERNET_KEY_HERE="
    ```
5.  **Firewall:** Allow incoming connections on port 8000 for the web server on **VM2 only**:
    ```bash
    sudo ufw allow 8000/tcp
    ```

### Phase 2: Configuration

1.  Clone this repository onto your host machine.

2.  Edit the `run_remote.sh` script on your **host machine** to set the correct connection details:

    ```bash
    VM1_HOST="vm1_user@vm1_ip_address"
    VM2_HOST="vm2_user@vm2_ip_address"
    PROJECT_DIR="InfraETL1" 
    ```

### Phase 3: Execution

Run the orchestrator script from your host machine's terminal within the project directory:

```bash
./run_remote.sh
```

The script will prompt you for the number of users, execute the ETL on the remote machines, and automatically open the final dashboard URL (`http://<VM2_IP>:8000/dashboard.html`) in your browser.
