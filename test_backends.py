import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.models.config import EmailConfig
from emails_mcp.backends import FileBackend
from emails_mcp.models.email import EmailMessage, EmailAttachment
import tempfile
import json

def test_file_backend():
    """Test file backend operations"""
    print("Testing FileBackend...")
    
    # Create test email data
    attachment = EmailAttachment(
        filename="test.txt",
        content_type="text/plain",
        size=100
    )
    
    test_email = EmailMessage(
        email_id="test123",
        subject="Test Email",
        from_addr="sender@example.com",
        to_addr="recipient@example.com",
        body_text="Test email body",
        attachments=[attachment]
    )
    
    # Test export to JSON
    with tempfile.TemporaryDirectory() as temp_dir:
        backend = FileBackend(temp_dir)
        export_path = os.path.join(temp_dir, "export.json")
        
        success = backend.export_emails([test_email], export_path, 'json')
        assert success == True
        print("✓ JSON export works")
        
        # Test import from JSON
        imported_emails = backend.import_emails(export_path)
        assert len(imported_emails) == 1
        assert imported_emails[0].subject == "Test Email"
        assert imported_emails[0].from_addr == "sender@example.com"
        print("✓ JSON import works")
        
        # Test attachment saving
        test_data = b"Test attachment content"
        saved_path = backend.save_attachment(test_data, "test.txt", temp_dir)
        assert os.path.exists(saved_path)
        
        with open(saved_path, 'rb') as f:
            assert f.read() == test_data
        print("✓ Attachment saving works")


def test_backend_validation():
    """Test backend validation"""
    print("Testing backend validation...")
    
    backend = FileBackend()
    
    # Test invalid export path
    try:
        backend.export_emails([], "")
        assert False, "Should have raised ValidationError"
    except Exception as e:
        assert "path cannot be empty" in str(e)
    print("✓ Export path validation works")
    
    # Test invalid import path
    try:
        backend.import_emails("/nonexistent/file.json")
        assert False, "Should have raised ValidationError"
    except Exception as e:
        assert "does not exist" in str(e)
    print("✓ Import path validation works")


if __name__ == "__main__":
    test_file_backend()
    test_backend_validation()
    print("All backend tests passed!")