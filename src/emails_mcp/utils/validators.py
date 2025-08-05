import re
from typing import Optional
from pathlib import Path
from .exceptions import ValidationError


def validate_email_address(email: str) -> bool:
    """Validate email address format"""
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_email_list(email_list: str) -> tuple[bool, str]:
    """Validate comma-separated email list"""
    if not email_list:
        return False, "Email list cannot be empty"
    
    emails = [email.strip() for email in email_list.split(',')]
    invalid_emails = []
    
    for email in emails:
        if not validate_email_address(email):
            invalid_emails.append(email)
    
    if invalid_emails:
        return False, f"Invalid email addresses: {', '.join(invalid_emails)}"
    
    return True, ""


def validate_page_params(page: int, page_size: int, max_page_size: int = 50) -> tuple[int, int, str]:
    """Validate and normalize pagination parameters"""
    warning = ""
    
    if page < 1:
        page = 1
        warning += "Page number adjusted to 1. "
    
    if page_size < 1:
        page_size = 20
        warning += "Page size adjusted to 20. "
    elif page_size > max_page_size:
        page_size = max_page_size
        warning += f"Page size limited to {max_page_size}. "
    
    return page, page_size, warning


def validate_file_path(file_path: str, must_exist: bool = True) -> tuple[bool, str]:
    """Validate file path"""
    if not file_path:
        return False, "File path cannot be empty"
    
    try:
        path = Path(file_path)
        
        if must_exist and not path.exists():
            return False, f"File does not exist: {file_path}"
        
        if must_exist and not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid file path: {str(e)}"


def validate_folder_name(folder_name: str) -> tuple[bool, str]:
    """Validate email folder name"""
    if not folder_name:
        return False, "Folder name cannot be empty"
    
    # Basic validation - no path separators or special chars
    invalid_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in invalid_chars:
        if char in folder_name:
            return False, f"Folder name contains invalid character: {char}"
    
    if len(folder_name) > 255:
        return False, "Folder name too long (max 255 characters)"
    
    return True, ""


def sanitize_subject(subject: str) -> str:
    """Sanitize email subject"""
    if not subject:
        return ""
    
    # Remove control characters and normalize whitespace
    sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', subject)
    sanitized = ' '.join(sanitized.split())
    
    return sanitized[:998]  # RFC limit for subject length


def validate_search_query(query: str) -> tuple[bool, str]:
    """Validate search query"""
    if not query or not query.strip():
        return False, "Search query cannot be empty"
    
    if len(query) > 1000:
        return False, "Search query too long (max 1000 characters)"
    
    return True, ""