"""
Input validation and sanitization utilities.
Prevents injection attacks and ensures data quality.
"""
import re
from typing import Optional
from bleach import clean


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """
    Sanitize input text by removing potentially harmful content.
    
    Args:
        text: The raw input text
        max_length: Maximum allowed text length
        
    Returns:
        Sanitized text string
    """
    if not text:
        return ""
    
    # Remove HTML tags completely
    text = clean(text, tags=[], strip=True)
    
    # Limit length
    text = text[:max_length]
    
    # Remove control characters (except newlines and tabs)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Normalize whitespace (but preserve single newlines)
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
    
    return text.strip()


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, None


def validate_batch_csv(content: bytes, max_size_mb: int = 10, max_rows: int = 500) -> tuple[bool, Optional[str]]:
    """
    Validate CSV file content for batch processing.
    
    Args:
        content: Raw CSV file bytes
        max_size_mb: Maximum file size in megabytes
        max_rows: Maximum number of rows allowed
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check file size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"File too large. Maximum size is {max_size_mb}MB"
    
    try:
        # Decode and check structure
        decoded = content.decode('utf-8')
        lines = decoded.strip().split('\n')
        
        if len(lines) < 2:
            return False, "CSV must have a header row and at least one data row"
        
        if len(lines) > max_rows + 1:  # +1 for header
            return False, f"Too many rows. Maximum is {max_rows} rows"
        
        # Check for 'text' column in header
        header = lines[0].lower()
        if 'text' not in header:
            return False, "CSV must have a 'text' column"
        
        return True, None
        
    except UnicodeDecodeError:
        return False, "File must be UTF-8 encoded"
    except Exception as e:
        return False, f"Invalid CSV format: {str(e)}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove path separators and null bytes
    filename = re.sub(r'[/\\:\x00]', '', filename)
    
    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename or 'unnamed'
