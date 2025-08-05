#!/usr/bin/env python3
"""
Complete email marking test with debugging
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.email_service import EmailService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_complete_marking():
    """Test complete email marking functionality"""
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
        backend.connect()
        backend.select_folder("INBOX")
        
        # Get test emails
        result = email_service.get_emails("INBOX", page=1, page_size=2)
        if not result.emails:
            print("❌ No emails found")
            return
            
        test_email_ids = [email.email_id for email in result.emails]
        print(f"Testing with emails: {test_email_ids}")
        
        # Test individual operations step by step
        email_id = test_email_ids[0]
        print(f"\n--- Testing email {email_id} ---")
        
        # Step 1: Get initial state
        try:
            email = backend.fetch_email(email_id)
            print(f"Initial: Read={email.is_read}, Important={email.is_important}")
        except Exception as e:
            print(f"❌ Initial fetch failed: {e}")
            return
        
        # Step 2: Mark as read
        success = backend.mark_as_read(email_id)
        print(f"Mark as read: {'✅' if success else '❌'}")
        
        try:
            email = backend.fetch_email(email_id)
            print(f"After read: Read={email.is_read}, Important={email.is_important}")
        except Exception as e:
            print(f"❌ Fetch after read failed: {e}")
            return
        
        # Step 3: Mark as unread
        success = backend.mark_as_unread(email_id)
        print(f"Mark as unread: {'✅' if success else '❌'}")
        
        try:
            email = backend.fetch_email(email_id)
            print(f"After unread: Read={email.is_read}, Important={email.is_important}")
        except Exception as e:
            print(f"❌ Fetch after unread failed: {e}")
            return
        
        # Step 4: Mark as important
        success = backend.mark_as_important(email_id)
        print(f"Mark as important: {'✅' if success else '❌'}")
        
        try:
            email = backend.fetch_email(email_id)
            print(f"After important: Read={email.is_read}, Important={email.is_important}")
        except Exception as e:
            print(f"❌ Fetch after important failed: {e}")
            return
        
        # Step 5: Test batch operations if individual operations work
        print(f"\n--- Testing batch operations on {len(test_email_ids)} emails ---")
        
        # Batch mark as unread
        success_count = email_service.mark_emails(test_email_ids, "unread")
        print(f"Batch unread: {success_count}/{len(test_email_ids)}")
        
        # Verify batch result
        print("Verifying batch unread:")
        for i, eid in enumerate(test_email_ids):
            try:
                email = backend.fetch_email(eid)
                print(f"  Email {i+1}: Read={email.is_read}")
            except Exception as e:
                print(f"  Email {i+1}: ❌ Fetch failed: {e}")
        
        # Batch mark as important
        success_count = email_service.mark_emails(test_email_ids, "important")
        print(f"Batch important: {success_count}/{len(test_email_ids)}")
        
        # Verify batch result
        print("Verifying batch important:")
        for i, eid in enumerate(test_email_ids):
            try:
                email = backend.fetch_email(eid)
                print(f"  Email {i+1}: Important={email.is_important}")
            except Exception as e:
                print(f"  Email {i+1}: ❌ Fetch failed: {e}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Test error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_marking()