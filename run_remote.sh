#!/bin/bash

# --- Configuration ---
# !! REMEMBER TO CHANGE THESE !!
VM1_HOST="vm1@192.168.122.34"
VM2_HOST="vm2@192.168.122.231"
PROJECT_DIR="InfraETL1"
LOCAL_OUTPUT_DIR="./output_from_vm"

echo "--- 1. Updating Repositories on VMs ---"
ssh $VM1_HOST "cd $PROJECT_DIR && git pull"
ssh $VM2_HOST "cd $PROJECT_DIR && git pull"

# --- 2. Running Extraction on VM1 (CORRECTED) ---
echo "--- 2. Running Extraction on VM1 ---"
# Call the new extract-only script, requesting 10,000 users.
# The 'tee' command lets us see the output in our host terminal
ssh $VM1_HOST "cd $PROJECT_DIR && source venv/bin/activate && python3 run_extract_only.py 10000 | tee /dev/stderr"

# --- 3. Finding the Output Directory on VM1 ---
echo "--- 3. Finding latest run directory on VM1 ---"
# This command finds the most recently modified output directory
LATEST_RUN_DIR=$(ssh $VM1_HOST "ls -td $PROJECT_DIR/output/*/ | head -1")
if [ -z "$LATEST_RUN_DIR" ]; then
    echo "Error: No output directory found on VM1."
    exit 1
fi
# Remove trailing slash for consistency
LATEST_RUN_DIR=$(echo $LATEST_RUN_DIR | sed 's:/*$::')
echo "Found: $LATEST_RUN_DIR"

# --- 4. Copying Data from VM1 to VM2 (Host is middle-man) ---
echo "--- 4. Transferring data from VM1 -> Host -> VM2 ---"
# Create a temp dir on host
TEMP_DIR_NAME=$(basename $LATEST_RUN_DIR)
mkdir -p ./temp_run_data/$TEMP_DIR_NAME

# Copy dir from VM1 to host
scp -r $VM1_HOST:$LATEST_RUN_DIR/* ./temp_run_data/$TEMP_DIR_NAME/

# Ensure target output dir exists on VM2
ssh $VM2_HOST "mkdir -p $PROJECT_DIR/output"
# Copy from host to VM2
scp -r ./temp_run_data/$TEMP_DIR_NAME $VM2_HOST:$PROJECT_DIR/output/

# Clean up host
rm -rf ./temp_run_data
echo "Transfer complete."

# --- 5. Running Transform & Load on VM2 ---
echo "--- 5. Running Transform & Load on VM2 ---"
# We get the directory name (not the full path)
RUN_DIR_NAME=$(basename $LATEST_RUN_DIR)
VM2_RUN_PATH="$PROJECT_DIR/output/$RUN_DIR_NAME"
ssh $VM2_HOST "cd $PROJECT_DIR && source venv/bin/activate && python3 run_transform_load.py $VM2_RUN_PATH | tee /dev/stderr"

# --- 6. Retrieving Final Dashboard from VM2 ---
echo "--- 6. Retrieving final dashboard from VM2 ---"
mkdir -p $LOCAL_OUTPUT_DIR
scp -r $VM2_HOST:$VM2_RUN_PATH $LOCAL_OUTPUT_DIR/
echo "Done."
echo "Final dashboard and stats are in: $LOCAL_OUTPUT_DIR/$RUN_DIR_NAME"