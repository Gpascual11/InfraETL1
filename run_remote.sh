#!/bin/bash

# --- Robustness Settings ---
# Exit immediately if a command exits with a non-zero status.
set -e
# Make pipeline exit status the last non-zero status, or zero if all succeed.
set -o pipefail

# --- Configuration ---
VM1_HOST="vm1@192.168.122.34"
VM2_HOST="vm2@192.168.122.231"
PROJECT_DIR="InfraETL1"
LOCAL_OUTPUT_DIR="./output_from_vm"

# --- (NEW) Error Handling Function ---
# This function will be called whenever a command fails
# It prints a red error message and exits the script.
error_exit() {
    # Print to stderr in red
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
ssh $VM1_HOST "cd $PROJECT_DIR && source ~/.profile && source venv/bin/activate && python3 run_extract_only.py $N_USERS | tee /dev/stderr" \
    || error_exit "Extraction script failed on VM1."

# --- 4. Finding the Output Directory on VM1 ---
echo "--- 4. Finding latest run directory on VM1 ---"
# We must check for an empty directory variable, as this won't trigger 'set -e'
LATEST_RUN_DIR=$(ssh $VM1_HOST "ls -td $PROJECT_DIR/output/*/ | head -1")
if [ -z "$LATEST_RUN_DIR" ]; then
    error_exit "Could not find any output directory on VM1. (Is output/ empty?)"
fi
LATEST_RUN_DIR=$(echo $LATEST_RUN_DIR | sed 's:/*$::')
echo "Found: $LATEST_RUN_DIR"

# --- 5. Copying Data from VM1 to VM2 (Host is middle-man) ---
echo "--- 5. Transferring data from VM1 -> Host -> VM2 ---"
TEMP_DIR_NAME=$(basename $LATEST_RUN_DIR)
mkdir -p ./temp_run_data/$TEMP_DIR_NAME || error_exit "Failed to create temp directory on host."

scp -r $VM1_HOST:$LATEST_RUN_DIR/* ./temp_run_data/$TEMP_DIR_NAME/ \
    || error_exit "Failed to copy files from VM1 to host. (Did extraction create any files?)"

ssh $VM2_HOST "mkdir -p $PROJECT_DIR/output" || error_exit "Failed to create output directory on VM2."
scp -r ./temp_run_data/$TEMP_DIR_NAME $VM2_HOST:$PROJECT_DIR/output/ \
    || error_exit "Failed to copy files from host to VM2."

rm -rf ./temp_run_data
echo "Transfer complete."

# --- 6. Running Transform & Load on VM2 ---
echo "--- 6. Running Transform & Load on VM2 ---"
RUN_DIR_NAME=$(basename $LATEST_RUN_DIR)
VM2_RUN_PATH="output/$RUN_DIR_NAME"
ssh $VM2_HOST "cd $PROJECT_DIR && source ~/.profile && source venv/bin/activate && python3 run_transform_load.py $VM2_RUN_PATH | tee /dev/stderr" \
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