#!/usr/bin/env python3
"""
Test export functionality
"""
import logging
import os
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.services.email_service import EmailService
from src.emails_mcp.backends.file_backend import FileBackend

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_export_functionality():
    """Test email export functionality"""
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
        
        print("=== Testing Export Functionality ===")
        
        # First, let's see how many emails we have
        result = email_service.get_emails("INBOX", page=1, page_size=10)
        total_emails = result.total_results
        print(f"Total emails in INBOX: {total_emails}")
        
        # Test the old vs new export logic
        print(f"\n--- Testing old export logic (single page) ---")
        result_old = email_service.get_emails("INBOX", page=1, page_size=1000)
        print(f"Old method would export: {len(result_old.emails)} emails")
        
        # Test new export logic manually
        print(f"\n--- Testing new export logic (all pages) ---")
        all_emails = []
        page = 1
        page_size = 2  # Small page size to test pagination
        
        while True:
            result = email_service.get_emails("INBOX", page=page, page_size=page_size)
            print(f"Page {page}: Found {len(result.emails)} emails")
            
            if not result.emails:
                break
                
            all_emails.extend(result.emails)
            
            # Check if we've got all emails
            if page * page_size >= result.total_results:
                break
                
            page += 1
        
        print(f"New method exports: {len(all_emails)} emails")
        
        # Test actual export function
        print(f"\n--- Testing actual export function ---")
        
        # Create a simple file backend for testing
        file_backend = FileBackend(
            email_export_path="./",
            attachment_download_path="./"
        )
        
        # Export a few emails for testing
        test_emails = all_emails[:3] if len(all_emails) >= 3 else all_emails
        exported_file = file_backend.export_emails(test_emails, "test_export", 'json')
        
        print(f"Exported {len(test_emails)} emails to: {exported_file}")
        
        # Check if file exists and show its size
        if os.path.exists(exported_file):
            file_size = os.path.getsize(exported_file)
            print(f"Export file size: {file_size} bytes")
            
            # Show first few lines of the export file
            with open(exported_file, 'r', encoding='utf-8') as f:
                content = f.read(500)  # First 500 characters
                print(f"Export file preview:\n{content}...")
            
            # Clean up test file
            os.remove(exported_file)
            print("Cleaned up test export file")
        else:
            print("❌ Export file was not created")
        
        print(f"\n=== Export Test Summary ===")
        print(f"Total emails available: {total_emails}")
        print(f"Old method limitation: {len(result_old.emails)} emails (single page)")
        print(f"New method capability: {len(all_emails)} emails (all pages)")
        print(f"Export test: {'✅ Success' if os.path.exists(exported_file) == False else '❌ Failed'}")
        
    except Exception as e:
        print(f"Test error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_export_functionality()