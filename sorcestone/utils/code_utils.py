def extract_code(text: str, language: str) -> str:
    """
    Extract code from a text that may contain markdown-style code blocks.
    
    Args:
        text (str): Input text potentially containing code block
        language (str): Input language name
    
    Returns:
        str: Extracted code, or the original text if no code block is found
    """
    # Remove leading and trailing whitespace
    text = text.strip()
    prefix = f'```{language}'
    suffix = '```'
    # Check if text starts with ```<language> and remove it
    if text.startswith(prefix):
        text = text[len(prefix):].strip()
    
    # Check if ends with ``` and remove it
    if text.endswith(suffix):
        text = text[:-len(suffix)].strip()
    
    # If no code block markers found, return original text
    return text
