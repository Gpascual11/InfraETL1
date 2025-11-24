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

Aquí tienes el texto en Markdown listo para copiar y pegar al final de tu `README.md`.

He mantenido el idioma inglés para que sea coherente con el resto de tu documentación, y he añadido los iconos y el formato de tablas para que siga el mismo estilo visual profesional.

-----

## AWS Cloud Demo: Interactive Dashboard & RDS

This project has been enhanced with a Cloud Deployment feature using **Amazon Web Services (AWS)**. This allows public access to the dashboard, mobile interaction via QR Code, and persistent data storage for the password auditing feature.

### Cloud Architecture

| Component | Service | Purpose |
| :--- | :--- | :--- |
| **Compute** | **AWS EC2** (Ubuntu) | Hosts the ETL pipeline execution and the Flask Web Server. Replaces the local VMs. |
| **Database** | **AWS RDS** (PostgreSQL) | Persistently stores the random passwords input by users from the dashboard. |
| **Networking** | **Security Groups** | Manages traffic (Port 80 for Web, 22 for SSH, 5432 for Database). |
| **Access** | **Public IP + QR** | Allows any device (mobile/desktop) to access the dashboard globally. |

### Deployment Guide (Step-by-Step)

Follow these steps to deploy the demo on AWS:

#### 1. Infrastructure Setup
* **RDS:** Create a PostgreSQL instance (Free Tier). Enable **Public Access**. Note the **Endpoint** and **Master Password**.
* **EC2:** Launch an Ubuntu instance (`t2.micro`). Ensure the Security Group allows **HTTP (80)** and **SSH (22)** from `0.0.0.0/0`.
* **Connection:** Edit the RDS Security Group to allow Inbound traffic on port **5432** from "My IP" (for local testing) or `0.0.0.0/0` (for the demo).

#### 2. Project Configuration
Before uploading, configure the `app.py` file locally with your RDS credentials:
```python
# app.py
DB_HOST = "your-rds-endpoint.us-east-1.rds.amazonaws.com"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "YourSecurePassword!"
````

#### 3\. Upload & Install

Transfer the project files to the EC2 instance using your `.pem` key:

```bash
# From your local machine
scp -i "demo-key.pem" *.py *.html ubuntu@<EC2_PUBLIC_IP>:~/my_project/
```

SSH into the instance and install dependencies:

```bash
ssh -i "demo-key.pem" ubuntu@<EC2_PUBLIC_IP>

# Inside EC2
sudo apt update && sudo apt install python3-pip python3-venv libpq-dev -y
python3 -m venv venv
source venv/bin/activate
pip install flask pandas psycopg2-binary faker requests cryptography
```

#### 4\. Environment Setup

Set the encryption key persistently in the EC2 instance (run once):

```bash
echo 'export ETL_ENCRYPTION_KEY="_xERQLzrYUJPTxcYbVT9y0OjSMlczaW1meXCc4rLw7g="' >> ~/.bashrc
source ~/.bashrc
```

#### 5\. Run the Demo

1.  **Generate Data:** Run the ETL pipeline to create the `output` folder and dashboard.
    ```bash
    python3 main.py
    ```
2.  **Start Web Server:** Launch the Flask app on port 80.
    ```bash
    sudo ./venv/bin/python3 app.py
    ```

### How to Use the Live Demo

1.  Open your browser and navigate to `http://<EC2_PUBLIC_IP>`.
2.  View the generated **ETL Statistics**.
3.  Go to the **"Connect & DB"** tab.
4.  **Scan the QR Code** with your mobile phone to open the dashboard on your device.
5.  Enter a text/password in the input field and click **"Save to AWS RDS"**.
6.  The data is securely sent to the PostgreSQL database in the cloud\! ✅
7.  (Optional) Verify the data insertion by executing the 'see_bd.py'.

<!-- end list -->

```