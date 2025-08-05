#!/usr/bin/env python3
"""
Simple flag test
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

def simple_flag_test():
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
    
    # Check initial flags
    print("=== Initial state ===")
    status, data = backend.connection.fetch(email_id, '(FLAGS)')
    print(f"Raw response: {data}")
    
    # Mark as read
    print("\n=== Mark as read ===")
    result = backend.connection.store(email_id, '+FLAGS', '\\Seen')
    print(f"Store result: {result}")
    
    status, data = backend.connection.fetch(email_id, '(FLAGS)')
    print(f"After read: {data}")
    
    # Mark as unread  
    print("\n=== Mark as unread ===")
    result = backend.connection.store(email_id, '-FLAGS', '\\Seen')
    print(f"Store result: {result}")
    
    status, data = backend.connection.fetch(email_id, '(FLAGS)')
    print(f"After unread: {data}")
    
    backend.disconnect()

if __name__ == "__main__":
    simple_flag_test()