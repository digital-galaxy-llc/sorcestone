#!/bin/bash
SRC_FILE=$1
DST_FILE=$2

echo "== Source file to be compiled $SRC_FILE"  
echo "== Output file to be created $DST_FILE"  

BUILD_FOLDER=$(mktemp -d)
PROJECT_NAME=$(basename $(dirname  $SRC_FILE))

cd $BUILD_FOLDER
echo "BUILD_DIR - ${BUILD_FOLDER}"
echo "=== Init ==="
cargo new --lib $PROJECT_NAME 
cd $PROJECT_NAME 
echo "=== Fix Cargo Toml ==="
echo "" >> Cargo.toml
echo "[lib]" >> Cargo.toml
echo 'crate-type = ["cdylib"]' >> Cargo.toml
echo "" >> Cargo.toml
echo "=== Check Cargo Toml ==="
cat Cargo.toml

echo "=== Copy Source Code ==="
cp $SRC_FILE src/lib.rs

echo "=== Check lib RS ==="
cat src/lib.rs

echo "=== Build ==="
time cargo build --release
BUILD_RETURN_CODE=$?

echo "=== Copy artefact ==="
cp target/release/lib$PROJECT_NAME.dylib $DST_FILE

rm -rf $BUILD_FOLDER
echo "=== Done ==="
exit $BUILD_RETURN_CODE
