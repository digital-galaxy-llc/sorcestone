import os
import subprocess

from sorcestone.utils.logger import logger


def generate_ast(file_path, language, output_file=None, cpp_args="", skip=False):
    """
    Generate AST using the parse.sh script from language specific folder.

    Args:
        file_path (str): Path to the source file
        language (str): Source language name (e.g., 'C', 'Java')
        output_file (str, optional): Path for the output AST file. If not provided,
            will use source_file_path + '.ast'
        cpp_args (str, optional): Additional arguments to pass to the parser. Defaults to "".
        skip (bool, optional): Skip AST generation if True. Defaults to False.

    Returns:
        subprocess.CompletedProcess: Parse result
    
    Raises:
        FileNotFoundError: If parse.sh is not found for the language
        Exception: If parsing fails
    """
    if skip:
        return None

    # Get language-specific parse.sh path
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    parse_script = os.path.join(PROJECT_ROOT, f'../language_tools/{language}/parse.sh')
    
    if not os.path.exists(parse_script):
        raise FileNotFoundError(f"Parse script not found for language {language}")

    # Generate output file path if not provided
    if output_file is None:
        output_file = f"{os.path.splitext(file_path)[0]}.ast"

    # Run parsing
    result = subprocess.run(
        ['/bin/bash', parse_script, file_path, output_file, cpp_args],
        capture_output=True,
        text=True,
        check=False
    )

    logger.info(f"{language} parse output: {result.stdout}")
    if result.stderr:
        logger.error(f"{language} parse errors: {result.stderr}")

    if result.returncode != 0:
        raise Exception(f"{language} code parsing failed")

    return result