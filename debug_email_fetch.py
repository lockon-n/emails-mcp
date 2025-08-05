#!/usr/bin/env python3
"""
Debug email content fetching issue
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

def debug_email_fetch():
    config = EmailConfig(
        email="kindtree001@mcp.com",
        password="pass001",
        imap_server="localhost",
        imap_port=1143,
        smtp_server="localhost",
        smtp_port=1587,
        use_ssl=False
    )
    
    backend = IMAPBackend(config) 
    backend.connect()
    backend.select_folder("INBOX")
    
    email_id = "6"
    
    print("=== Testing RFC822 fetch ===")
    status, content_data = backend.connection.fetch(email_id, '(RFC822)')
    print(f"Status: {status}")
    print(f"Content data type: {type(content_data)}")
    print(f"Content data length: {len(content_data)}")
    
    for i, item in enumerate(content_data):
        print(f"Item {i}: type={type(item)}")
        if isinstance(item, tuple):
            print(f"  Tuple length: {len(item)}")
            print(f"  Item[0] type: {type(item[0])}")
            print(f"  Item[1] type: {type(item[1])}")
            if isinstance(item[1], bytes):
                print(f"  Item[1] first 100 bytes: {item[1][:100]}")
            else:
                print(f"  Item[1] value: {item[1]}")
    
    # Test the extraction logic
    raw_email = None
    if content_data and isinstance(content_data[0], tuple):
        raw_email = content_data[0][1]
        print(f"\nExtracted raw_email type: {type(raw_email)}")
        if raw_email:
            print(f"Raw email exists: True, length: {len(raw_email)}")
        else:
            print("Raw email is None!")
    
    backend.disconnect()

if __name__ == "__main__":
    debug_email_fetch()