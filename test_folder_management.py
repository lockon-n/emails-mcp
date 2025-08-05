#!/usr/bin/env python3
"""
Test folder management functionality - create, list, delete
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.folder_service import FolderService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_folder_management():
    """Test folder creation, listing, and deletion"""
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
        folder_service = FolderService(backend)
        
        # Step 1: List existing folders
        print("=== Step 1: Initial folder list ===")
        initial_folders = folder_service.get_folders()
        print(f"Found {len(initial_folders)} folders:")
        for folder in initial_folders:
            print(f"  - {folder.name} (selectable: {folder.can_select})")
        
        # Step 2: Create a test folder
        test_folder_name = "TestFolder123"
        print(f"\n=== Step 2: Creating folder '{test_folder_name}' ===")
        
        try:
            success = folder_service.create_folder(test_folder_name)
            print(f"Folder creation result: {success}")
        except Exception as e:
            print(f"Folder creation error: {e}")
        
        # Step 3: List folders again to see if new folder appears
        print(f"\n=== Step 3: Folder list after creation ===")
        updated_folders = folder_service.get_folders()
        print(f"Found {len(updated_folders)} folders:")
        for folder in updated_folders:
            print(f"  - {folder.name} (selectable: {folder.can_select})")
            if test_folder_name in folder.name:
                print(f"    ✅ Found our test folder!")
        
        # Check if folder count increased
        if len(updated_folders) > len(initial_folders):
            print(f"✅ Folder count increased from {len(initial_folders)} to {len(updated_folders)}")
        else:
            print(f"❌ Folder count did not increase (still {len(updated_folders)})")
        
        # Step 4: Test direct IMAP LIST command
        print(f"\n=== Step 4: Direct IMAP LIST command ===")
        backend.connect()
        status, raw_folders = backend.connection.list()
        
        if status == 'OK':
            print(f"Raw IMAP LIST returned {len(raw_folders)} items:")
            for i, folder in enumerate(raw_folders):
                folder_info = folder.decode('utf-8')
                print(f"  {i+1}. {folder_info}")
                if test_folder_name in folder_info:
                    print(f"    ✅ Test folder found in raw IMAP response!")
        else:
            print(f"IMAP LIST failed: {status}")
        
        # Step 5: Test different folder name patterns
        print(f"\n=== Step 5: Testing different folder name patterns ===")
        possible_names = [
            test_folder_name,
            f"INBOX.{test_folder_name}",
            f"INBOX/{test_folder_name}",
        ]
        
        for name in possible_names:
            try:
                total, unread = backend.select_folder(name)
                print(f"✅ Can select folder '{name}': {total} total, {unread} unread")
            except Exception as e:
                print(f"❌ Cannot select folder '{name}': {e}")
        
        # Step 6: Clean up - try to delete the test folder
        print(f"\n=== Step 6: Cleaning up test folder ===")
        
        # Try to delete with different names
        for name in possible_names:
            try:
                print(f"Trying to delete: {name}")
                status, data = backend.connection.delete(name)
                if status == 'OK':
                    print(f"✅ Successfully deleted folder: {name}")
                    break
                else:
                    print(f"❌ Failed to delete '{name}': {status} {data}")
            except Exception as e:
                print(f"❌ Exception deleting '{name}': {e}")
        
        backend.disconnect()
        
        # Step 7: Final folder list
        print(f"\n=== Step 7: Final folder list ===")
        final_folders = folder_service.get_folders()
        print(f"Found {len(final_folders)} folders:")
        for folder in final_folders:
            print(f"  - {folder.name} (selectable: {folder.can_select})")
        
    except Exception as e:
        print(f"Test error: {str(e)}")

if __name__ == "__main__":
    test_folder_management()