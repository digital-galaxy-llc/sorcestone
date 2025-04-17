import subprocess
from functools import partial
from code_utils import extract_code

from iteration import Iteration, FakeIteration
from logger import logger


def get_test_file_name(file_path):
    return "_".join([file_path.split(".")[0], "test.py"])


def test_validation_callback(response, file_path="", project_type = 'C'):
    test_file = get_test_file_name(file_path)
    response = extract_code(response, 'python')

    with open(test_file, 'w+') as f:
        f.write(response)
    logger.info("Checking that C code passes meta test")
    
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
    
    return 0, test_file


def get_test_gen_stage(meta_file, code_file, skip=False):
    
    if skip:
        return FakeIteration(fake_response=get_test_file_name(code_file))    
    
    with open(meta_file, 'r') as f:
        ast = f.read()

    initial_query = f"""
Task: Generate Test script which will test everfy function described by the provided AST. Verify function signature and ouput typles.
Notes: 
    - AST describes C code
    - Functional test should be done in python. 
    - To make me able to run script from the console add arguments parsing for project_name and project_type 
    - to test shared libararies we should use ctypes and cffi
    - for project_type == C assume lib file '<project_name>.c.so' and for project_type == Rust assume lib file '<project_name>.rs.so'
    - your answer is going to be stored as python file so ommit all the explanations, comments. return python code only.
AST: {ast} 
Knowledgebased:
- Use cffi to do cdef
- In case of - TypeError: incompatible types, <some type> instance instead of c_char_p instance c. We may cast it to c_char_p
 s = create_string_buffer(b'test')
 f = cast(s,c_char_p)
"""
    
    stage = Iteration(initial_query=initial_query, validation_callback=partial(test_validation_callback, file_path=code_file))

    return stage
