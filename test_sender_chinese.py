#!/usr/bin/env python3
"""
Test Chinese sender search functionality
"""
import logging
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.email_service import EmailService
from src.emails_mcp.services.search_service import SearchService

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_chinese_sender_search():
    """Test searching for Chinese names/text in sender field"""
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
        # First, let's see what senders we have in the mailbox
        email_service = EmailService(config)
        
        print("=== Examining current emails to find sender information ===")
        result = email_service.get_emails("INBOX", page=1, page_size=10)
        
        print(f"Found {result.total_results} emails total")
        print("\nSender information:")
        unique_senders = set()
        
        for i, email in enumerate(result.emails):
            sender = email.from_addr
            unique_senders.add(sender)
            print(f"{i+1}. From: {sender}")
            print(f"   Subject: {email.subject}")
            
            # Check if sender contains any Chinese characters
            contains_chinese = any('\u4e00' <= char <= '\u9fff' for char in sender)
            if contains_chinese:
                print(f"   ✅ Contains Chinese characters")
            print()
        
        print(f"\nUnique senders: {len(unique_senders)}")
        for sender in sorted(unique_senders):
            print(f"  - {sender}")
        
        print("\n" + "=" * 60)
        print("=== Testing sender search functionality ===")
        
        # Test various Chinese terms that might be in sender names or email addresses
        test_queries = [
            "lightfire002",  # English part of email
            "mcp.com",       # Domain part
            "测试",          # Chinese word
            "中文",          # Chinese word meaning "Chinese"
            "张三",          # Common Chinese name
            "李四",          # Common Chinese name
        ]
        
        # Test with general search (should find in any field including FROM)
        print("\n--- Testing general search (TEXT search) ---")
        for query in test_queries:
            result = email_service.search_emails(query, folder="INBOX")
            print(f"Search '{query}': Found {result.total_results} emails")
            
            if result.emails:
                for email in result.emails[:2]:  # Show first 2 results
                    print(f"  - ID: {email.email_id}, From: {email.from_addr}")
        
        # Test with specific FROM search using SearchService
        print("\n--- Testing specific FROM field search ---")
        backend = IMAPBackend(config)
        search_service = SearchService(backend)
        
        for query in test_queries:
            try:
                email_ids = search_service.search_by_sender(query, "INBOX")
                print(f"FROM search '{query}': Found {len(email_ids)} emails")
                
                if email_ids:
                    print(f"  Email IDs: {email_ids[:3]}")  # Show first 3 IDs
                    
            except Exception as e:
                print(f"FROM search '{query}': Error - {str(e)}")
        
        # Test with direct IMAP FROM search
        print("\n--- Testing direct IMAP FROM search ---")
        backend.connect()
        backend.select_folder("INBOX")
        
        for query in test_queries:
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
                
                if status == 'OK':
                    count = len(email_ids[0].split()) if email_ids[0] else 0
                    print(f"IMAP FROM '{query}': Found {count} emails")
                else:
                    print(f"IMAP FROM '{query}': Failed - {status}")
                    
            except Exception as e:
                print(f"IMAP FROM '{query}': Error - {str(e)}")
        
        backend.disconnect()
        
    except Exception as e:
        print(f"Test error: {str(e)}")

if __name__ == "__main__":
    test_chinese_sender_search()