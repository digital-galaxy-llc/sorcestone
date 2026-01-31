import os
import subprocess
from functools import partial
import json

from sorcestone.utils.code_utils import extract_code
from sorcestone.main.iteration import Iteration
from sorcestone.utils.logger import logger
from sorcestone.main.compile import compile_code

PROJECT_ROOT = os.path.dirname(__file__)


def test_validation_callback(response, file_path="", test_file="", dest_lang=""):
    response = extract_code(response, dest_lang.lower())

    # Before we Compile we may need to fix LLM errors - Thigns which LLM do not know yet
    # Replace #[no_mangle] with #[unsafe(no_mangle)]
    response = response.replace('#[no_mangle]', '#[unsafe(no_mangle)]')
    
    with open(file_path, 'w+') as f:
        f.write(response)

    try:
        output_file = f"{file_path}.so"
        compile_code(file_path, dest_lang, output_file=output_file)
    except Exception as e:
        return 1, str(e)

    result = subprocess.run(
        [
            '/bin/bash', '-c',
            f"""
            time python {test_file} {output_file} {dest_lang}
            """
        ],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode:
        return result.returncode, result.stderr

    return 0, file_path


IMPORTANT_REQUIREMENTS = {
    "Rust": """
    a. Every Rust function definition must be prepended with the following attribute:
        #[unsafe(no_mangle)]
    b. Every Rust function must also be declared as:
        pub extern "C"
    """,
    "Java": """
    a. Java code assume that class name is going to be equal to file name in UpperCamelCase
    b. Java code assume that method name is going to be equal to function name in lowerCamelCase
    c. Java code assume that it will be in package com.<file name>
    d. Java code assume that it will have public static void main(String[] args) {}
    e. Java code assume that all methods in Java class will be with modificators "public static"
    """,

}


def get_translation_gen_stage(meta_file, dst_file, test_file, source_lang="C", dest_lang="Rust"):
    with open(meta_file, 'r') as f:
        ast = f.read()

    initial_query = f"""
    You are tasked with generating {dest_lang} code from a {source_lang} Abstract Syntax Tree (AST). The generated {dest_lang} code will be compiled as a shared object (.so) file, which requires specific considerations. Follow these instructions carefully:

    1. You will be provided with an AST representing {source_lang} code. The AST will be enclosed in XML tags like this:

    <AST>
    {json.dumps(json.loads(ast))} 
    </AST>

    2. Your goal is to generate equivalent {dest_lang} code based on this AST. Pay close attention to the structure and semantics of the {source_lang} code represented by the AST.

    3. Important requirements for the {dest_lang} code:
    {IMPORTANT_REQUIREMENTS[dest_lang]}
    These requirements ensure that the {dest_lang} functions can be called from {source_lang} code and that the resulting .so file can be properly linked.

    4. Process the AST and generate {dest_lang} code following these guidelines:
    a. Translate each {source_lang} function into a {dest_lang} function
    b. Convert {source_lang} types to their {dest_lang} equivalents
    c. Implement the logic of each function in {dest_lang}, maintaining the same behavior as the {source_lang} code
    d. Ensure that all necessary {dest_lang} modules or crates are imported
    e. Handle any {source_lang}-specific constructs or idioms appropriately in {dest_lang}

    5. After generating the {dest_lang} code, DO NOT INCLUDE ANY EXPLANATIONS in your response.

    6. If you encounter any constructs in the AST that don't have a direct equivalent in {dest_lang} or require special handling, explain your approach in comments within the {dest_lang} code.

    7. Ensure that the generated {dest_lang} code adheres to {dest_lang} best practices and idioms while maintaining the functionality of the original {source_lang} code.

    8. If there are any parts of the AST that you're unsure about or that require additional context, include a comment in the {dest_lang} code explaining the issue and your best interpretation.

    Remember, the primary goal is to create {dest_lang} code that can be compiled into a .so file and used as a shared library, maintaining the same interface and functionality as the original {source_lang} code.

    Please provide the generated {dest_lang} code based on the given AST, ensuring it meets all the specified requirements.
    """
    
    stage = Iteration(
        initial_query=initial_query,
        validation_callback=partial(
            test_validation_callback,
            file_path=dst_file,
            test_file=test_file,
            dest_lang=dest_lang
        )
    )

    return stage
