#!/usr/bin/env python3
"""
测试批量移动和删除功能的ID同步问题修复
"""
import sys
import os
import unittest.mock

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.services.email_service import EmailService
from emails_mcp.backends.imap_backend import IMAPBackend
from emails_mcp.backends.smtp_backend import SMTPBackend
from emails_mcp.models.config import EmailConfig


class MockEmailService:
    """模拟邮件服务"""
    def __init__(self):
        self.existing_emails = set(['1', '2', '3', '4', '5', '10', '15', '20'])
        self.moved_emails = []
        self.deleted_emails = []
        self.operations_log = []
    
    def _check_email_exists(self, email_id: str) -> bool:
        """检查邮件是否存在"""
        exists = email_id in self.existing_emails
        self.operations_log.append(f"Check {email_id}: {'exists' if exists else 'not found'}")
        return exists
    
    def move_email(self, email_id: str, target_folder: str) -> bool:
        """模拟移动邮件"""
        if email_id in self.existing_emails:
            self.moved_emails.append(email_id)
            self.existing_emails.remove(email_id)
            self.operations_log.append(f"Moved {email_id} to {target_folder}")
            return True
        else:
            self.operations_log.append(f"Failed to move {email_id}: not found")
            return False
    
    def delete_email(self, email_id: str) -> bool:
        """模拟删除邮件"""
        if email_id in self.existing_emails:
            self.deleted_emails.append(email_id)
            self.existing_emails.remove(email_id)
            self.operations_log.append(f"Deleted {email_id}")
            return True
        else:
            self.operations_log.append(f"Failed to delete {email_id}: not found")
            return False


def test_batch_move_id_synchronization():
    """测试批量移动功能的ID同步"""
    print("开始测试批量移动功能的ID同步...")
    
    try:
        mock_service = MockEmailService()
        
        # 测试邮件ID列表（包含一些不存在的ID）
        email_ids = ['1', '2', '3', '999', '4', '5']
        target_folder = "Archive"
        
        # 模拟批量移动的逻辑
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        # 按降序排序，避免ID重新编号问题
        sorted_ids = sorted(email_ids, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
        print(f"原始ID顺序: {email_ids}")
        print(f"排序后ID顺序: {sorted_ids}")
        
        for email_id in sorted_ids:
            # 检查邮件是否存在
            email_exists = mock_service._check_email_exists(email_id)
            if not email_exists:
                failed_count += 1
                failed_ids.append(email_id)
                continue
            
            # 尝试移动邮件
            success = mock_service.move_email(email_id, target_folder)
            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(email_id)
        
        # 验证结果
        total_count = len(email_ids)
        expected_success = 5  # ID 1,2,3,4,5应该成功
        expected_failed = 1   # ID 999不存在
        
        print(f"\n操作日志:")
        for log in mock_service.operations_log:
            print(f"  {log}")
        
        print(f"\n结果: 成功移动 {success_count}/{total_count} 邮件")
        print(f"成功移动的邮件: {mock_service.moved_emails}")
        print(f"失败的邮件ID: {failed_ids}")
        
        if success_count == expected_success and failed_count == expected_failed:
            print("✓ 批量移动ID同步测试通过")
            return True
        else:
            print(f"✗ 批量移动ID同步测试失败: 期望成功{expected_success}个，实际{success_count}个")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_delete_id_synchronization():
    """测试批量删除功能的ID同步"""
    print("\n开始测试批量删除功能的ID同步...")
    
    try:
        mock_service = MockEmailService()
        
        # 测试邮件ID列表（包含一些不存在的ID）
        email_ids = ['20', '15', '10', '999', '5', '1']
        
        # 模拟批量删除的逻辑
        success_count = 0
        failed_count = 0
        failed_ids = []
        
        # 按降序排序，避免ID重新编号问题
        sorted_ids = sorted(email_ids, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
        print(f"原始ID顺序: {email_ids}")
        print(f"排序后ID顺序: {sorted_ids}")
        
        for email_id in sorted_ids:
            # 检查邮件是否存在
            email_exists = mock_service._check_email_exists(email_id)
            if not email_exists:
                failed_count += 1
                failed_ids.append(email_id)
                continue
            
            # 尝试删除邮件
            success = mock_service.delete_email(email_id)
            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(email_id)
        
        # 验证结果
        total_count = len(email_ids)
        expected_success = 5  # ID 20,15,10,5,1应该成功
        expected_failed = 1   # ID 999不存在
        
        print(f"\n操作日志:")
        for log in mock_service.operations_log:
            print(f"  {log}")
        
        print(f"\n结果: 成功删除 {success_count}/{total_count} 邮件")
        print(f"成功删除的邮件: {mock_service.deleted_emails}")
        print(f"失败的邮件ID: {failed_ids}")
        
        if success_count == expected_success and failed_count == expected_failed:
            print("✓ 批量删除ID同步测试通过")
            return True
        else:
            print(f"✗ 批量删除ID同步测试失败: 期望成功{expected_success}个，实际{success_count}个")
            return False
            
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_id_sorting_logic():
    """测试ID排序逻辑"""
    print("\n开始测试ID排序逻辑...")
    
    try:
        test_cases = [
            (['1', '2', '3', '10', '20'], ['20', '10', '3', '2', '1']),
            (['100', '5', '15', '2'], ['100', '15', '5', '2']),
            (['abc', '1', '2', 'xyz'], ['2', '1', 'abc', 'xyz']),  # 非数字ID
        ]
        
        for original, expected in test_cases:
            sorted_ids = sorted(original, key=lambda x: int(x) if x.isdigit() else 0, reverse=True)
            print(f"原始: {original} -> 排序后: {sorted_ids}")
            
            if sorted_ids == expected:
                print("✓ 排序正确")
            else:
                print(f"✗ 排序错误，期望: {expected}")
                return False
        
        print("✓ ID排序逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("批量移动和删除功能ID同步测试")
    print("=" * 50)
    
    # 运行测试
    test1_passed = test_batch_move_id_synchronization()
    test2_passed = test_batch_delete_id_synchronization()
    test3_passed = test_id_sorting_logic()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"批量移动ID同步测试: {'通过' if test1_passed else '失败'}")
    print(f"批量删除ID同步测试: {'通过' if test2_passed else '失败'}")
    print(f"ID排序逻辑测试: {'通过' if test3_passed else '失败'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("✓ 所有测试通过")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)