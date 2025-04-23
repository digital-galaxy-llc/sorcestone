echo "== File to be compiled $1"  
time gcc -shared -fPIC $1.c -o $1.c.so
