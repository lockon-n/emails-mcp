#!/usr/bin/env python3
"""
Test email marking and import functionality
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
        
        print("=== Testing Email Marking Functionality ===")
        
        # Get some emails to test with
        result = email_service.get_emails("INBOX", page=1, page_size=3)
        if not result.emails:
            print("❌ No emails found for testing")
            return
            
        print(f"Found {len(result.emails)} emails for testing")
        
        test_email_ids = [email.email_id for email in result.emails]
        
        # Test individual marking functions
        print(f"\n--- Testing individual marking on email {test_email_ids[0]} ---")
        
        backend = IMAPBackend(config)
        backend.connect()
        backend.select_folder("INBOX")
        
        # Get initial email state
        initial_email = backend.fetch_email(test_email_ids[0])
        print(f"Initial state - Read: {initial_email.is_read}, Important: {initial_email.is_important}")
        
        # Test mark as unread
        success = backend.mark_as_unread(test_email_ids[0])
        print(f"Mark as unread: {'✅' if success else '❌'} {success}")
        
        # Check state
        email_after_unread = backend.fetch_email(test_email_ids[0])
        print(f"After unread - Read: {email_after_unread.is_read}, Important: {email_after_unread.is_important}")
        
        # Test mark as read
        success = backend.mark_as_read(test_email_ids[0])
        print(f"Mark as read: {'✅' if success else '❌'} {success}")
        
        # Check state
        email_after_read = backend.fetch_email(test_email_ids[0])
        print(f"After read - Read: {email_after_read.is_read}, Important: {email_after_read.is_important}")
        
        # Test mark as important
        success = backend.mark_as_important(test_email_ids[0])
        print(f"Mark as important: {'✅' if success else '❌'} {success}")
        
        # Check state
        email_after_important = backend.fetch_email(test_email_ids[0])
        print(f"After important - Read: {email_after_important.is_read}, Important: {email_after_important.is_important}")
        
        # Test remove important
        success = backend.mark_as_not_important(test_email_ids[0])
        print(f"Remove important: {'✅' if success else '❌'} {success}")
        
        # Check final state
        email_final = backend.fetch_email(test_email_ids[0])
        print(f"Final state - Read: {email_final.is_read}, Important: {email_final.is_important}")
        
        # Test batch marking
        print(f"\n--- Testing batch marking on {len(test_email_ids)} emails ---")
        
        # Mark all as unread
        success_count = email_service.mark_emails(test_email_ids, "unread")
        print(f"Batch mark as unread: {success_count}/{len(test_email_ids)} emails")
        
        # Mark all as important
        success_count = email_service.mark_emails(test_email_ids, "important")
        print(f"Batch mark as important: {success_count}/{len(test_email_ids)} emails")
        
        # Verify batch changes
        print("\nVerifying batch changes:")
        for i, email_id in enumerate(test_email_ids):
            email = backend.fetch_email(email_id)
            print(f"  Email {i+1}: Read={email.is_read}, Important={email.is_important}")
        
        # Clean up - mark all as read and not important
        email_service.mark_emails(test_email_ids, "read")
        email_service.mark_emails(test_email_ids, "not_important")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Test error: {str(e)}")

def test_batch_functions():
    """Test what batch functions are available"""
    print("=== Available Batch Functions ===")
    
    functions = [
        "mark_emails(email_ids: List[str], status: str) - ✅ Available",
        "move_email(email_id: str, target_folder: str) - ❌ Single only", 
        "delete_email(email_id: str) - ❌ Single only",
    ]
    
    print("Current batch functionality:")
    for func in functions:
        print(f"  {func}")
    print("\n✅ = Batch function available")
    print("❌ = Only single item function available")

if __name__ == "__main__":
    test_batch_functions()
    test_email_marking()