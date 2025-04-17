import os
import subprocess
from functools import partial
import json

from code_utils import extract_code
from iteration import Iteration
from logger import logger

PROJECT_ROOT = os.path.dirname(__file__)


def test_validation_callback(response, file_path="", test_file=""):
    project_type = "Rust" 

    rust_file = ".".join([file_path.split(".")[0], "rs"])

    response = extract_code(response, 'rust')

    with open(rust_file, 'w+') as f:
        f.write(response)

    compile_script = os.path.join(PROJECT_ROOT, 'compile_rust.sh')
    result = subprocess.run(
        [
            '/bin/bash', '-c',
            f"""
            source {compile_script} {os.path.dirname(file_path)} {os.path.splitext(os.path.basename(file_path))[0]}
            """
        ], 
        capture_output=True, 
        text=True,
        check=False
    )
    if result.returncode:
        return result.returncode, result.stderr

    result = subprocess.run(
        [
            '/bin/bash', '-c',
            f"""
            time python {test_file} {file_path.split('.')[0]} {project_type}
            """
        ], 
        capture_output=True, 
        text=True,
        check=False
    )
    if result.returncode:
        return result.returncode, result.stderr

    return 0, rust_file



def get_rust_gen_stage(meta_file, code_file, test_file):
    with open(meta_file, 'r') as f:
        ast = f.read()

    initial_query = f"""
Here's AST data structure which describes C program. 
Generate program in Rust based on this AST. 
Prepend all the functions with '#[no_mangle] pub extern "C"' so that rust code can be compiled into shared library.
Return only rust code! Ommit any comments. Omit explanations.  
AST: {json.dumps(json.loads(ast))} """
    
    stage = Iteration(
        initial_query=initial_query, 
        validation_callback=partial(
            test_validation_callback, 
            file_path=code_file, 
            test_file=test_file
        )
    )

    return stage