#!/usr/bin/env python3
"""
Test with forced refresh
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_with_forced_refresh():
    """Test with forced refresh"""
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
        
        email_ids = backend.get_email_ids("INBOX", limit=1)
        email_id = email_ids[0]
        
        print(f"Testing with email {email_id}")
        
        # Mark as read
        print("\n1. Mark as read...")
        backend.mark_as_read(email_id)
        
        # Force NOOP and check
        backend.connection.noop()
        email = backend.fetch_email(email_id)
        print(f"After read: Read={email.is_read}")
        
        # Mark as unread
        print("\n2. Mark as unread...")
        backend.mark_as_unread(email_id)
        
        # Force NOOP and check
        backend.connection.noop()
        email = backend.fetch_email(email_id)
        print(f"After unread: Read={email.is_read}")
        
        # Alternative: use FETCH FLAGS only to avoid caching
        print("\n3. Direct FLAGS only fetch...")
        status, msg_data = backend.connection.fetch(email_id, '(FLAGS)')
        print(f"Status: {status}")
        
        for item in msg_data:
            if isinstance(item, tuple):
                header = item[0].decode() if isinstance(item[0], bytes) else str(item[0])
                print(f"Raw header: {header}")
                
                if 'FLAGS' in header:
                    import re
                    flag_match = re.search(r'FLAGS \(([^)]*)\)', header)
                    if flag_match:
                        flags_str = flag_match.group(1)
                        flags = flags_str.split()
                        print(f"Extracted flags: {flags}")
                        print(f"Is read (\\Seen present): {'\\Seen' in flags}")
        
        # Try marking as unread again and immediate check
        print("\n4. Mark unread + immediate FLAGS check...")
        result = backend.connection.store(email_id, '-FLAGS', '\\Seen')
        print(f"Store result: {result}")
        
        # Immediate flags check
        status, msg_data = backend.connection.fetch(email_id, '(FLAGS)')
        for item in msg_data:
            if isinstance(item, tuple):
                header = item[0].decode() if isinstance(item[0], bytes) else str(item[0])
                if 'FLAGS' in header:
                    import re
                    flag_match = re.search(r'FLAGS \(([^)]*)\)', header)
                    if flag_match:
                        flags_str = flag_match.group(1)
                        flags = flags_str.split()
                        print(f"Immediate check flags: {flags}")
                        print(f"Is read: {'\\Seen' in flags}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_with_forced_refresh()