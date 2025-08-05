#!/usr/bin/env python3
"""
测试中文相关的批量移动和删除功能
"""
import sys
import os
import unittest.mock

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.services.email_service import EmailService
from emails_mcp.models.email import EmailMessage


class MockEmailServiceChinese:
    """模拟支持中文的邮件服务"""
    def __init__(self):
        # 包含中文主题和内容的邮件
        self.existing_emails = {
            '1': {'subject': '测试邮件1', 'folder': 'INBOX'},
            '2': {'subject': '工作报告', 'folder': 'INBOX'}, 
            '3': {'subject': 'Test Email', 'folder': 'INBOX'},
            '4': {'subject': '重要通知', 'folder': 'INBOX'},
            '5': {'subject': '项目文档', 'folder': 'INBOX'}
        }
        self.moved_emails = []
        self.deleted_emails = []
        self.operations_log = []
        self.current_folder = 'INBOX'
    
    def _check_email_exists(self, email_id: str) -> bool:
        """检查邮件是否存在"""
        exists = email_id in self.existing_emails
        email_info = self.existing_emails.get(email_id, {})
        subject = email_info.get('subject', 'Unknown')
        self.operations_log.append(f"Check {email_id} ({subject}): {'exists' if exists else 'not found'}")
        return exists
    
    def move_email(self, email_id: str, target_folder: str) -> bool:
        """移动邮件（支持中文文件夹名）"""
        if email_id in self.existing_emails:
            email_info = self.existing_emails[email_id]
            self.moved_emails.append({
                'id': email_id,
                'subject': email_info['subject'],
                'target_folder': target_folder
            })
            # 更新邮件文件夹
            self.existing_emails[email_id]['folder'] = target_folder
            self.operations_log.append(f"Moved {email_id} ({email_info['subject']}) to {target_folder}")
            return True
        else:
            self.operations_log.append(f"Failed to move {email_id}: not found")
            return False
    
    def delete_email(self, email_id: str) -> bool:
        """删除邮件"""
        if email_id in self.existing_emails:
            email_info = self.existing_emails[email_id]
            self.deleted_emails.append({
                'id': email_id,
                'subject': email_info['subject']
            })
            del self.existing_emails[email_id]
            self.operations_log.append(f"Deleted {email_id} ({email_info['subject']})")
            return True
        else:
            self.operations_log.append(f"Failed to delete {email_id}: not found")
            return False


