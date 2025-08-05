import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.utils import (
    validate_email_address, validate_email_list, validate_page_params,
    decode_email_header, ValidationError
)

def test_validators():
    """Test validation utilities"""
    print("Testing validators...")
    
    # Test email validation
    assert validate_email_address("test@example.com") == True
    assert validate_email_address("invalid-email") == False
    assert validate_email_address("") == False
    print("✓ Email address validation works")
    
    # Test email list validation
    valid, _ = validate_email_list("test1@example.com,test2@example.com")
    assert valid == True
    
    valid, error = validate_email_list("test@example.com,invalid-email")
    assert valid == False
    assert "invalid-email" in error
    print("✓ Email list validation works")
    
    # Test page params validation
    page, size, warning = validate_page_params(0, 100)
    assert page == 1
    assert size == 50  # max limit
    assert "adjusted" in warning
    print("✓ Page parameter validation works")


def test_email_parser():
    """Test email parsing utilities"""
    print("Testing email parser...")
    
    # Test header decoding
    result = decode_email_header("Test Subject")
    assert result == "Test Subject"
    
    result = decode_email_header(None)
    assert result == ""
    print("✓ Header decoding works")


def test_exceptions():
    """Test custom exceptions"""
    print("Testing exceptions...")
    
    try:
        raise ValidationError("Test validation error")
    except ValidationError as e:
        assert str(e) == "Test validation error"
    
    print("✓ Custom exceptions work")


if __name__ == "__main__":
    test_validators()
    test_email_parser()
    test_exceptions()
    print("All utils tests passed!")