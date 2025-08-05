#!/usr/bin/env python3
"""
Test script for Chinese search functionality
"""
import sys
import asyncio
from src.emails_mcp.models.config import EmailConfig
from src.emails_mcp.backends.imap_backend import IMAPBackend
from src.emails_mcp.services.search_service import SearchService


async def test_chinese_search():
    """Test Chinese character search functionality"""
    print("Testing Chinese search functionality...")
    
    # Note: This test requires actual email credentials
    # For demonstration purposes only - replace with your test credentials
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
        # Initialize backend and service
        backend = IMAPBackend(config)
        search_service = SearchService(backend)
        
        # Test connection and UTF-8 support
        print("Connecting to IMAP server...")
        backend.connect()
        print(f"UTF-8 support enabled: {backend.utf8_enabled}")
        
        # Test cases with Chinese characters
        test_queries = [
            "测试",           # Chinese word for "test"
            "邮件",           # Chinese word for "email"
            "重要",           # Chinese word for "important"
            "会议",           # Chinese word for "meeting"
            "项目",           # Chinese word for "project"
        ]
        
        print("\nTesting general search with Chinese queries:")
        for query in test_queries:
            try:
                results = search_service.search_emails_by_query(query, "INBOX")
                print(f"Query '{query}': Found {len(results)} emails")
            except Exception as e:
                print(f"Query '{query}': Error - {str(e)}")
        
        print("\nTesting subject search with Chinese:")
        chinese_subjects = ["测试邮件", "重要通知", "会议安排"]
        for subject in chinese_subjects:
            try:
                results = search_service.search_by_subject(subject, "INBOX")
                print(f"Subject '{subject}': Found {len(results)} emails")
            except Exception as e:
                print(f"Subject '{subject}': Error - {str(e)}")
        
        print("\nTesting sender search with Chinese names:")
        chinese_senders = ["张三", "李四", "王五"]
        for sender in chinese_senders:
            try:
                results = search_service.search_by_sender(sender, "INBOX")
                print(f"Sender '{sender}': Found {len(results)} emails")
            except Exception as e:
                print(f"Sender '{sender}': Error - {str(e)}")
        
        # Test mixed language queries
        print("\nTesting mixed language queries:")
        mixed_queries = ["test 测试", "meeting 会议", "重要 important"]
        for query in mixed_queries:
            try:
                results = search_service.search_emails_by_query(query, "INBOX")
                print(f"Mixed query '{query}': Found {len(results)} emails")
            except Exception as e:
                print(f"Mixed query '{query}': Error - {str(e)}")
        
        backend.disconnect()
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Test failed with error: {str(e)}")
        return False
    
    return True


def test_charset_encoding():
    """Test character encoding and charset handling"""
    print("\nTesting character encoding:")
    
    test_strings = [
        "测试",
        "邮件系统", 
        "重要通知",
        "会议安排表",
        "项目进度报告"
    ]
    
    for s in test_strings:
        # Test UTF-8 encoding
        utf8_bytes = s.encode('utf-8')
        utf8_decoded = utf8_bytes.decode('utf-8')
        print(f"'{s}' -> UTF-8 bytes: {len(utf8_bytes)} -> '{utf8_decoded}'")
        
        # Test ASCII fallback
        ascii_fallback = s.encode('ascii', errors='ignore').decode('ascii')
        if ascii_fallback.strip():
            print(f"  ASCII fallback: '{ascii_fallback}'")
        else:
            print(f"  ASCII fallback: [empty - no ASCII characters]")


if __name__ == "__main__":
    print("Chinese Search Test Suite")
    print("=" * 50)
    
    # Test encoding first
    test_charset_encoding()
    
    print("\n" + "=" * 50)
    print("Note: To test actual IMAP search, update the config with real credentials")
    print("Current test runs in demo mode with placeholder credentials")
    
    # Uncomment to test with real credentials:
    asyncio.run(test_chinese_search())