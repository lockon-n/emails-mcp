#!/usr/bin/env python3
"""
Test SUBJECT vs BODY search differences for Chinese characters
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend

# Set up logging to see detailed messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_individual_search_methods():
    """Test individual search methods to isolate the problem"""
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
        
        test_query = "测试"
        print(f"Testing with Chinese query: '{test_query}'")
        print(f"UTF-8 enabled: {backend.utf8_enabled}")
        print("=" * 60)
        
        # Test individual search criteria
        search_types = [
            ("SUBJECT only", f'SUBJECT "{test_query}"'),
            ("FROM only", f'FROM "{test_query}"'), 
            ("BODY only", f'BODY "{test_query}"'),
            ("TEXT only", f'TEXT "{test_query}"'),  # TEXT searches all text parts
        ]
        
        for search_name, search_criteria in search_types:
            print(f"\n{search_name}: {search_criteria}")
            try:
                # Test with UTF-8 bytes encoding
                query_bytes = test_query.encode('utf-8')
                if backend.utf8_enabled:
                    criteria_bytes = search_criteria.replace(f'"{test_query}"', f'"{query_bytes.decode("utf-8")}"').encode('utf-8')
                    status, email_ids = backend.connection.search(None, criteria_bytes)
                else:
                    # Try UTF-8 charset first
                    try:
                        criteria_bytes = search_criteria.replace(f'"{test_query}"', f'"{query_bytes.decode("utf-8")}"').encode('utf-8')
                        status, email_ids = backend.connection.search('UTF-8', criteria_bytes)
                    except Exception as e:
                        print(f"  UTF-8 charset failed: {e}")
                        # Fallback to None charset
                        status, email_ids = backend.connection.search(None, search_criteria)
                
                if status == 'OK':
                    count = len(email_ids[0].split()) if email_ids[0] else 0
                    print(f"  ✅ SUCCESS: Found {count} emails")
                else:
                    print(f"  ❌ FAILED: Status = {status}")
                    
            except Exception as e:
                print(f"  ❌ ERROR: {str(e)}")
        
        # Test with literal syntax (alternative approach)
        print(f"\n" + "=" * 60)
        print("Testing with IMAP LITERAL syntax:")
        
        try:
            # Set up literal for Chinese query
            backend.connection.literal = test_query.encode('utf-8')
            
            # Try BODY search with literal
            status, email_ids = backend.connection.search(None, 'BODY')
            if status == 'OK':
                count = len(email_ids[0].split()) if email_ids[0] else 0
                print(f"  BODY with literal: Found {count} emails")
            else:
                print(f"  BODY with literal failed: {status}")
                
        except Exception as e:
            print(f"  Literal syntax error: {str(e)}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    test_individual_search_methods()