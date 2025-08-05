#!/usr/bin/env python3
"""Test IMAP folder parsing"""

def test_imap_folder_parsing():
    """Test parsing of IMAP folder list responses"""
    
    # Common IMAP LIST response formats
    test_responses = [
        b'(\\HasNoChildren) "." "INBOX"',
        b'(\\HasChildren) "." "INBOX.Sent"', 
        b'(\\HasNoChildren) "/" "Sent"',
        b'(\\HasNoChildren \\Sent) "/" "Sent Messages"',
        b'(\\HasNoChildren \\Drafts) "/" "Drafts"',
        b'(\\HasNoChildren) "." "Trash"'
    ]
    
    print("Testing IMAP folder parsing:")
    print("=" * 50)
    
    for response in test_responses:
        folder_info = response.decode('utf-8')
        print(f"Raw response: {folder_info}")
        
        # Current parsing logic (incorrect)
        parts_old = folder_info.split('"')
        if len(parts_old) >= 3:
            folder_name_old = parts_old[-2]  # This gets the delimiter, not the folder name
            print(f"  Old parsing result: '{folder_name_old}'")
        
        # Correct parsing logic
        import re
        # Match the pattern: (flags) "delimiter" "folder_name"
        match = re.match(r'\(.*?\)\s+".*?"\s+"(.+)"', folder_info)
        if match:
            folder_name_new = match.group(1)
            print(f"  Correct parsing result: '{folder_name_new}'")
        else:
            print(f"  No match found")
        
        print()

if __name__ == "__main__":
    test_imap_folder_parsing()