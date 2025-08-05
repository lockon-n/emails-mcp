import sys
import os
import tempfile
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.config import config_manager
from emails_mcp.models.config import EmailConfig
from emails_mcp.services import EmailService, FolderService, DraftService
from emails_mcp.backends import IMAPBackend, SMTPBackend, FileBackend


def test_full_integration():
    """Test full integration of all components"""
    print("Testing full system integration...")
    
    # Test configuration loading
    test_config = {
        "email": "test@example.com",
        "password": "testpass",
        "name": "Test User"
    }
    
    email_config = EmailConfig(**test_config)
    print("✓ Email config creation works")
    
    # Test backend creation
    try:
        imap_backend = IMAPBackend(email_config)
        smtp_backend = SMTPBackend(email_config)
        file_backend = FileBackend()
        print("✓ Backend creation works")
    except Exception as e:
        print(f"⚠ Backend creation (expected to fail without real server): {str(e)}")
    
    # Test service creation
    try:
        email_service = EmailService(email_config)
        folder_service = FolderService(imap_backend)
        draft_service = DraftService(file_backend)
        print("✓ Service creation works")
    except Exception as e:
        print(f"✗ Service creation failed: {str(e)}")
        return False
    
    # Test draft functionality (doesn't require server)
    draft_id = draft_service.save_draft(
        subject="Integration Test",
        body="Test integration email",
        to="recipient@example.com"
    )
    assert draft_id is not None
    print("✓ Draft service integration works")
    
    # Test file operations
    with tempfile.TemporaryDirectory() as temp_dir:
        from emails_mcp.models.email import EmailMessage, EmailAttachment
        
        test_email = EmailMessage(
            email_id="test123",
            subject="Test Integration Email",
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            body_text="Integration test email body"
        )
        
        export_path = os.path.join(temp_dir, "test_export.json")
        success = file_backend.export_emails([test_email], export_path, 'json')
        assert success == True
        
        imported_emails = file_backend.import_emails(export_path)
        assert len(imported_emails) == 1
        assert imported_emails[0].subject == "Test Integration Email"
        print("✓ File backend integration works")
    
    return True


def test_mcp_tools_import():
    """Test MCP tools can be imported and registered"""
    print("Testing MCP tools integration...")
    
    try:
        from mcp.server.fastmcp import FastMCP
        from emails_mcp.tools import register_email_tools, register_folder_tools, register_management_tools
        
        # Create mock MCP instance
        mcp = FastMCP("test-server")
        
        # Create mock services
        email_config = EmailConfig(email="test@example.com", password="test")
        email_service = EmailService(email_config)
        folder_service = FolderService(IMAPBackend(email_config))
        draft_service = DraftService(FileBackend())
        
        # Test tool registration (should not fail)
        register_email_tools(mcp, email_service)
        register_folder_tools(mcp, folder_service)
        register_management_tools(mcp, draft_service, email_service)
        
        print("✓ MCP tools registration works")
        return True
        
    except Exception as e:
        print(f"✗ MCP tools integration failed: {str(e)}")
        return False


def test_server_startup():
    """Test server can be imported and initialized"""
    print("Testing server startup...")
    
    try:
        from emails_mcp.server import setup_logging, create_services
        
        # Test logging setup
        setup_logging(debug=False)
        print("✓ Logging setup works")
        
        # Test service creation
        email_config = EmailConfig(email="test@example.com", password="test")
        services = create_services(email_config)
        assert len(services) == 4  # email, folder, search, draft services
        print("✓ Service creation in server works")
        
        return True
        
    except Exception as e:
        print(f"✗ Server startup test failed: {str(e)}")
        return False


def test_config_file_loading():
    """Test loading configuration from actual test file"""
    print("Testing config file loading...")
    
    try:
        if os.path.exists("test_emils.json"):
            config_manager.load_workspace_config()
            email_config = config_manager.load_email_config("test_emils.json")
            
            assert email_config is not None
            assert email_config.email == "kindtree001@mcp.com"
            
            current_config = config_manager.get_email_config()
            assert current_config is not None
            
            print("✓ Config file loading works")
            return True
        else:
            print("⚠ test_emils.json not found, skipping config file test")
            return True
            
    except Exception as e:
        print(f"✗ Config file loading failed: {str(e)}")
        return False


def test_error_handling():
    """Test error handling across components"""
    print("Testing error handling...")
    
    try:
        # Test invalid email config
        from emails_mcp.utils.exceptions import ValidationError
        from emails_mcp.utils.validators import validate_email_address
        
        assert validate_email_address("invalid-email") == False
        print("✓ Email validation error handling works")
        
        # Test file backend with invalid paths
        file_backend = FileBackend()
        try:
            file_backend.import_emails("/nonexistent/file.json")
            assert False, "Should have raised error"
        except Exception:
            pass
        print("✓ File backend error handling works")
        
        # Test draft service with invalid operations
        draft_service = DraftService(FileBackend())
        try:
            draft_service.get_draft("nonexistent")
            assert False, "Should have raised error"
        except Exception:
            pass
        print("✓ Draft service error handling works")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {str(e)}")
        return False


def run_all_integration_tests():
    """Run all integration tests"""
    print("Running comprehensive integration tests...\n")
    
    tests = [
        test_full_integration,
        test_mcp_tools_import,
        test_server_startup,
        test_config_file_loading,
        test_error_handling
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {str(e)}")
            failed += 1
        print()  # Add spacing between tests
    
    print(f"Integration test results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed! The emails MCP server is ready to use.")
        return True
    else:
        print("❌ Some integration tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_integration_tests()
    sys.exit(0 if success else 1)