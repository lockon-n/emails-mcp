#!/usr/bin/env python3
"""
Test email marking functionality (read/unread/important)
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.email_service import EmailService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_email_marking():
    """Test email marking functionality"""
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
        email_service = EmailService(config)
        backend = IMAPBackend(config)
        
        print("=== Testing Email Marking Functionality ===")
        
        # Step 1: Get a list of emails
        result = email_service.get_emails("INBOX", page=1, page_size=3)
        if not result.emails:
            print("No emails found in INBOX")
            return
        
        print(f"Found {len(result.emails)} emails to test with:")
        for i, email in enumerate(result.emails):
            print(f"  {i+1}. ID: {email.email_id}, Subject: {email.subject[:50]}...")
            print(f"      is_read: {email.is_read}, is_important: {email.is_important}")
        
        # Step 2: Test reading an email (should auto-mark as read)
        test_email_id = result.emails[0].email_id
        print(f"\n=== Step 2: Testing read_email() auto-marking ===")
        print(f"Reading email ID: {test_email_id}")
        
        # Read the email
        email_obj = email_service.read_email(test_email_id)
        print(f"After reading - is_read: {email_obj.is_read}")
        
        # Verify by fetching again
        email_obj_verify = backend.fetch_email(test_email_id)
        print(f"Verification fetch - is_read: {email_obj_verify.is_read}")
        
        # Step 3: Test manual marking as unread
        print(f"\n=== Step 3: Testing mark as unread ===")
        success_count = email_service.mark_emails([test_email_id], "unread")
        print(f"Mark unread result: {success_count}/1 emails marked")
        
        # Verify
        email_obj_after_unread = backend.fetch_email(test_email_id)
        print(f"After marking unread - is_read: {email_obj_after_unread.is_read}")
        
        # Step 4: Test manual marking as read
        print(f"\n=== Step 4: Testing mark as read ===")
        success_count = email_service.mark_emails([test_email_id], "read")
        print(f"Mark read result: {success_count}/1 emails marked")
        
        # Verify
        email_obj_after_read = backend.fetch_email(test_email_id)
        print(f"After marking read - is_read: {email_obj_after_read.is_read}")
        
        # Step 5: Test marking as important (should show the limitation)
        print(f"\n=== Step 5: Testing mark as important ===")
        success_count = email_service.mark_emails([test_email_id], "important")
        print(f"Mark important result: {success_count}/1 emails marked")
        
        # Step 6: Test direct IMAP flag checking
        print(f"\n=== Step 6: Direct IMAP flag checking ===")
        backend.connect()
        backend.select_folder("INBOX")
        
        # Fetch flags for the test email
        status, flag_data = backend.connection.fetch(test_email_id, '(FLAGS)')
        if status == 'OK':
            print(f"IMAP flags for email {test_email_id}: {flag_data}")
        else:
            print(f"Failed to fetch flags: {status}")
        
        # Step 7: Test different IMAP flags
        print(f"\n=== Step 7: Testing IMAP flag operations ===")
        
        # Test setting custom important flag
        try:
            result = backend.connection.store(test_email_id, '+FLAGS', '\\Flagged')
            print(f"Set \\Flagged flag result: {result}")
            
            # Check flags again
            status, flag_data = backend.connection.fetch(test_email_id, '(FLAGS)')
            if status == 'OK':
                print(f"Flags after setting \\Flagged: {flag_data}")
        except Exception as e:
            print(f"Error testing \\Flagged flag: {e}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Test error: {str(e)}")

if __name__ == "__main__":
    test_email_marking()