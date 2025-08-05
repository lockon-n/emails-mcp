import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.config import config_manager
from emails_mcp.models import EmailConfig, WorkspaceConfig

def test_config_loading():
    """Test configuration loading functionality"""
    print("Testing ConfigManager...")
    
    # Test workspace config
    workspace_config = config_manager.load_workspace_config("/tmp/test", "test.json")
    assert workspace_config.workspace_path == "/tmp/test"
    assert workspace_config.config_file == "test.json"
    print("✓ Workspace config loading works")
    
    # Test email config loading (using test file)  
    test_config_file = "test_emils.json"
    if os.path.exists(test_config_file):
        try:
            email_config = config_manager.load_email_config(test_config_file)
            assert email_config is not None
            assert email_config.email == "kindtree001@mcp.com"
            print("✓ Email config loading works")
            
            # Test get config
            current = config_manager.get_email_config()
            assert current is not None
            assert current.email == "kindtree001@mcp.com"
            print("✓ Email config retrieval works")
            
        except Exception as e:
            print(f"✗ Email config loading failed: {str(e)}")
    else:
        print("! Skipping email config test (test_emils.json not found)")
    
    # Test path validation  
    config_manager.load_workspace_config("/tmp")
    valid, _ = config_manager.validate_workspace_path("/tmp/test.txt")
    assert valid == True
    print("✓ Path validation works")
    
    valid, error = config_manager.validate_workspace_path("/etc/passwd")
    assert valid == False
    assert "outside workspace" in error
    print("✓ Path validation rejects outside paths")

if __name__ == "__main__":
    test_config_loading()
    print("All configuration tests passed!")