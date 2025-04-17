import os
import sys
import argparse
from telescope import get_client

from logger import logger
from parse import c_to_meta
from compile import compile_c_code
from generate_tests import get_test_gen_stage
from generate_rust import get_rust_gen_stage


def process_file(file_path):
    """
    Process a single file to generate its meta model
    
    Args:
        file_path (str): Path to the file to process
    """
    # Check_List makes us able to mark specific stages as accomplished during the previous run
    check_list = {
        "c_to_meta": False,
        "compile_c": False,
        "generate_tests": False,
        "generate_rust_code": False
    }
    
    logger.info("Building C code")
    c_compile_result = compile_c_code(file_path, skip=check_list['compile_c'])

    logger.info("Generating C code meta model")
    meta_file = c_to_meta(file_name=file_path, skip=check_list['c_to_meta'])
    # client = get_client(vendor='anthropic', model='claude-3-7-sonnet-latest')
    client = get_client(vendor='anthropic', model='claude-3-5-sonnet-latest')
    # client = get_client(vendor='google', model='gemini-2.0-flash')
    # client = get_client(vendor='google', model='gemini-2.5-pro-exp-03-25')
    
    logger.info("Generate and run C meta test")
    tests_generation_stage = get_test_gen_stage(meta_file=meta_file, code_file=file_path, skip=check_list['generate_tests'])
    test_file = tests_generation_stage.run(llm_client=client)

    logger.info("Generate Rust and verify with meta test")
    rust_generation_stage = get_rust_gen_stage(meta_file=meta_file, code_file=file_path, test_file=test_file)
    rust_file = rust_generation_stage.run(llm_client=client)
    return rust_file


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Sorcerer's Stone: C to Rust Translation Tool"
    )
    parser.add_argument(
        'file_path', 
        type=str, 
        help='Path to the C source file to be translated (mandatory)'
    )
    return parser.parse_args()


def main():
    """
    Main function to process a single file.
    """
    # Parse arguments
    args = parse_arguments()
    
    try:
        # Ensure the file exists
        if not os.path.isfile(args.file_path):
            logger.error(f"File not found: {args.file_path}")
            sys.exit(1)
        
        # Log the processing of the file
        logger.info(f"========Processing {args.file_path}  ===========")
        
        # Process the file
        rust_file = process_file(os.path.abspath(args.file_path))
        
        # Log completion
        logger.info(f"========Done processing {args.file_path}  ===========")
        
        # Return the path of the generated Rust file
        return rust_file
    
    except Exception as e:
        logger.error(f"Error processing file {args.file_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
