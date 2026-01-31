import os
import sys
import argparse
from telescope import get_client

from sorcestone.utils.logger import logger
from sorcestone.main.compile import compile_code
from sorcestone.main.generate_ast import generate_ast
from sorcestone.main.generate_tests import get_test_gen_stage
from sorcestone.main.generate_code_from_ast import get_translation_gen_stage


def get_language_extensions():
    """
    Get the file extensions for each language.
    
    Returns:
        dict: Mapping of language names to their file extensions
    """
    return {
        'C': ['.h', '.c'],
        'COBOL': ['.cob', '.cbl', '.cpy'],
        'Java': ['.java'],
        'Rust': ['.rs']
    }


def get_language_categories():
    """
    Categorize language folders based on available tools.
    
    Returns:
        tuple: (source_languages, destination_languages)
        - source_languages: list of folders with both parse.sh and compile.sh
        - destination_languages: list of folders with compile.sh only
    """
    language_tools_path = os.path.join(os.path.dirname(__file__), "language_tools")
    source_languages = []
    destination_languages = []
    
    # List all directories in language_tools
    for folder in os.listdir(language_tools_path):
        folder_path = os.path.join(language_tools_path, folder)
        if not os.path.isdir(folder_path):
            continue
            
        has_compile = os.path.exists(os.path.join(folder_path, "compile.sh"))
        has_parse = os.path.exists(os.path.join(folder_path, "parse.sh"))
        
        if has_compile and has_parse:
            source_languages.append(folder)
        elif has_compile:
            destination_languages.append(folder)
    
    return source_languages, destination_languages


def get_ai_client():
    return get_client(
        vendor='anthropic', model='claude-3-5-sonnet-latest'
        # vendor='anthropic', model='claude-3-7-sonnet-latest'
        # vendor='google', model='gemini-2.0-flash
        # vendor='google', model='gemini-2.5-pro-exp-03-25
        )


def process_file(file_path, from_language, to_language, cpp_args=None):
    """
    Process a single file to generate its meta model

    Args:
        file_path (str): Path to the file to process
    """
    # Check_List makes us able to mark specific stages as accomplished during the previous run
    check_list = {
        "generate_ast": False,
        "compile": False,
        "generate_tests": False,
        "generate_dst_code": False
    }
    check_list.update({
        # "generate_ast": True,
        # "compile": True,
        # "generate_tests": True,
    })

    # Generate AST first
    logger.info(f"Generating {from_language} AST")
    ast_file_path = f"{os.path.splitext(file_path)[0]}.ast"
    _ = generate_ast(
        file_path=file_path,
        language=from_language,
        output_file=ast_file_path,
        cpp_args=cpp_args,
        skip=check_list['generate_ast']
    )

    # Then compile the code
    logger.info(f"Compiling {from_language} code")
    src_so_file_path = f"{file_path}.so"
    _ = compile_code(
        file_path=file_path,
        language=from_language,
        output_file=src_so_file_path,
        skip=check_list['compile']
    )
    
    client = get_ai_client()
    
    # Then Generate functional tests
    logger.info(f"Generate and run tests for {from_language}->{to_language} translation")
    tests_generation_stage = get_test_gen_stage(
        meta_file=ast_file_path,
        code_file=src_so_file_path,
        src_language=from_language,
        dst_language=to_language,
        skip=check_list['generate_tests']
    )
    test_file_path = tests_generation_stage.run(llm_client=client)

    # Then Generate code in destinatio language and verify with tests
    logger.info(f"Generate {to_language} code and verify with tests")
    language_extensions = get_language_extensions()
    generated_code_path =  f"{os.path.splitext(file_path)[0]}{language_extensions[to_language][0]}"
    dst_generation_stage = get_translation_gen_stage(meta_file=ast_file_path, dst_file=generated_code_path, test_file=test_file_path,
                                                     source_lang=from_language, dest_lang=to_language)
    _ = dst_generation_stage.run(llm_client=client)
    return generated_code_path


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    # Get available languages before setting up arguments
    source_languages, destination_languages = get_language_categories()
    
    parser = argparse.ArgumentParser(
        prog="sourcestone",
        description="Sorcerer's Stone: multi language translation framework"
    )
    parser.add_argument(
        'file_path',
        type=str,
        help='Path to the source file to be translated (mandatory)'
    )

    parser.add_argument(
        'src_language',
        type=str,
        choices=source_languages,
        help=f'Language to translate from. Available options: {", ".join(source_languages)}'
    )

    parser.add_argument(
        'dst_language',
        type=str,
        choices=destination_languages,
        help=f'Language to translate to. Available options: {", ".join(destination_languages)}'
    )

    parser.add_argument(
        '--build_args',
        type=str,
        default="",
        help="build args to be provided during the meta model generation. Space separated list of flags expected"
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
            
        # Check if file extension matches source language
        file_ext = os.path.splitext(args.file_path)[1].lower()
        language_extensions = get_language_extensions()
        valid_extensions = [ext.lower() for ext in language_extensions.get(args.src_language, [])]
        
        if not valid_extensions:
            logger.error(f"No known file extensions for language '{args.src_language}'")
            sys.exit(1)
            
        if file_ext not in valid_extensions:
            logger.error(f"File extension '{file_ext}' is not valid for {args.src_language}. Expected: {', '.join(valid_extensions)}")
            sys.exit(1)
            
        # Log the processing of the file
        logger.info(f"========Processing {args.file_path}  ===========")
        
        # Process the file
        rust_file = process_file(
            file_path=os.path.abspath(args.file_path), 
            from_language=args.src_language,
            to_language=args.dst_language,
            cpp_args=args.build_args)

        # Log completion
        logger.info(f"========Done processing {args.file_path}  ===========")

        # Return the path of the generated Rust file
        return rust_file

    except Exception as e:
        logger.error(f"Error processing file {args.file_path}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
