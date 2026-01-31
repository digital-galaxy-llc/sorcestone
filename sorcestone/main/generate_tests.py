import subprocess
from functools import partial
from sorcestone.utils.code_utils import extract_code

from sorcestone.main.iteration import Iteration, FakeIteration
from sorcestone.utils.logger import logger


def get_test_file_name(file_path, dst_language):
    return "_".join([file_path.split(".")[0], dst_language, "test.py"])


def test_validation_callback(response, file_path="", src_language="C", dst_language="Rust"):
    test_file = get_test_file_name(file_path, dst_language)
    response = extract_code(response, 'python')

    with open(test_file, 'w+') as f:
        f.write(response)
    logger.info(f"Checking that {src_language} code passes tests and is compatible with {dst_language} interface")
    
    result = subprocess.run(
        [
            '/bin/bash', '-c',
            f"""
            time python {test_file} {file_path} {src_language}
            """
        ],
        capture_output=True, 
        text=True,
        check=False
    )
    if result.returncode:
        return result.returncode, result.stderr
    
    return 0, test_file

IMPORTANT_REQUIREMENTS = {
    "C": """
        - For string handling in C-compatible languages:
            s = create_string_buffer(b'test')
            f = cast(s,c_char_p)
    """,
    "Java": """
        - For Java code assume that class name is going to be equal to file name in UpperCamelCase
        - For Java code assume that method name is going to be equal to function name in lowerCamelCase
        - For Java code assume that it will be in package com.<file name>
        - For Java code assume that it will have public static void main(String[] args) {}
        - For Java code assume that all methods in Java class will be with modificators "public static"
        - For Java code assume that test will call it via jpype.JClass as com.<file name>.<class name>
     """
}

def get_test_gen_stage(meta_file, code_file, src_language="C", dst_language="Rust", skip=False):
    
    if skip:
        return FakeIteration(fake_response=get_test_file_name(code_file, dst_language))
    
    with open(meta_file, 'r') as f:
        ast = f.read()

    initial_query = f"""
Task: Generate Test script which will test every function described by the provided AST. Verify function signatures and output types.
Notes:
    - AST describes {src_language} code that will be translated to {dst_language}
    - Functional test should be done in Python
    - To make me able to run script from the console add mandatory arguments parsing for:
      - lib_path: base name for the .so file
      - language: which should be {src_language} or {dst_language}
    - To test shared libraries we should use ctypes and cffi
    - Test is going to be started as: python <test_file_path> <.so file path> <language .so was created from>
    - Verify that both libraries provide identical results
    - Your answer is going to be stored as python file so omit all explanations, comments. Return python code only.
AST: {ast}
Knowledge base:
- Use cffi to do cdef for C-compatible languages
{IMPORTANT_REQUIREMENTS.get(src_language, "")}
{IMPORTANT_REQUIREMENTS.get(dst_language, "")}
"""
    
    stage = Iteration(
        initial_query=initial_query,
        validation_callback=partial(
            test_validation_callback,
            file_path=code_file,
            src_language=src_language,
            dst_language=dst_language
        )
    )

    return stage 
