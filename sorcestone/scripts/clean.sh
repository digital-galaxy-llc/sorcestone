#!/bin/bash

# Enhanced clean script with safety and logging

# Logging function
# Clean function with improved safety
SAMPLE_FOLDER_PATH="$1"

if [ -z "$SAMPLE_FOLDER_PATH" ]; then 
    echo "[ERROR] Project name not provided" >&2
    return 1
fi

# Use safer removal with checks
local files_to_remove=(
    "$SAMPLE_FOLDER_PATH/*.c.so"
    "$SAMPLE_FOLDER_PATH/*.meta"
    "$SAMPLE_FOLDER_PATH/*.rs"
    "$SAMPLE_FOLDER_PATH/*.rs.so"
    "$SAMPLE_FOLDER_PATH/*.rust.so"
    "$SAMPLE_FOLDER_PATH/*_test.py"
)

for file in "${files_to_remove[@]}"; do
    if [ -f "$file" ]; then
        echo "Removing $file"
        rm -rf "$file"
    else
        echo "File not found: $file"
    fi
done

find $SAMPLE_FOLDER_PATH/*  -type d -maxdepth 1 | xargs -0 rm 

echo "Cleanup completed successfully"
