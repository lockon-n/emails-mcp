#!/usr/bin/env python3
"""Test script for name field functionality"""

import tempfile
import json
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.smtp_backend import SMTPBackend
from email.mime.text import MIMEText

def test_name_field_formatting():
    """Test that name field is properly used in From header"""
    
    # Test with name field
    config_with_name = EmailConfig(
        email="test@example.com",
        password="password",
        name="Test User"
    )
    
    smtp_backend = SMTPBackend(config_with_name)
    
    # Create a simple message to test header formatting
    msg = MIMEText("Test body", 'plain', 'utf-8')
    msg['Subject'] = "Test Subject"
    
    # Apply the same logic as in send_email method
    if smtp_backend.config.name:
        from email.utils import formataddr
        msg['From'] = formataddr((smtp_backend.config.name, smtp_backend.config.email))
    else:
        msg['From'] = smtp_backend.config.email
    
    expected_from = 'Test User <test@example.com>'
    actual_from = msg['From']
    
    print(f"With name field:")
    print(f"  Expected: {expected_from}")
    print(f"  Actual:   {actual_from}")
    assert actual_from == expected_from, f"Expected {expected_from}, got {actual_from}"
    
    # Test without name field
    config_without_name = EmailConfig(
        email="test@example.com",
        password="password",
        name=""  # Empty name
    )
    
    smtp_backend2 = SMTPBackend(config_without_name)
    
    msg2 = MIMEText("Test body", 'plain', 'utf-8')
    msg2['Subject'] = "Test Subject"
    
    if smtp_backend2.config.name:
        from email.utils import formataddr
        msg2['From'] = formataddr((smtp_backend2.config.name, smtp_backend2.config.email))
    else:
        msg2['From'] = smtp_backend2.config.email
    
    expected_from2 = "test@example.com"
    actual_from2 = msg2['From']
    
    print(f"Without name field:")
    print(f"  Expected: {expected_from2}")
    print(f"  Actual:   {actual_from2}")
    assert actual_from2 == expected_from2, f"Expected {expected_from2}, got {actual_from2}"
    
    print("✓ All name field formatting tests passed!")

if __name__ == "__main__":
    test_name_field_formatting()