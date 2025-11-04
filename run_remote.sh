#!/bin/bash

# --- Configuration ---
VM1_HOST="vm1@192.168.122.34"
VM2_HOST="vm2@192.168.122.231"
PROJECT_DIR="InfraETL1"
LOCAL_OUTPUT_DIR="./output_from_vm"

echo "--- 1. Updating Repositories on VMs ---"
ssh $VM1_HOST "cd $PROJECT_DIR && git pull"
ssh $VM2_HOST "cd $PROJECT_DIR && git pull"

# --- 2. (NEW!) Get User Input ---
echo "--- 2. Get Number of Users ---"
while true; do
    read -p "Enter number of users to extract (e.g., 200 or 10000): " N_USERS
    # Check if it's an integer greater than 0
    if [[ "$N_USERS" =~ ^[1-9][0-9]*$ ]]; then
        break # Valid input, exit loop
    else
        echo "Invalid input. Please enter a number greater than 0."
    fi
done

# --- 3. Running Extraction on VM1 ---
echo "--- 3. Running Extraction on VM1 ---"
echo "Starting extraction for $N_USERS users..."
# Use the $N_USERS variable from the input above
ssh $VM1_HOST "cd $PROJECT_DIR && source venv/bin/activate && python3 run_extract_only.py $N_USERS | tee /dev/stderr"

# --- 4. Finding the Output Directory on VM1 ---
echo "--- 4. Finding latest run directory on VM1 ---"
LATEST_RUN_DIR=$(ssh $VM1_HOST "ls -td $PROJECT_DIR/output/*/ | head -1")
if [ -z "$LATEST_RUN_DIR" ]; then
    echo "Error: No output directory found on VM1."
    exit 1
fi
LATEST_RUN_DIR=$(echo $LATEST_RUN_DIR | sed 's:/*$::')
echo "Found: $LATEST_RUN_DIR"

# --- 5. Copying Data from VM1 to VM2 (Host is middle-man) ---
echo "--- 5. Transferring data from VM1 -> Host -> VM2 ---"
TEMP_DIR_NAME=$(basename $LATEST_RUN_DIR)
mkdir -p ./temp_run_data/$TEMP_DIR_NAME
scp -r $VM1_HOST:$LATEST_RUN_DIR/* ./temp_run_data/$TEMP_DIR_NAME/
ssh $VM2_HOST "mkdir -p $PROJECT_DIR/output"
scp -r ./temp_run_data/$TEMP_DIR_NAME $VM2_HOST:$PROJECT_DIR/output/
rm -rf ./temp_run_data
echo "Transfer complete."

# --- 6. Running Transform & Load on VM2 ---
echo "--- 6. Running Transform & Load on VM2 ---"
RUN_DIR_NAME=$(basename $LATEST_RUN_DIR)
VM2_RUN_PATH="output/$RUN_DIR_NAME"
ssh $VM2_HOST "cd $PROJECT_DIR && source venv/bin/activate && python3 run_transform_load.py $VM2_RUN_PATH | tee /dev/stderr"

# --- 7. Retrieving Final Dashboard from VM2 ---
echo "--- 7. Retrieving final dashboard from VM2 ---"
mkdir -p $LOCAL_OUTPUT_DIR
scp -r $VM2_HOST:$PROJECT_DIR/$VM2_RUN_PATH $LOCAL_OUTPUT_DIR/
echo "Done."
echo "Final dashboard and stats are in: $LOCAL_OUTPUT_DIR/$RUN_DIR_NAME"

# --- 8. Open Dashboard on Host ---
echo "--- 8. Opening dashboard in your browser... ---"
xdg-open "$LOCAL_OUTPUT_DIR/$RUN_DIR_NAME/dashboard.html"