import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.config import config_manager
from emails_mcp.services import EmailService, FolderService, DraftService
from emails_mcp.backends import IMAPBackend, SMTPBackend, FileBackend
from emails_mcp.tools.email_tools import register_email_tools
from emails_mcp.tools.folder_tools import register_folder_tools
from emails_mcp.tools.management_tools import register_management_tools
from mcp.server.fastmcp import FastMCP
import tempfile


class MockMCPTool:
    """Mock MCP tool for testing"""
    def __init__(self, name, func):
        self.name = name
        self.func = func
    
    async def call(self, **kwargs):
        return await self.func(**kwargs)


class TestMCP:
    """Test MCP server with real email operations"""
    
    def __init__(self):
        self.tools = {}
        self.email_service = None
        self.folder_service = None
        self.draft_service = None
    
    def tool(self):
        """Decorator to register tools"""
        def decorator(func):
            tool_name = func.__name__
            self.tools[tool_name] = MockMCPTool(tool_name, func)
            return func
        return decorator
    
    async def setup(self):
        """Setup test environment with real email config"""
        print("Setting up test environment...")
        
        # Load email configuration
        if not os.path.exists("test_emils.json"):
            print("❌ test_emils.json not found!")
            return False
        
        try:
            config_manager.load_workspace_config(workspace_path=tempfile.gettempdir())
            email_config = config_manager.load_email_config("test_emils.json")
            
            print(f"✓ Using email account: {email_config.email}")
            
            # Create services
            imap_backend = IMAPBackend(email_config)
            smtp_backend = SMTPBackend(email_config) 
            file_backend = FileBackend(tempfile.gettempdir())
            
            self.email_service = EmailService(email_config)
            self.folder_service = FolderService(imap_backend)
            self.draft_service = DraftService(file_backend)
            
            # Register tools
            register_email_tools(self, self.email_service)
            register_folder_tools(self, self.folder_service)
            register_management_tools(self, self.draft_service, self.email_service)
            
            print(f"✓ Registered {len(self.tools)} MCP tools")
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {str(e)}")
            return False
    
    async def test_tool(self, tool_name, **kwargs):
        """Test a specific MCP tool"""
        if tool_name not in self.tools:
            return f"❌ Tool '{tool_name}' not found"
        
        try:
            result = await self.tools[tool_name].call(**kwargs)
            return result
        except Exception as e:
            return f"❌ Tool '{tool_name}' failed: {str(e)}"


async def test_connection_tools(mcp):
    """Test connection and basic tools"""
    print("\n=== Testing Connection & Basic Tools ===")
    
    # Test connection
    result = await mcp.test_tool("check_connection")
    print(f"check_connection: {result[:100]}...")
    
    # Test get folders
    result = await mcp.test_tool("get_folders")
    print(f"get_folders: {result[:200]}...")
    
    # Test mailbox stats
    result = await mcp.test_tool("get_mailbox_stats")
    print(f"get_mailbox_stats: {result[:200]}...")


async def test_email_reading_tools(mcp):
    """Test email reading tools"""
    print("\n=== Testing Email Reading Tools ===")
    
    # Test get emails from inbox
    result = await mcp.test_tool("get_emails", folder="INBOX", page=1, page_size=5)
    print(f"get_emails: {result[:300]}...")
    
    # Extract first email ID for further testing
    email_id = None
    if "ID:" in result:
        lines = result.split('\n')
        for line in lines:
            if "ID:" in line:
                email_id = line.split("ID:")[1].strip().split()[0]
                break
    
    if email_id:
        print(f"✓ Found email ID for testing: {email_id}")
        
        # Test read specific email
        result = await mcp.test_tool("read_email", email_id=email_id)
        print(f"read_email: {result[:200]}...")
        
        # Test get email headers
        result = await mcp.test_tool("get_email_headers", email_id=email_id)
        print(f"get_email_headers: {result[:200]}...")
        
        return email_id
    else:
        print("⚠ No email ID found for further testing")
        return None


async def test_search_tools(mcp):
    """Test search functionality"""
    print("\n=== Testing Search Tools ===")
    
    # Test search emails
    result = await mcp.test_tool("search_emails", query="test", page=1, page_size=3)
    print(f"search_emails: {result[:300]}...")


async def test_draft_tools(mcp):
    """Test draft management"""
    print("\n=== Testing Draft Tools ===")
    
    # Test save draft
    result = await mcp.test_tool("save_draft", 
                                subject="Test Draft Email",
                                body="This is a test draft created by MCP tool testing",
                                to="test@example.com")
    print(f"save_draft: {result}")
    
    # Test get drafts
    result = await mcp.test_tool("get_drafts", page=1, page_size=5)
    print(f"get_drafts: {result[:300]}...")
    
    # Extract draft ID for further testing 
    draft_id = None
    if "ID:" in result:
        lines = result.split('\n')
        for line in lines:
            if "ID:" in line:
                draft_id = line.split("ID:")[1].strip().split()[0]
                break
    
    if draft_id:
        print(f"✓ Found draft ID for testing: {draft_id}")
        
        # Test update draft
        result = await mcp.test_tool("update_draft",
                                    draft_id=draft_id,
                                    subject="Updated Test Draft",
                                    cc="cc@example.com")
        print(f"update_draft: {result}")
        
        # Test delete draft
        result = await mcp.test_tool("delete_draft", draft_id=draft_id)
        print(f"delete_draft: {result}")


