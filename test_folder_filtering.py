#!/usr/bin/env python3
"""Test the fixed folder listing"""

def test_folder_filtering():
    """Test that invalid folders are filtered out correctly"""
    
    # Simulate the filtering logic
    test_folders = [
        ('INBOX', True),      # Valid folder
        ('Sent', True),       # Valid folder
        ('.', False),         # Should be filtered out
        ('', False),          # Should be filtered out  
        ('..', False),        # Should be filtered out
        ('Drafts', True),     # Valid folder
        ('Trash', True),      # Valid folder
    ]
    
    print("Testing folder filtering logic:")
    print("=" * 40)
    
    filtered_folders = []
    for folder_name, should_keep in test_folders:
        # Apply the filtering logic
        if not folder_name or folder_name in [".", ".."]:
            keep = False
        else:
            keep = True
        
        print(f"Folder: '{folder_name}' -> Keep: {keep} (Expected: {should_keep})")
        
        if keep == should_keep:
            print("  ✓ Correct")
        else:
            print("  ✗ Wrong!")
        
        if keep:
            filtered_folders.append(folder_name)
    
    print(f"\nFiltered result: {filtered_folders}")
    expected = ['INBOX', 'Sent', 'Drafts', 'Trash']
    if filtered_folders == expected:
        print("✓ All filtering tests passed!")
    else:
        print("✗ Filtering test failed!")

if __name__ == "__main__":
    test_folder_filtering()