#!/usr/bin/env python3
"""
测试SMTP修复 - 发送HTML格式的中英文邮件（包含CC和BCC）
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.config import config_manager
from emails_mcp.backends.smtp_backend import SMTPBackend

def test_smtp_connection():
    """测试SMTP连接和认证修复"""
    smtp_backend = None
    try:
        # 加载配置
        email_config = config_manager.load_email_config("test_emils.json")
        if not email_config:
            print("❌ 无法加载邮件配置")
            return False
            
        print(f"✓ 使用邮件账户: {email_config.email}")
        print(f"✓ SMTP: {email_config.smtp_server}:{email_config.smtp_port}")
        print(f"✓ SSL: {email_config.use_ssl}, StartTLS: {email_config.use_starttls}")
        
        # 创建SMTP后端
        smtp_backend = SMTPBackend(email_config)
        
        # 测试连接
        print("\n📤 测试SMTP连接...")
        success = smtp_backend.test_connection()
        
        if success:
            print("✅ SMTP连接成功!")
            
            # 测试发送HTML邮件
            print("\n📧 测试发送HTML格式的中英文邮件...")
            
            # HTML内容
            html_body = """
            <html>
            <body>
                <h2>测试邮件 / Test Email</h2>
                <p><strong>中文内容：</strong>这是一封测试邮件，用于验证HTML格式和中英文混合内容。</p>
                <p><strong>English Content:</strong> This is a test email to verify HTML formatting and mixed Chinese-English content.</p>
                <ul>
                    <li>支持HTML格式 / HTML Format Support</li>
                    <li>中英文混合 / Mixed Languages</li>
                    <li>CC和BCC功能 / CC and BCC Features</li>
                </ul>
                <p style="color: blue;">蓝色文字 / <em>Blue Text</em></p>
            </body>
            </html>
            """
            
            # 纯文本内容
            text_body = """
测试邮件 / Test Email

中文内容：这是一封测试邮件，用于验证HTML格式和中英文混合内容。
English Content: This is a test email to verify HTML formatting and mixed Chinese-English content.

功能测试：
- 支持HTML格式 / HTML Format Support  
- 中英文混合 / Mixed Languages
- CC and BCC Features
            """
            
            result = smtp_backend.send_email(
                to="kindtree001@mcp.com",
                subject="🧪 HTML中英文测试邮件 / HTML Mixed Language Test",
                body=text_body,
                html_body=html_body,
                cc="lightfire002@mcp.com", 
                bcc="darkorange003@mcp.com"
            )
            
            if result[0]:
                print("✅ HTML中英文邮件发送成功!")
                print("   - TO: kindtree001@mcp.com")
                print("   - CC: lightfire002@mcp.com")  
                print("   - BCC: darkorange003@mcp.com")
                return True
            else:
                print("❌ 邮件发送失败")
                return False
                
        else:
            print("❌ SMTP连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False
    finally:
        if smtp_backend:
            smtp_backend.disconnect()

if __name__ == "__main__":
    print("🔧 测试SMTP修复和HTML邮件发送...")
    success = test_smtp_connection()
    sys.exit(0 if success else 1)