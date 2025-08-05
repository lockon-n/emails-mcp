#!/usr/bin/env python3
"""
Debug email flag parsing
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

# Set up logging to see debug messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def debug_flag_parsing():
    """Debug how IMAP flags are parsed"""
    config = EmailConfig(
        email="kindtree001@mcp.com",
        password="pass001",
        imap_server="localhost",
        imap_port=1143,
        smtp_server="localhost",
        smtp_port=1587,
        use_ssl=False
    )
    
    try:
        backend = IMAPBackend(config)
        backend.connect()
        backend.select_folder("INBOX")
        
        # Get the first email
        email_ids = backend.get_email_ids("INBOX", limit=1)
        if not email_ids:
            print("No emails found")
            return
            
        email_id = email_ids[0]
        print(f"Testing with email ID: {email_id}")
        
        # Fetch email with flags - debug the raw response
        print("\n=== Raw IMAP FETCH Response ===")
        status, msg_data = backend.connection.fetch(email_id, '(RFC822 FLAGS)')
        print(f"Status: {status}")
        print(f"Data length: {len(msg_data)}")
        
        for i, item in enumerate(msg_data):
            print(f"Item {i}: type={type(item)}")
            if isinstance(item, tuple):
                print(f"  Tuple length: {len(item)}")
                for j, sub_item in enumerate(item):
                    print(f"    Sub-item {j}: type={type(sub_item)}")
                    if isinstance(sub_item, bytes):
                        decoded = sub_item.decode('utf-8', errors='ignore')[:100]
                        print(f"      Decoded (first 100 chars): {decoded}")
                    else:
                        print(f"      Value: {str(sub_item)[:100]}")
            else:
                print(f"  Value: {str(item)[:100]}")
        
        # Test flag parsing logic
        print(f"\n=== Testing Flag Parsing ===")
        raw_email = None
        flags = None
        
        for item in msg_data:
            if isinstance(item, tuple) and len(item) == 2:
                print(f"Processing tuple: {item[0][:50] if isinstance(item[0], bytes) else str(item[0])[:50]}")
                if isinstance(item[0], bytes) and item[0].startswith(b'FLAGS'):
                    print("  Found FLAGS item!")
                    flags_str = item[1].decode() if isinstance(item[1], bytes) else str(item[1])
                    flags = flags_str.split()
                    print(f"  Flags string: '{flags_str}'")
                    print(f"  Parsed flags: {flags}")
                else:
                    print("  This is email content")
                    raw_email = item[1]
        
        print(f"\nExtracted flags: {flags}")
        if flags:
            print(f"Is read (\\Seen in flags): {'\\Seen' in flags}")
            print(f"Is important (\\Flagged in flags): {'\\Flagged' in flags}")
        
        # Test marking operations
        print(f"\n=== Testing Mark Operations ===")
        
        # Mark as read and check
        print("Marking as read...")
        success = backend.mark_as_read(email_id)
        print(f"Mark as read success: {success}")
        
        # Fetch flags again
        status, msg_data = backend.connection.fetch(email_id, '(FLAGS)')
        print(f"Flags fetch status: {status}")
        
        for item in msg_data:
            if isinstance(item, tuple) and len(item) == 2:
                if isinstance(item[0], bytes) and b'FLAGS' in item[0]:
                    flags_str = item[1].decode() if isinstance(item[1], bytes) else str(item[1])
                    flags = flags_str.split()
                    print(f"New flags after mark as read: {flags}")
                    print(f"Contains \\Seen: {'\\Seen' in flags}")
        
        # Test the full fetch_email method
        print(f"\n=== Testing fetch_email method ===")
        email_obj = backend.fetch_email(email_id)
        print(f"Email object - Read: {email_obj.is_read}, Important: {email_obj.is_important}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Debug error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_flag_parsing()