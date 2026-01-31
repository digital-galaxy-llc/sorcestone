import os
import subprocess

from sorcestone.utils.logger import logger


def compile_code(file_path, language, output_file=None, skip=False):
    """
    Compile code using the compile.sh script from language specific folder.

    Args:
        file_path (str): Path to the source file
        language (str): Source language name (e.g., 'C', 'Java')
        output_file (str, optional): Path for the output file. If not provided,
            will use source_file_path + '.so'
        skip (bool, optional): Skip compilation if True. Defaults to False.

    Returns:
        subprocess.CompletedProcess: Compilation result
    
    Raises:
        FileNotFoundError: If compile.sh is not found for the language
        Exception: If compilation fails
    """
    if skip:
        return None

    # Get language-specific compile.sh path
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    compile_script = os.path.join(PROJECT_ROOT, f'../language_tools/{language}/compile.sh')
    
    if not os.path.exists(compile_script):
        raise FileNotFoundError(f"Compile script not found for language {language}")

    # Generate output file path if not provided
    if output_file is None:
        output_file = f"{os.path.splitext(file_path)[0]}.so"

    # Run compilation
    result = subprocess.run(
        ['/bin/bash', compile_script, file_path, output_file],
        capture_output=True,
        text=True,
        check=False
    )

    logger.info(f"{language} compile output: {result.stdout}")
    if result.stderr:
        logger.error(f"{language} compile errors: {result.stderr}")

    if result.returncode != 0:
        raise Exception(f"{language} code compilation failed")

    return result