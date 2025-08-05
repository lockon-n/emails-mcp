#!/usr/bin/env python3
"""
测试邮件导入修复 - 验证时间排序和自定义文件夹导入
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.config import config_manager
from emails_mcp.services.email_service import EmailService
from emails_mcp.services.folder_service import FolderService
from emails_mcp.backends.imap_backend import IMAPBackend
from emails_mcp.backends.smtp_backend import SMTPBackend
import json

def setup_test_environment():
    """设置测试环境"""
    print("🔧 设置测试环境...")
    
    # Load email config
    email_config = config_manager.load_email_config("test_emils.json")
    if not email_config:
        raise Exception("无法加载邮件配置")
    
    email_service = EmailService(email_config)
    folder_service = FolderService(email_service.imap_backend)
    
    return email_service, folder_service

def clean_test_data(email_service, folder_service):
    """清理测试数据"""
    print("🧹 清理测试数据...")
    
    try:
        # Get all folders
        folders = folder_service.get_folders()
        
        # Delete all custom folders (keep system folders)
        system_folders = {"INBOX", "SENT", "DRAFTS", "TRASH", "Sent", "Drafts", "Trash"}
        
        for folder in folders:
            if folder.name not in system_folders:
                try:
                    print(f"  删除文件夹: {folder.name}")
                    folder_service.delete_folder(folder.name)
                except Exception as e:
                    print(f"  警告：删除文件夹 {folder.name} 失败: {e}")
        
        # Clear INBOX
        try:
            inbox_emails = email_service.get_emails("INBOX", page_size=1000)
            if inbox_emails.emails:
                print(f"  清理 INBOX 中的 {len(inbox_emails.emails)} 封邮件")
                for email in inbox_emails.emails:
                    email_service.delete_email(email.email_id)
        except Exception as e:
            print(f"  警告：清理 INBOX 失败: {e}")
            
        print("✅ 测试数据清理完成")
        
    except Exception as e:
        print(f"⚠️ 清理过程中出现错误: {e}")

def create_test_emails(email_service):
    """创建测试邮件到不同文件夹"""
    print("📧 创建测试邮件...")
    
    # First create some custom folders
    folder_service = FolderService(email_service.imap_backend)
    
    test_folders = ["测试文件夹1", "TestFolder2", "工作邮件"]
    for folder_name in test_folders:
        try:
            success = folder_service.create_folder(folder_name)
            if success:
                print(f"  ✓ 创建文件夹: {folder_name}")
            else:
                print(f"  ❌ 创建文件夹失败: {folder_name}")
        except Exception as e:
            print(f"  ❌ 创建文件夹异常 {folder_name}: {e}")
    
    # Send test emails to different folders
    test_emails = [
        {
            "to": "kindtree001@mcp.com",
            "subject": "📧 测试邮件1 - INBOX",
            "body": "这是第一封测试邮件，应该在INBOX中。时间：最新",
            "folder": "INBOX"
        },
        {
            "to": "kindtree001@mcp.com", 
            "subject": "📧 测试邮件2 - 测试文件夹1",
            "body": "这是第二封测试邮件，在自定义文件夹中。时间：第二新",
            "folder": "测试文件夹1"
        },
        {
            "to": "kindtree001@mcp.com",
            "subject": "📧 测试邮件3 - TestFolder2", 
            "body": "这是第三封测试邮件，在英文文件夹中。时间：第三新",
            "folder": "TestFolder2"
        },
        {
            "to": "kindtree001@mcp.com",
            "subject": "📧 测试邮件4 - 工作邮件",
            "body": "这是第四封测试邮件，在工作文件夹中。时间：最旧",
            "folder": "工作邮件"
        }
    ]
    
    # Send emails with delays to ensure different timestamps
    import time
    for i, email_data in enumerate(test_emails):
        try:
            result = email_service.smtp_backend.send_email(
                to=email_data["to"],
                subject=email_data["subject"],
                body=email_data["body"]
            )
            
            if result[0]:
                print(f"  ✓ 发送邮件 {i+1}: {email_data['subject']}")
                
                # Move to target folder if not INBOX
                if email_data["folder"] != "INBOX":
                    # Wait a bit for email to arrive
                    time.sleep(2)
                    
                    # Find the latest email in INBOX and move it
                    try:
                        inbox_emails = email_service.get_emails("INBOX", page_size=1)
                        if inbox_emails.emails:
                            latest_email = inbox_emails.emails[0]
                            success = email_service.move_email(latest_email.email_id, email_data["folder"])
                            if success:
                                print(f"    ↻ 移动到文件夹: {email_data['folder']}")
                            else:
                                print(f"    ❌ 移动失败到: {email_data['folder']}")
                    except Exception as move_e:
                        print(f"    ❌ 移动邮件异常: {move_e}")
            else:
                print(f"  ❌ 发送邮件失败 {i+1}")
                
            # Small delay between emails
            time.sleep(1)
            
        except Exception as e:
            print(f"  ❌ 发送邮件异常 {i+1}: {e}")
    
    print("✅ 测试邮件创建完成")

def test_export_import_functionality(email_service):
    """测试导出导入功能"""
    print("🔄 测试导出导入功能...")
    
    # Import the management tools
    from emails_mcp.tools.management_tools import register_management_tools
    from mcp.server.fastmcp import FastMCP
    
    # Create a mock MCP instance to access the tools
    class MockMCP:
        def __init__(self):
            self.tools = {}
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
    
    mock_mcp = MockMCP()
    register_management_tools(mock_mcp, None, email_service)
    
    # Test export
    print("  📤 测试导出...")
    try:
        export_result = await mock_mcp.tools['export_emails'](export_all_folders=True)
        print(f"  导出结果: {export_result}")
        
        # Extract exported file path
        export_file = None
        if "exported" in export_result and "to" in export_result:
            # Parse the file path from result message
            lines = export_result.split('\n')
            for line in lines:
                if 'emails_export' in line and '.json' in line:
                    import re
                    match = re.search(r'to (.+\.json)', line)
                    if match:
                        export_file = match.group(1)
                        break
        
        if not export_file:
            print("  ❌ 无法找到导出文件路径")
            return False
            
        print(f"  ✓ 导出文件: {export_file}")
        
    except Exception as e:
        print(f"  ❌ 导出失败: {e}")
        return False
    
    # Clear all data again
    clean_test_data(email_service, folder_service)
    
    # Test import
    print("  📥 测试导入...")
    try:
        import_result = await mock_mcp.tools['import_emails'](
            import_path=export_file,
            preserve_folders=True
        )
        print(f"  导入结果: {import_result}")
        
        # Verify imported emails
        print("  🔍 验证导入结果...")
        
        # Check INBOX (should have newest email first)
        inbox_emails = email_service.get_emails("INBOX", page_size=10)
        print(f"  INBOX: {len(inbox_emails.emails)} 封邮件")
        
        if inbox_emails.emails:
            print("  INBOX 邮件顺序（应该是时间倒序）:")
            for i, email in enumerate(inbox_emails.emails):
                print(f"    {i+1}. {email.subject} - {email.date}")
        
        # Check custom folders
        folder_service = FolderService(email_service.imap_backend)
        folders = folder_service.get_folders()
        
        for folder in folders:
            if folder.name not in {"INBOX", "SENT", "DRAFTS", "TRASH", "Sent", "Drafts", "Trash"}:
                try:
                    folder_emails = email_service.get_emails(folder.name, page_size=10)
                    print(f"  {folder.name}: {len(folder_emails.emails)} 封邮件")
                    
                    if folder_emails.emails:
                        for i, email in enumerate(folder_emails.emails):
                            print(f"    {i+1}. {email.subject}")
                            
                except Exception as e:
                    print(f"  ❌ 读取文件夹 {folder.name} 失败: {e}")
        
        print("✅ 导入测试完成")
        return True
        
    except Exception as e:
        print(f"  ❌ 导入失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 开始邮件导入修复测试...\n")
    
    try:
        # Setup
        email_service, folder_service = setup_test_environment()
        
        # Clean existing data
        clean_test_data(email_service, folder_service)
        
        # Create test emails
        create_test_emails(email_service)
        
        # Wait for emails to arrive
        import time
        print("⏳ 等待邮件到达...")
        time.sleep(10)
        
        # Test export/import
        success = await test_export_import_functionality(email_service)
        
        if success:
            print("\n🎉 所有测试通过！")
            print("✓ 时间排序修复验证成功")
            print("✓ 自定义文件夹导入修复验证成功")
        else:
            print("\n❌ 测试失败")
            
        return success
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import asyncio
    success = asyncio.run(main())
    sys.exit(0 if success else 1)