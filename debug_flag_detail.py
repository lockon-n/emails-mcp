#!/usr/bin/env python3
"""
Debug flag parsing in detail
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def debug_flag_parsing_detail():
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
    
    # Mark as read first
    print("=== Mark as read ===")
    backend.mark_as_read(email_id)
    
    # Get flags
    status, flag_data = backend.connection.fetch(email_id, '(FLAGS)')
    print(f"Flag data: {flag_data}")
    
    # Test flag parsing logic
    flags = []
    for item in flag_data:
        print(f"Processing item: {item} (type: {type(item)})")
        if isinstance(item, tuple) and len(item) == 2:
            header = item[0].decode() if isinstance(item[0], bytes) else str(item[0])
            print(f"  Header: '{header}'")
            if 'FLAGS' in header:
                print("  Found FLAGS in header!")
                import re
                flag_match = re.search(r'FLAGS \(([^)]*)\)', header)
                if flag_match:
                    flags_str = flag_match.group(1)
                    flags = flags_str.split() if flags_str.strip() else []
                    print(f"  Extracted flags: {flags}")
                    print(f"  Flags string: '{flags_str}'")
                else:
                    print("  No regex match found")
            else:
                print("  No FLAGS in header")
    
    print(f"\nFinal flags: {flags}")
    print(f"Is read: {'\\Seen' in flags}")
    print(f"Is important: {'\\Flagged' in flags}")
    
    # Test with mark as important
    print("\n=== Mark as important ===")
    backend.mark_as_important(email_id)
    
    # Get flags again
    status, flag_data = backend.connection.fetch(email_id, '(FLAGS)')
    print(f"Flag data after important: {flag_data}")
    
    flags = []
    for item in flag_data:
        if isinstance(item, tuple) and len(item) == 2:
            header = item[0].decode() if isinstance(item[0], bytes) else str(item[0])
            if 'FLAGS' in header:
                import re
                flag_match = re.search(r'FLAGS \(([^)]*)\)', header)
                if flag_match:
                    flags_str = flag_match.group(1)
                    flags = flags_str.split() if flags_str.strip() else []
                    print(f"  Flags after important: {flags}")
    
    print(f"Is read: {'\\Seen' in flags}")  
    print(f"Is important: {'\\Flagged' in flags}")
    
    backend.disconnect()

if __name__ == "__main__":
    debug_flag_parsing_detail()