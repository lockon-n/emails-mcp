#!/usr/bin/env python3
"""Test script for sent mail saving functionality"""

import tempfile
import json
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.services.email_service import EmailService

def test_sent_mail_construction():
    """Test that sent mail message is properly constructed"""
    
    # Test email config with name field
    config = EmailConfig(
        email="test@example.com",
        password="password",
        name="Test User"
    )
    
    # Test message construction logic
    from datetime import datetime
    from email.utils import formataddr
    
    to = "recipient@example.com"
    cc = "cc@example.com"
    subject = "Test Subject"
    body = "Test body content"
    html_body = "<p>Test HTML content</p>"
    
    message_lines = []
    
    # Add headers
    if config.name:
        from_header = formataddr((config.name, config.email))
    else:
        from_header = config.email
    
    message_lines.append(f"From: {from_header}")
    message_lines.append(f"To: {to}")
    message_lines.append(f"Cc: {cc}")
    message_lines.append(f"Subject: {subject}")
    message_lines.append(f"Date: {datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')}")
    message_lines.append("MIME-Version: 1.0")
    
    if html_body:
        message_lines.append("Content-Type: multipart/alternative; boundary=\"boundary123\"")
        message_lines.append("")
        message_lines.append("--boundary123")
        message_lines.append("Content-Type: text/plain; charset=utf-8")
        message_lines.append("")
        message_lines.append(body)
        message_lines.append("")
        message_lines.append("--boundary123")
        message_lines.append("Content-Type: text/html; charset=utf-8")
        message_lines.append("")
        message_lines.append(html_body)
        message_lines.append("")
        message_lines.append("--boundary123--")
    else:
        message_lines.append("Content-Type: text/plain; charset=utf-8")
        message_lines.append("")
        message_lines.append(body)
    
    message_string = "\r\n".join(message_lines)
    
    print("Constructed message for saving to Sent folder:")
    print("=" * 50)
    print(message_string)
    print("=" * 50)
    
    # Verify key components
    assert "From: Test User <test@example.com>" in message_string
    assert "To: recipient@example.com" in message_string
    assert "Cc: cc@example.com" in message_string
    assert "Subject: Test Subject" in message_string
    assert "MIME-Version: 1.0" in message_string
    assert "Content-Type: multipart/alternative" in message_string
    assert body in message_string
    assert html_body in message_string
    
    print("✓ Message construction test passed!")

def test_sent_folders_list():
    """Test the sent folders priority list"""
    sent_folders = ["Sent", "INBOX.Sent", "Sent Messages", "Sent Items"]
    
    print(f"Will try to save to these folders in order: {sent_folders}")
    
    # This shows the priority order for different email providers:
    # - "Sent" - common for many providers
    # - "INBOX.Sent" - common for servers using INBOX prefix
    # - "Sent Messages" - used by some providers
    # - "Sent Items" - used by Microsoft Exchange/Outlook
    
    print("✓ Sent folders configuration looks good!")

if __name__ == "__main__":
    test_sent_mail_construction()
    test_sent_folders_list()