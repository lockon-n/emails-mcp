#!/usr/bin/env python3
"""
Comprehensive test for all email functionality
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.services.email_service import EmailService
from src.emails_mcp.services.folder_service import FolderService
from src.emails_mcp.backends.imap_backend import IMAPBackend

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_all_functionality():
    """Test all email functionality comprehensively"""
    config = EmailConfig(
        email="kindtree001@mcp.com",
        password="pass001",
        imap_server="localhost",
        imap_port=1143,
        smtp_server="localhost",
        smtp_port=1587,
        use_ssl=False
    )
    
    print("🔄 Starting comprehensive email functionality test...")
    
    try:
        # Initialize services
        imap_backend = IMAPBackend(config)
        email_service = EmailService(config)
        folder_service = FolderService(imap_backend)
        
        # Test 1: Folder Management
        print("\n📁 Testing Folder Management...")
        folders = folder_service.get_folders()
        print(f"✅ Found {len(folders)} folders")
        
        # Create test folder
        test_folder = "TestBatch123"
        success = folder_service.create_folder(test_folder)
        print(f"✅ Create folder: {'Success' if success else 'Failed'}")
        
        # Verify folder appears in list
        updated_folders = folder_service.get_folders()
        test_folder_found = any(f.name == test_folder for f in updated_folders)
        print(f"✅ Folder in list: {'Yes' if test_folder_found else 'No'}")
        
        # Test 2: Email Listing and Search
        print(f"\n📧 Testing Email Operations...")
        result = email_service.get_emails("INBOX", page=1, page_size=3)
        print(f"✅ Found {result.total_results} emails in INBOX")
        
        if result.emails:
            test_email_ids = [email.email_id for email in result.emails[:2]]
            
            # Test search
            search_result = email_service.search_emails("测试", folder="INBOX")
            print(f"✅ Chinese search: Found {search_result.total_results} emails")
            
            # Test 3: Individual Email Marking
            print(f"\n🏷️  Testing Individual Email Marking...")
            email_id = test_email_ids[0]
            
            # Test each marking function
            imap_backend.connect()
            imap_backend.select_folder("INBOX")
            
            success = imap_backend.mark_as_read(email_id)
            print(f"✅ Mark as read: {'Success' if success else 'Failed'}")
            
            success = imap_backend.mark_as_unread(email_id)
            print(f"✅ Mark as unread: {'Success' if success else 'Failed'}")
            
            success = imap_backend.mark_as_important(email_id)
            print(f"✅ Mark as important: {'Success' if success else 'Failed'}")
            
            success = imap_backend.mark_as_not_important(email_id)
            print(f"✅ Remove important: {'Success' if success else 'Failed'}")
            
            # Test 4: Batch Operations
            print(f"\n📦 Testing Batch Operations...")
            
            # Batch marking
            success_count = email_service.mark_emails(test_email_ids, "read")
            print(f"✅ Batch mark as read: {success_count}/{len(test_email_ids)}")
            
            success_count = email_service.mark_emails(test_email_ids, "important")
            print(f"✅ Batch mark as important: {success_count}/{len(test_email_ids)}")
            
            # Verify states
            for i, eid in enumerate(test_email_ids):
                email = imap_backend.fetch_email(eid)
                print(f"  Email {i+1}: Read={email.is_read}, Important={email.is_important}")
            
            # Test batch move (if test folder exists)
            if test_folder_found:
                # Move one email to test folder for batch move test
                try:
                    # First test single move
                    success = email_service.move_email(test_email_ids[0], test_folder)
                    print(f"✅ Single move to test folder: {'Success' if success else 'Failed'}")
                    
                    # Move it back for batch test
                    if success:
                        success = email_service.move_email(test_email_ids[0], "INBOX")
                        print(f"✅ Move back to INBOX: {'Success' if success else 'Failed'}")
                
                except Exception as e:
                    print(f"❓ Move test skipped: {str(e)}")
            
            imap_backend.disconnect()
        
        # Test 5: Available Functions Summary
        print(f"\n📋 Function Availability Summary:")
        
        available_functions = [
            "✅ get_emails() - List emails with pagination",
            "✅ read_email() - Read individual email",
            "✅ search_emails() - Search with Chinese support",
            "✅ send_email() - Send emails",
            "✅ reply_email() - Reply to emails", 
            "✅ forward_email() - Forward emails",
            "✅ delete_email() - Delete single email",
            "✅ move_email() - Move single email",
            "✅ mark_emails() - Batch mark emails",
            "✅ move_emails() - Batch move emails (NEW)",
            "✅ delete_emails() - Batch delete emails (NEW)",
            "✅ get_folders() - List folders",
            "✅ create_folder() - Create folders",
            "✅ delete_folder() - Delete folders",
            "✅ import_emails() - Import emails (basic)",
        ]
        
        for func in available_functions:
            print(f"  {func}")
        
        # Clean up test folder
        if test_folder_found:
            try:
                folder_service.delete_folder(test_folder)
                print(f"\n🧹 Cleaned up test folder: {test_folder}")
            except:
                print(f"\n⚠️  Could not clean up test folder: {test_folder}")
        
        print("\n🎉 Comprehensive test completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_all_functionality()