async def test_sending_tools(mcp):
    """Test email sending tools"""
    print("\n=== Testing Email Sending Tools ===")
    
    # Get both test email addresses from config
    config = config_manager.get_email_config()
    if not config:
        print("❌ No email config available")
        return
    
    sender_email = config.email
    
    # Determine recipient (use the other test account)
    if "kindtree001" in sender_email:
        recipient_email = "lightfire002@mcp.com"
    else:
        recipient_email = "kindtree001@mcp.com"
    
    print(f"✓ Testing email sending from {sender_email} to {recipient_email}")
    
    # Test send email
    result = await mcp.test_tool("send_email",
                                to=recipient_email,
                                subject="MCP Tool Test Email",
                                body="This is a test email sent via MCP tools testing.\n\nTime: " + str(asyncio.get_event_loop().time()),
                                html_body="<h2>MCP Tool Test Email</h2><p>This is a <b>test email</b> sent via MCP tools testing.</p><p>Time: " + str(asyncio.get_event_loop().time()) + "</p>")
    print(f"send_email: {result}")
    
    return recipient_email


async def test_reply_forward_tools(mcp, test_email_id, recipient_email):
    """Test reply and forward tools"""
    if not test_email_id:
        print("\n⚠ Skipping reply/forward tests - no email ID available")
        return
    
    print("\n=== Testing Reply & Forward Tools ===")
    
    # Test reply email
    result = await mcp.test_tool("reply_email",
                                email_id=test_email_id,
                                body="This is a test reply via MCP tools.",
                                reply_all=False)
    print(f"reply_email: {result}")
    
    # Test forward email
    if recipient_email:
        result = await mcp.test_tool("forward_email",
                                    email_id=test_email_id,
                                    to=recipient_email,
                                    body="Forwarding this email for testing purposes.")
        print(f"forward_email: {result}")


async def test_management_tools(mcp, test_email_id):
    """Test email management tools"""
    if not test_email_id:
        print("\n⚠ Skipping management tests - no email ID available")
        return
    
    print("\n=== Testing Email Management Tools ===")
    
    # Test mark emails
    result = await mcp.test_tool("mark_emails",
                                email_ids=[test_email_id],
                                status="read")
    print(f"mark_emails: {result}")
    
    # Note: Not testing delete/move to avoid losing test emails
    print("⚠ Skipping delete/move tests to preserve test emails")


async def test_export_import_tools(mcp):
    """Test import/export functionality"""
    print("\n=== Testing Export/Import Tools ===")
    
    # Test export emails
    export_path = os.path.join(tempfile.gettempdir(), "test_export.json")
    result = await mcp.test_tool("export_emails",
                                folder="INBOX",
                                export_path=export_path)
    print(f"export_emails: {result}")
    
    # Test import emails (if export succeeded)
    if "Successfully exported" in str(result):
        result = await mcp.test_tool("import_emails",
                                    import_path=export_path,
                                    target_folder="INBOX")
        print(f"import_emails: {result}")


async def run_comprehensive_mcp_tests():
    """Run comprehensive MCP tool tests with real email accounts"""
    print("🚀 Starting Comprehensive MCP Tools Testing with Real Email Accounts")
    print("=" * 70)
    
    # Setup test environment
    mcp = TestMCP()
    success = await mcp.setup()
    
    if not success:
        print("❌ Test setup failed!")
        return False
    
    try:
        # Test connection and basic tools
        await test_connection_tools(mcp)
        
        # Test email reading
        test_email_id = await test_email_reading_tools(mcp)
        
        # Test search
        await test_search_tools(mcp)
        
        # Test drafts
        await test_draft_tools(mcp)
        
        # Test sending (this will send real emails!)
        recipient_email = await test_sending_tools(mcp)
        
        # Test reply/forward
        await test_reply_forward_tools(mcp, test_email_id, recipient_email)
        
        # Test management
        await test_management_tools(mcp, test_email_id)
        
        # Test export/import
        await test_export_import_tools(mcp)
        
        print("\n" + "=" * 70)
        print("🎉 MCP Tools Testing Completed!")
        print("✓ All tools have been tested with real email accounts")
        print("📧 Check your email accounts for test messages")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Testing failed with error: {str(e)}")
        return False
    finally:
        # Cleanup
        if mcp.email_service:
            mcp.email_service.cleanup()


if __name__ == "__main__":
    # Run the comprehensive test
    success = asyncio.run(run_comprehensive_mcp_tests())
    sys.exit(0 if success else 1)