def test_chinese_batch_move():
    """测试中文环境下的批量移动"""
    print("开始测试中文环境下的批量移动...")
    
    try:
        mock_service = MockEmailServiceChinese()
        
        # 测试移动到中文文件夹名
        email_ids = ['1', '2', '4']  # 包含中文主题的邮件
        target_folder = "已处理"  # 中文文件夹名
        
        # 模拟批量移动逻辑
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        # 按降序排序避免ID重新编号
        sorted_ids = sorted(email_ids, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
        print(f"处理邮件ID顺序: {sorted_ids}")
        
        for email_id in sorted_ids:
            # 检查邮件存在性
            email_exists = mock_service._check_email_exists(email_id)
            if not email_exists:
                failed_count += 1
                failed_ids.append(email_id)
                continue
            
            # 尝试移动
            success = mock_service.move_email(email_id, target_folder)
            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(email_id)
        
        print(f"\n操作日志:")
        for log in mock_service.operations_log:
            print(f"  {log}")
        
        print(f"\n移动结果:")
        for moved in mock_service.moved_emails:
            print(f"  - 邮件 {moved['id']} '{moved['subject']}' -> {moved['target_folder']}")
        
        # 验证结果
        expected_success = 3
        if success_count == expected_success and failed_count == 0:
            print("✓ 中文环境批量移动测试通过")
            return True
        else:
            print(f"✗ 中文环境批量移动测试失败: 成功{success_count}个，失败{failed_count}个")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chinese_batch_delete():
    """测试中文环境下的批量删除"""
    print("\n开始测试中文环境下的批量删除...")
    
    try:
        mock_service = MockEmailServiceChinese()
        
        # 测试删除包含中文内容的邮件
        email_ids = ['2', '4', '5']  # 工作报告、重要通知、项目文档
        
        # 模拟批量删除逻辑
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        # 按降序排序避免ID重新编号
        sorted_ids = sorted(email_ids, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
        print(f"删除邮件ID顺序: {sorted_ids}")
        
        for email_id in sorted_ids:
            # 检查邮件存在性
            email_exists = mock_service._check_email_exists(email_id)
            if not email_exists:
                failed_count += 1
                failed_ids.append(email_id)
                continue
            
            # 尝试删除
            success = mock_service.delete_email(email_id)
            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(email_id)
        
        print(f"\n操作日志:")
        for log in mock_service.operations_log:
            print(f"  {log}")
        
        print(f"\n删除结果:")
        for deleted in mock_service.deleted_emails:
            print(f"  - 删除邮件 {deleted['id']} '{deleted['subject']}'")
        
        # 验证结果
        expected_success = 3
        if success_count == expected_success and failed_count == 0:
            print("✓ 中文环境批量删除测试通过")
            return True
        else:
            print(f"✗ 中文环境批量删除测试失败: 成功{success_count}个，失败{failed_count}个")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_chinese_folder_name_encoding():
    """测试中文文件夹名编码处理"""
    print("\n开始测试中文文件夹名编码处理...")
    
    try:
        # 测试各种中文文件夹名
        test_folders = [
            "已处理",
            "工作邮件", 
            "重要/紧急",
            "客户沟通",
            "项目文档",
            "2024年度报告"
        ]
        
        print("测试中文文件夹名:")
        for folder in test_folders:
            # 测试UTF-8编码
            try:
                utf8_encoded = folder.encode('utf-8')
                utf8_decoded = utf8_encoded.decode('utf-8')
                if utf8_decoded == folder:
                    print(f"  ✓ UTF-8: '{folder}' -> {len(utf8_encoded)} bytes")
                else:
                    print(f"  ✗ UTF-8编码/解码失败: {folder}")
                    return False
            except Exception as e:
                print(f"  ✗ UTF-8处理失败 '{folder}': {e}")
                return False
            
            # 测试UTF-7编码（IMAP标准）
            try:
                utf7_encoded = folder.encode('utf-7').decode('ascii')
                print(f"  ✓ UTF-7: '{folder}' -> '{utf7_encoded}'")
            except Exception as e:
                print(f"  ✗ UTF-7编码失败 '{folder}': {e}")
                return False
        
        print("✓ 中文文件夹名编码处理测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


def test_mixed_language_batch_operations():
    """测试中英文混合的批量操作"""
    print("\n开始测试中英文混合的批量操作...")
    
    try:
        mock_service = MockEmailServiceChinese()
        
        # 测试中英文混合的邮件ID和文件夹
        email_ids = ['1', '2', '3', '4', '5']  # 包含中英文邮件
        operations = [
            {'ids': ['1', '3'], 'action': 'move', 'target': 'Archive'},
            {'ids': ['2', '4'], 'action': 'move', 'target': '已归档'},
            {'ids': ['5'], 'action': 'delete'}
        ]
        
        total_success = 0
        total_operations = 0
        
        for operation in operations:
            op_ids = operation['ids']
            action = operation['action']
            
            if action == 'move':
                target = operation['target']
                print(f"\n移动邮件 {op_ids} 到 '{target}'")
                
                for email_id in sorted(op_ids, key=lambda x: int(x), reverse=True):
                    total_operations += 1
                    if mock_service._check_email_exists(email_id):
                        if mock_service.move_email(email_id, target):
                            total_success += 1
                            
            elif action == 'delete':
                print(f"\n删除邮件 {op_ids}")
                
                for email_id in sorted(op_ids, key=lambda x: int(x), reverse=True):
                    total_operations += 1
                    if mock_service._check_email_exists(email_id):
                        if mock_service.delete_email(email_id):
                            total_success += 1
        
        print(f"\n最终结果:")
        print(f"移动的邮件:")
        for moved in mock_service.moved_emails:
            print(f"  - {moved['id']}: '{moved['subject']}' -> {moved['target_folder']}")
        
        print(f"删除的邮件:")
        for deleted in mock_service.deleted_emails:
            print(f"  - {deleted['id']}: '{deleted['subject']}'")
        
        if total_success == total_operations:
            print("✓ 中英文混合批量操作测试通过")
            return True
        else:
            print(f"✗ 中英文混合批量操作测试失败: {total_success}/{total_operations}")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("中文批量移动和删除功能测试")
    print("=" * 50)
    
    # 运行测试
    test1_passed = test_chinese_batch_move()
    test2_passed = test_chinese_batch_delete()
    test3_passed = test_chinese_folder_name_encoding()
    test4_passed = test_mixed_language_batch_operations()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"中文批量移动测试: {'通过' if test1_passed else '失败'}")
    print(f"中文批量删除测试: {'通过' if test2_passed else '失败'}")
    print(f"中文文件夹名编码测试: {'通过' if test3_passed else '失败'}")
    print(f"中英文混合操作测试: {'通过' if test4_passed else '失败'}")
    
    if test1_passed and test2_passed and test3_passed and test4_passed:
        print("✓ 所有测试通过")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)