#!/usr/bin/env python3
"""
Test searching for the actual Chinese sender name "张小明"
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.email_service import EmailService
from src.emails_mcp.services.search_service import SearchService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_zhangxiaoming_search():
    """Test searching for the specific Chinese name '张小明' that exists in our mailbox"""
    config = EmailConfig(
        email="kindtree001@mcp.com",
        password="pass001",
        imap_server="localhost",
        imap_port=1143,
        smtp_server="localhost",
        smtp_port=1587,
        use_ssl=False
    )
    
    # Test queries based on what we found in the mailbox
    test_queries = [
        "张小明",        # Full Chinese name
        "张",           # First character
        "小明",         # Last two characters  
        "小",           # Middle character
        "明",           # Last character
    ]
    
    try:
        print("=== Testing search for existing Chinese sender: 张小明 <lightfire002@mcp.com> ===")
        
        # Test with general search
        email_service = EmailService(config)
        print("\n--- General search (TEXT search) ---")
        
        for query in test_queries:
            result = email_service.search_emails(query, folder="INBOX")
            print(f"Search '{query}': Found {result.total_results} emails")
            
            if result.emails:
                for email in result.emails:
                    if "张小明" in email.from_addr:
                        print(f"  ✅ Found target email - ID: {email.email_id}, From: {email.from_addr}")
                        break
        
        # Test with specific FROM search
        backend = IMAPBackend(config)
        search_service = SearchService(backend)
        
        print("\n--- Specific FROM field search ---")
        for query in test_queries:
            try:
                email_ids = search_service.search_by_sender(query, "INBOX")
                print(f"FROM search '{query}': Found {len(email_ids)} emails")
                
                if email_ids:
                    # Check if any of the found emails have the Chinese sender
                    backend.connect()
                    backend.select_folder("INBOX")
                    
                    for email_id in email_ids[:2]:  # Check first 2 results
                        try:
                            email = backend.fetch_email(email_id)
                            if "张小明" in email.from_addr:
                                print(f"  ✅ Found target sender in email {email_id}: {email.from_addr}")
                        except Exception as e:
                            print(f"  Error fetching email {email_id}: {e}")
                    
                    backend.disconnect()
                    
            except Exception as e:
                print(f"FROM search '{query}': Error - {str(e)}")
        
        # Test direct IMAP search with different approaches
        print("\n--- Testing different IMAP search approaches ---")
        backend.connect()
        backend.select_folder("INBOX")
        
        for query in test_queries:
            print(f"\nTesting query: '{query}'")
            
            # Method 1: Standard FROM search
            try:
                query_bytes = query.encode('utf-8')
                search_criteria = b'FROM "' + query_bytes + b'"'
                
                if backend.utf8_enabled:
                    status, email_ids = backend.connection.search(None, search_criteria)
                else:
                    try:
                        status, email_ids = backend.connection.search('UTF-8', search_criteria)
                    except:
                        status, email_ids = backend.connection.search(None, f'FROM "{query}"')
                
                count = len(email_ids[0].split()) if status == 'OK' and email_ids[0] else 0
                print(f"  FROM search: {count} emails")
                
            except Exception as e:
                print(f"  FROM search error: {e}")
            
            # Method 2: HEADER FROM search (alternative approach)
            try:
                query_bytes = query.encode('utf-8')
                search_criteria = b'HEADER FROM "' + query_bytes + b'"'
                
                if backend.utf8_enabled:
                    status, email_ids = backend.connection.search(None, search_criteria)
                else:
                    try:
                        status, email_ids = backend.connection.search('UTF-8', search_criteria)
                    except:
                        status, email_ids = backend.connection.search(None, f'HEADER FROM "{query}"')
                
                count = len(email_ids[0].split()) if status == 'OK' and email_ids[0] else 0
                print(f"  HEADER FROM search: {count} emails")
                
            except Exception as e:
                print(f"  HEADER FROM search error: {e}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Test error: {str(e)}")

if __name__ == "__main__":
    test_zhangxiaoming_search()