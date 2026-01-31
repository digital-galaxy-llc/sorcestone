# Run this script as 
# ./run.sh ../c2rust-samples/basic/basic.c  - If you do not have any special includes to mention
# ./run.sh ../c2rust-samples/basic/basic.c '-I/path/to/module1 -I/path/to/module2' - If have some special modules to include during preprocessing
PYTHONPATH=.  python sorcestone/run.py $1 --build_args="$2" C Rust
