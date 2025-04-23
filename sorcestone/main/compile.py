import os
import subprocess

from sorcestone.utils.logger import logger


def compile_c_code(file_path, skip=False):
    """
    Compile C code using the compile_c.sh script.

    :param file_path: Path to the C file
    :return: Compilation result
    """
    if skip:
        return ""

    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    compile_script = os.path.join(PROJECT_ROOT, 'compile_c.sh')
    result = subprocess.run(
        [
            '/bin/bash', '-c',
            f"""
            cd {PROJECT_ROOT} && \
            source {compile_script} {os.path.splitext(file_path)[0]}
            """
        ], 
        capture_output=True, 
        text=True,
        check=False
    )
    logger.info(f"C Compile time: {result.stderr}")

    if result.returncode:
        raise Exception("C code compilation error")


    return result