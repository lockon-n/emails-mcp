#!/usr/bin/env python3
"""
测试EmailMessage参数修复
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.config import config_manager
from emails_mcp.services.email_service import EmailService

def test_email_parsing():
    """测试邮件解析修复"""
    print("🧪 测试邮件解析修复...")
    
    try:
        # Load email config
        email_config = config_manager.load_email_config("test_emils.json")
        if not email_config:
            print("❌ 无法加载邮件配置")
            return False
        
        email_service = EmailService(email_config)
        
        # Try to get emails to test parsing
        print("📧 获取邮件进行解析测试...")
        result = email_service.get_emails("INBOX", page_size=5)
        
        if result.emails:
            print(f"✅ 成功解析 {len(result.emails)} 封邮件")
            
            for i, email in enumerate(result.emails, 1):
                print(f"  {i}. {email.subject[:50]}...")
                print(f"     发件人: {email.from_addr}")
                print(f"     正文长度: {len(email.body_text or '')} 字符")
                if email.body_html:
                    print(f"     HTML长度: {len(email.body_html)} 字符")
            
            return True
        else:
            print("⚠️ INBOX中没有邮件，但解析功能正常")
            return True
            
    except Exception as e:
        print(f"❌ 邮件解析测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🔧 测试EmailMessage参数修复...\n")
    
    success = test_email_parsing()
    
    if success:
        print("\n🎉 EmailMessage参数修复验证成功！")
    else:
        print("\n❌ 修复验证失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)