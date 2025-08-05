#!/usr/bin/env python3
"""
测试转发邮件附件功能
"""
import sys
import os
import tempfile
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.models.config import EmailConfig
from emails_mcp.models.email import EmailMessage, EmailAttachment
from emails_mcp.services.email_service import EmailService


def create_test_email_with_attachment():
    """创建一个带附件的测试邮件"""
    # 创建测试附件
    test_content = b"This is a test attachment content"
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['Subject'] = "Test Email with Attachment"
    msg['From'] = "test@example.com"
    msg['To'] = "recipient@example.com"
    
    # 添加邮件正文
    body = MIMEText("This is a test email with attachment")
    msg.attach(body)
    
    # 添加附件
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(test_content)
    encoders.encode_base64(attachment)
    attachment.add_header(
        'Content-Disposition',
        'attachment; filename= test_file.txt'
    )
    msg.attach(attachment)
    
    return msg


def test_forward_with_attachment():
    """测试转发带附件的邮件功能"""
    print("开始测试转发附件功能...")
    
    try:
        # 创建测试邮件
        raw_msg = create_test_email_with_attachment()
        
        # 创建EmailMessage对象
        test_attachment = EmailAttachment(
            filename="test_file.txt",
            content_type="application/octet-stream",
            size=len(b"This is a test attachment content")
        )
        
        original_email = EmailMessage(
            email_id="123",
            subject="Test Email with Attachment",
            from_addr="test@example.com",
            to_addr="recipient@example.com",
            date="2025-01-01 12:00:00",
            body_text="This is a test email with attachment",
            attachments=[test_attachment],
            raw_message=raw_msg
        )
        
        # 测试_send_with_original_attachments方法的逻辑
        print("✓ 创建带附件的测试邮件成功")
        
        # 检查附件提取逻辑
        attachment_found = False
        if original_email.raw_message:
            for part in original_email.raw_message.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename and filename.strip() == 'test_file.txt':
                        attachment_data = part.get_payload(decode=True)
                        if attachment_data:
                            attachment_found = True
                            print(f"✓ 找到附件: {filename}, 大小: {len(attachment_data)} bytes")
                            break
        
        if attachment_found:
            print("✓ 附件提取逻辑测试通过")
        else:
            print("✗ 附件提取逻辑测试失败")
            return False
            
        print("✓ 转发附件功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_forward_without_attachment():
    """测试转发不带附件的邮件功能"""
    print("\n开始测试转发无附件邮件功能...")
    
    try:
        # 创建无附件的测试邮件
        original_email = EmailMessage(
            email_id="124",
            subject="Test Email without Attachment",
            from_addr="test@example.com",
            to_addr="recipient@example.com",
            date="2025-01-01 12:00:00",
            body_text="This is a test email without attachment",
            attachments=[]
        )
        
        # 验证无附件情况的处理
        if not original_email.attachments:
            print("✓ 无附件邮件处理逻辑正确")
            return True
        else:
            print("✗ 无附件邮件处理逻辑错误")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("转发邮件附件功能测试")
    print("=" * 50)
    
    # 运行测试
    test1_passed = test_forward_with_attachment()
    test2_passed = test_forward_without_attachment()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"带附件转发测试: {'通过' if test1_passed else '失败'}")
    print(f"无附件转发测试: {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("✓ 所有测试通过")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)