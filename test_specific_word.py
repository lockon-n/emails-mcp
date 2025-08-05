#!/usr/bin/env python3
"""
Test searching for specific Chinese word "亲爱的" that only appears in email body
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.email_service import EmailService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_qinaide_search():
    """Test searching for '亲爱的' which should only appear in email body"""
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
        # Test with EmailService (like MCP tool does)
        email_service = EmailService(config)
        
        test_query = "亲爱的"
        print(f"Searching for: '{test_query}' (should only be in email body)")
        print("=" * 60)
        
        # Use the actual MCP search method
        result = email_service.search_emails(test_query, folder="INBOX")
        print(f"EmailService search result: Found {result.total_results} emails")
        
        if result.emails:
            for i, email in enumerate(result.emails):
                print(f"\nEmail {i+1}:")
                print(f"  ID: {email.email_id}")
                print(f"  Subject: {email.subject}")
                print(f"  From: {email.from_addr}")
                
                # Check if the word appears in subject vs body
                subject_contains = test_query in email.subject if email.subject else False
                body_contains = (test_query in email.body_text if email.body_text else False) or \
                               (test_query in email.body_html if email.body_html else False)
                
                print(f"  Contains '{test_query}' in subject: {subject_contains}")
                print(f"  Contains '{test_query}' in body: {body_contains}")
        
        print("\n" + "=" * 60)
        print("Now testing individual search methods:")
        
        # Test with direct backend methods
        backend = IMAPBackend(config)
        backend.connect()
        backend.select_folder("INBOX")
        
        # Test different search criteria
        search_tests = [
            ("Combined (OR SUBJECT FROM BODY)", f'(OR SUBJECT "{test_query}" FROM "{test_query}" BODY "{test_query}")'),
            ("SUBJECT only", f'SUBJECT "{test_query}"'),
            ("BODY only", f'BODY "{test_query}"'),
            ("TEXT only", f'TEXT "{test_query}"'),
        ]
        
        for test_name, search_criteria in search_tests:
            print(f"\n{test_name}:")
            try:
                # Use the same encoding logic as our fixed search method
                query_bytes = test_query.encode('utf-8')
                if backend.utf8_enabled:
                    criteria_bytes = search_criteria.encode('utf-8')
                    status, email_ids = backend.connection.search(None, criteria_bytes)
                else:
                    try:
                        criteria_bytes = search_criteria.encode('utf-8')
                        status, email_ids = backend.connection.search('UTF-8', criteria_bytes)
                    except Exception as e:
                        print(f"  UTF-8 charset failed: {e}")
                        status, email_ids = backend.connection.search(None, search_criteria)
                
                if status == 'OK':
                    count = len(email_ids[0].split()) if email_ids[0] else 0
                    print(f"  ✅ Found {count} emails")
                    
                    # Show first few email IDs
                    if email_ids[0]:
                        ids = [uid.decode() for uid in reversed(email_ids[0].split())][:3]
                        print(f"  First few IDs: {ids}")
                else:
                    print(f"  ❌ Failed: {status}")
                    
            except Exception as e:
                print(f"  ❌ Error: {str(e)}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Connection error: {str(e)}")

if __name__ == "__main__":
    test_qinaide_search()