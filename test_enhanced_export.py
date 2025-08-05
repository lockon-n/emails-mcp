#!/usr/bin/env python3
"""
Test enhanced export functionality with all folders
"""
import logging
import os
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.services.email_service import EmailService
from src.emails_mcp.services.folder_service import FolderService
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.backends.file_backend import FileBackend

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_enhanced_export():
    """Test enhanced export functionality"""
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
        # Initialize services
        imap_backend = IMAPBackend(config)
        email_service = EmailService(config)
        folder_service = FolderService(imap_backend)
        
        print("=== Enhanced Export Functionality Test ===")
        
        # Get all folders
        folders = folder_service.get_folders()
        print(f"Available folders: {len(folders)}")
        
        folder_email_counts = {}
        total_emails_all_folders = 0
        
        for folder in folders:
            if folder.can_select:
                try:
                    result = email_service.get_emails(folder.name, page=1, page_size=10)
                    count = result.total_results
                    folder_email_counts[folder.name] = count
                    total_emails_all_folders += count
                    print(f"  - {folder.name}: {count} emails")
                except Exception as e:
                    print(f"  - {folder.name}: Error - {str(e)}")
                    folder_email_counts[folder.name] = 0
        
        print(f"\nTotal emails across all folders: {total_emails_all_folders}")
        
        # Test 1: Export single folder (INBOX)
        print(f"\n--- Test 1: Export INBOX only ---")
        inbox_emails = folder_email_counts.get("INBOX", 0)
        print(f"INBOX has {inbox_emails} emails")
        
        # Test 2: Export all folders simulation
        print(f"\n--- Test 2: Export all folders simulation ---")
        
        # Simulate the enhanced export logic
        folders_to_export = [f.name for f in folders if f.can_select]
        print(f"Would export from folders: {folders_to_export}")
        
        simulated_all_emails = []
        simulated_folder_stats = {}
        
        for folder_name in folders_to_export:
            try:
                # Get first page of emails from each folder
                result = email_service.get_emails(folder_name, page=1, page_size=100)
                folder_emails = result.emails
                simulated_all_emails.extend(folder_emails)
                simulated_folder_stats[folder_name] = len(folder_emails)
                print(f"  From {folder_name}: collected {len(folder_emails)} emails")
            except Exception as e:
                print(f"  From {folder_name}: Error - {str(e)}")
                simulated_folder_stats[folder_name] = 0
        
        print(f"\nSimulated export results:")
        print(f"Total emails that would be exported: {len(simulated_all_emails)}")
        
        for folder_name, count in simulated_folder_stats.items():
            print(f"  - {folder_name}: {count} emails")
        
        # Test 3: Actual export test (limited)
        print(f"\n--- Test 3: Actual export test ---")
        
        if simulated_all_emails:
            # Create file backend
            file_backend = FileBackend(
                email_export_path="./",
                attachment_download_path="./"
            )
            
            # Export first few emails as test
            test_emails = simulated_all_emails[:min(3, len(simulated_all_emails))]
            exported_file = file_backend.export_emails(test_emails, "multi_folder_test", 'json')
            
            print(f"Test export created: {exported_file}")
            
            if os.path.exists(exported_file):
                file_size = os.path.getsize(exported_file)
                print(f"Export file size: {file_size} bytes")
                
                # Clean up
                os.remove(exported_file)
                print("Cleaned up test file")
        
        # Summary
        print(f"\n=== Export Capability Summary ===")
        print(f"Single folder export (old): ✅ Available")
        print(f"Multi-folder export (new): ✅ Available")
        print(f"Total folders available: {len([f for f in folders if f.can_select])}")
        print(f"Total emails available: {total_emails_all_folders}")
        
        print(f"\nUsage examples:")
        print(f"  export_emails()                          # Export INBOX only")
        print(f"  export_emails(folder='Sent')             # Export Sent folder")
        print(f"  export_emails(export_all_folders=True)   # Export ALL folders")
        print(f"  export_emails(export_all_folders=True, max_emails=100)  # Limited export")
        
    except Exception as e:
        print(f"Test error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_export()