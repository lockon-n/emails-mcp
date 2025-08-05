#!/usr/bin/env python3
"""
Debug unread marking specifically
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

def test_unread_marking():
    """Test the unread marking issue"""
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
        
        print(f"Testing unread marking on email {email_id}")
        
        # First, mark as read to ensure we start from a known state
        print("\n1. Mark as read first...")
        success = backend.mark_as_read(email_id)
        print(f"Mark as read result: {success}")
        
        # Fetch and check state
        email = backend.fetch_email(email_id)
        print(f"After mark as read: Read={email.is_read}")
        
        # Now mark as unread
        print("\n2. Mark as unread...")
        success = backend.mark_as_unread(email_id)
        print(f"Mark as unread result: {success}")
        
        # Fetch and check state immediately
        email = backend.fetch_email(email_id)
        print(f"After mark as unread: Read={email.is_read}")
        
        # Double-check by fetching flags directly
        print("\n3. Direct flag check...")
        status, msg_data = backend.connection.fetch(email_id, '(FLAGS)')
        for item in msg_data:
            if isinstance(item, tuple) and len(item) == 2:
                header = item[0].decode() if isinstance(item[0], bytes) else str(item[0])
                if 'FLAGS' in header:
                    import re
                    flag_match = re.search(r'FLAGS \(([^)]*)\)', header)
                    if flag_match:
                        flags_str = flag_match.group(1)
                        flags = flags_str.split()
                        print(f"Direct flags check: {flags}")
                        print(f"Contains \\Seen: {'\\Seen' in flags}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unread_marking()