PROJECT_FOLDER=$1
PROJECT_NAME=$2

cd $PROJECT_FOLDER
echo "=== Clean ==="
rm -rf $PROJECT_NAME
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
cp ../$PROJECT_NAME.rs src/lib.rs

echo "=== Check lib RS ==="
cat src/lib.rs

echo "=== Build ==="
time cargo build --release 
BUILD_RETURN_CODE=$?

echo "=== Copy artefact ==="
cp target/release/lib$PROJECT_NAME.dylib ../$PROJECT_NAME.rust.so
cp target/release/lib$PROJECT_NAME.dylib ../$PROJECT_NAME.rs.so

echo "=== Done ==="
cd ../
exit $BUILD_RETURN_CODE
