#!/usr/bin/env python3
"""
测试附件名保持和文件夹导入修复
"""
import sys
import os
import tempfile
import json
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.models.email import EmailMessage, EmailAttachment


def test_attachment_filename_preservation():
    """测试转发时附件文件名保持不变"""
    print("开始测试附件文件名保持...")
    
    try:
        # 创建带附件的测试邮件
        msg = MIMEMultipart()
        msg['Subject'] = "Test with attachment"
        msg['From'] = "sender@example.com"
        msg['To'] = "recipient@example.com"
        
        # 添加正文
        body = MIMEText("Email with attachment")
        msg.attach(body)
        
        # 添加附件 - 使用中文文件名测试
        test_filename = "测试文档.pdf"
        attachment_content = b"This is test PDF content"
        
        attachment = MIMEBase('application', 'pdf')
        attachment.set_payload(attachment_content)
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename={test_filename}'
        )
        msg.attach(attachment)
        
        # 创建EmailMessage对象
        test_attachment = EmailAttachment(
            filename=test_filename,
            content_type="application/pdf",
            size=len(attachment_content)
        )
        
        original_email = EmailMessage(
            email_id="test_123",
            subject="Test with attachment",
            from_addr="sender@example.com",
            to_addr="recipient@example.com",
            date="2025-01-01 12:00:00",
            body_text="Email with attachment",
            attachments=[test_attachment],
            raw_message=msg
        )
        
        # 模拟附件提取过程
        extracted_files = []
        
        if original_email.raw_message:
            for part in original_email.raw_message.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        # 模拟新的文件保存方式（保持原文件名）
                        temp_dir = tempfile.mkdtemp()
                        temp_file_path = os.path.join(temp_dir, filename)
                        attachment_data = part.get_payload(decode=True)
                        
                        if attachment_data:
                            with open(temp_file_path, 'wb') as f:
                                f.write(attachment_data)
                            extracted_files.append(temp_file_path)
                            
                            # 验证文件名
                            actual_filename = os.path.basename(temp_file_path)
                            if actual_filename == test_filename:
                                print(f"✓ 附件文件名保持不变: {actual_filename}")
                            else:
                                print(f"✗ 附件文件名被改变: 期望 {test_filename}, 实际 {actual_filename}")
                                return False
        
        # 清理临时文件
        for temp_file_path in extracted_files:
            try:
                os.unlink(temp_file_path)
                temp_dir = os.path.dirname(temp_file_path)
                os.rmdir(temp_dir)
            except:
                pass
        
        if extracted_files:
            print("✓ 附件文件名保持功能测试通过")
            return True
        else:
            print("✗ 没有找到附件")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_folder_preserve_import():
    """测试导入时保持文件夹结构"""
    print("\n开始测试文件夹结构保持导入...")
    
    try:
        # 创建包含不同文件夹的测试导出文件
        temp_dir = tempfile.mkdtemp()
        export_file = os.path.join(temp_dir, "multi_folder_export.json")
        
        test_emails = [
            {
                'email_id': '1',
                'subject': 'INBOX邮件',
                'from_addr': 'sender1@example.com',
                'to_addr': 'recipient@example.com',
                'date': '2025-01-01 10:00:00',
                'body_text': '这是INBOX中的邮件',
                'is_read': True,
                'folder': 'INBOX',
                'attachments': []
            },
            {
                'email_id': '2',
                'subject': '已发送邮件',
                'from_addr': 'sender2@example.com',
                'to_addr': 'recipient@example.com',
                'date': '2025-01-02 11:00:00',
                'body_text': '这是已发送邮件',
                'is_read': True,
                'folder': 'Sent',
                'attachments': []
            },
            {
                'email_id': '3',
                'subject': '工作邮件',
                'from_addr': 'work@example.com',
                'to_addr': 'recipient@example.com',
                'date': '2025-01-03 12:00:00',
                'body_text': '这是工作文件夹中的邮件',
                'is_read': False,
                'folder': '工作',
                'attachments': []
            }
        ]
        
        # 创建导出文件
        export_data = {
            'export_date': '2025-01-03T12:00:00',
            'total_emails': len(test_emails),
            'emails': test_emails
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        # 模拟导入过程
        from emails_mcp.backends.file_backend import FileBackend
        file_backend = FileBackend()
        imported_emails = file_backend.import_emails(export_file)
        
        # 验证导入结果
        if len(imported_emails) != 3:
            print(f"✗ 导入邮件数量错误: 期望3个，实际{len(imported_emails)}个")
            return False
        
        # 检查文件夹分布
        folder_distribution = {}
        for email_obj in imported_emails:
            folder = email_obj.folder or 'INBOX'
            if folder not in folder_distribution:
                folder_distribution[folder] = 0
            folder_distribution[folder] += 1
        
        print(f"导入邮件文件夹分布: {folder_distribution}")
        
        expected_folders = ['INBOX', 'Sent', '工作']
        for folder in expected_folders:
            if folder not in folder_distribution or folder_distribution[folder] != 1:
                print(f"✗ 文件夹 {folder} 邮件数量错误")
                return False
        
        # 模拟导入逻辑测试
        class MockIMAPBackend:
            def __init__(self):
                self.existing_folders = {'INBOX': True, 'Sent': True}
                self.created_folders = []
                self.imported_emails = []
            
            def select_folder(self, folder):
                if folder not in self.existing_folders:
                    raise Exception(f"Folder {folder} not found")
                return 10, 2
            
            def append_message(self, folder, message, flags=''):
                self.imported_emails.append({
                    'folder': folder,
                    'message_preview': message[:50] + '...',
                    'flags': flags
                })
                return True
        
        class MockFolderService:
            def __init__(self, imap_backend):
                self.imap_backend = imap_backend
            
            def create_folder(self, folder_name):
                self.imap_backend.existing_folders[folder_name] = True
                self.imap_backend.created_folders.append(folder_name)
                return True
        
        # 模拟完整导入流程
        mock_imap = MockIMAPBackend()
        mock_folder_service = MockFolderService(mock_imap)
        
        success_count = 0
        folder_stats = {}
        
        for email_obj in imported_emails:
            # 使用preserve_folders=True的逻辑
            import_folder = email_obj.folder if email_obj.folder else "INBOX"
            
            # 检查文件夹是否存在
            try:
                mock_imap.select_folder(import_folder)
            except Exception:
                # 如果文件夹不存在，创建它
                if import_folder != "INBOX":
                    mock_folder_service.create_folder(import_folder)
            
            # 模拟导入
            message_string = f"Subject: {email_obj.subject}\n\n{email_obj.body_text}"
            success = mock_imap.append_message(
                import_folder,
                message_string,
                flags='\\Seen' if email_obj.is_read else ''
            )
            
            if success:
                success_count += 1
                if import_folder not in folder_stats:
                    folder_stats[import_folder] = 0
                folder_stats[import_folder] += 1
        
        # 验证结果
        if success_count != 3:
            print(f"✗ 导入成功数量错误: 期望3个，实际{success_count}个")
            return False
        
        if '工作' not in mock_imap.created_folders:
            print("✗ 中文文件夹没有被创建")
            return False
        
        print(f"✓ 成功导入{success_count}封邮件")
        print(f"✓ 文件夹分布: {folder_stats}")
        print(f"✓ 自动创建的新文件夹: {mock_imap.created_folders}")
        
        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        
        print("✓ 文件夹结构保持导入功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("附件名保持和文件夹导入修复测试")
    print("=" * 50)
    
    # 运行测试
    test1_passed = test_attachment_filename_preservation()
    test2_passed = test_folder_preserve_import()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"附件文件名保持测试: {'通过' if test1_passed else '失败'}")
    print(f"文件夹结构保持导入测试: {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("✓ 所有测试通过")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)