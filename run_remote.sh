#!/bin/bash

# --- Robustness Settings ---
set -e
set -o pipefail

# --- Configuration ---
VM1_HOST="vm1@192.168.122.34"
VM2_HOST="vm2@192.168.122.231"
PROJECT_DIR="InfraETL1"
LOCAL_OUTPUT_DIR="./output_from_vm"

# --- Error Handling Function ---
error_exit() {
    echo -e "\n\n\033[0;31m--- SCRIPT FAILED ---\033[0m"
    echo -e "\033[0;31mError: $1\033[0m" >&2
    exit 1
}

# --- 1. Updating Repositories on VMs ---
echo "--- 1. Updating Repositories on VMs ---"
ssh $VM1_HOST "cd $PROJECT_DIR && git pull" || error_exit "Failed to pull updates on VM1."
ssh $VM2_HOST "cd $PROJECT_DIR && git pull" || error_exit "Failed to pull updates on VM2."

# --- 2. Get User Input ---
echo "--- 2. Get Number of Users ---"
while true; do
    read -p "Enter number of users to extract (e.g., 200 or 10000): " N_USERS
    if [[ "$N_USERS" =~ ^[1-9][0-9]*$ ]]; then
        break
    else
        echo "Invalid input. Please enter a number greater than 0."
    fi
done

# --- 3. Running Extraction on VM1 ---
echo "--- 3. Running Extraction on VM1 ---"
echo "Starting extraction for $N_USERS users..."
# --- (FIXED: Removed '| tee /dev/stderr') ---
ssh $VM1_HOST "cd $PROJECT_DIR && source ~/.profile && source venv/bin/activate && python3 run_extract_only.py $N_USERS" \
    || error_exit "Extraction script failed on VM1."

# --- 4. Finding the Output Directory on VM1 ---
echo "--- 4. Finding latest run directory on VM1 ---"
LATEST_RUN_DIR=$(ssh $VM1_HOST "ls -td $PROJECT_DIR/output/*/ | head -1")
if [ -z "$LATEST_RUN_DIR" ]; then
    error_exit "Could not find any output directory on VM1. (Is output/ empty?)"
fi
LATEST_RUN_DIR=$(echo $LATEST_RUN_DIR | sed 's:/*$::')
echo "Found: $LATEST_RUN_DIR"

# --- 5. Transferring Data Directly (VM2 pulls from VM1) ---
echo "--- 5. Transferring data directly from VM1 -> VM2 ---"
ssh $VM2_HOST "mkdir -p $PROJECT_DIR/output && scp -r $VM1_HOST:$LATEST_RUN_DIR $PROJECT_DIR/output/" \
    || error_exit "Failed to copy files directly from VM1 to VM2. (Did you set up SSH keys between VMs?)"
echo "Transfer complete."

# --- 6. Running Transform & Load on VM2 ---
echo "--- 6. Running Transform & Load on VM2 ---"
RUN_DIR_NAME=$(basename $LATEST_RUN_DIR)
VM2_RUN_PATH="output/$RUN_DIR_NAME"
# --- (FIXED: Removed '| tee /dev/stderr') ---
ssh $VM2_HOST "cd $PROJECT_DIR && source ~/.profile && source venv/bin/activate && python3 run_transform_load.py $VM2_RUN_PATH" \
    || error_exit "Transform & Load script failed on VM2."

# --- 7. Retrieving Final Dashboard from VM2 ---
echo "--- 7. Retrieving final dashboard from VM2 ---"
mkdir -p $LOCAL_OUTPUT_DIR || error_exit "Failed to create local output directory on host."
scp -r $VM2_HOST:$PROJECT_DIR/$VM2_RUN_PATH $LOCAL_OUTPUT_DIR/ \
    || error_exit "Failed to retrieve final dashboard from VM2."

echo "Done."
echo "Final dashboard and stats are in: $LOCAL_OUTPUT_DIR/$RUN_DIR_NAME"

# --- 8. Open Dashboard on Host ---
echo "--- 8. Opening dashboard in your browser... ---"
xdg-open "$LOCAL_OUTPUT_DIR/$RUN_DIR_NAME/dashboard.html" || error_exit "Failed to open dashboard. (Is xdg-open installed?)"

echo -e "\n\033[0;32m--- SCRIPT COMPLETED SUCCESSFULLY ---\033[0m"