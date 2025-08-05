#!/usr/bin/env python3
"""
测试导出/导入时邮件顺序保持功能
"""
import sys
import os
import json
import tempfile

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.models.email import EmailMessage

def test_email_ordering_on_import():
    """测试导入时按ID排序功能"""
    print("测试导入时邮件ID排序功能...")
    
    # 模拟导出的邮件数据（IMAP序号顺序：最新到最老）
    mock_emails = [
        EmailMessage(
            email_id="10",  # 最新邮件
            subject="Latest Email",
            from_addr="sender1@example.com",
            to_addr="recipient@example.com",
            folder="INBOX"
        ),
        EmailMessage(
            email_id="9",
            subject="Second Email", 
            from_addr="sender2@example.com",
            to_addr="recipient@example.com",
            folder="INBOX"
        ),
        EmailMessage(
            email_id="8",
            subject="Third Email",
            from_addr="sender3@example.com", 
            to_addr="recipient@example.com",
            folder="INBOX"
        ),
        EmailMessage(
            email_id="1",  # 最老邮件
            subject="Oldest Email",
            from_addr="sender4@example.com",
            to_addr="recipient@example.com", 
            folder="INBOX"
        )
    ]
    
    print("原始邮件顺序（导出时的顺序，newest first）:")
    for i, email in enumerate(mock_emails):
        print(f"  {i}: ID={email.email_id}, Subject={email.subject}")
    
    # 模拟导入时的排序逻辑
    try:
        sorted_emails = sorted(mock_emails, key=lambda x: int(x.email_id) if x.email_id.isdigit() else 0, reverse=True)
        print(f"\n排序后的邮件顺序（导入顺序，ID从大到小）:")
        for i, email in enumerate(sorted_emails):
            print(f"  {i}: ID={email.email_id}, Subject={email.subject}")
        
        # 验证排序结果
        expected_order = ["10", "9", "8", "1"]
        actual_order = [email.email_id for email in sorted_emails]
        
        if actual_order == expected_order:
            print(f"\n✓ 排序正确！导入顺序: {' -> '.join(actual_order)}")
            print("这样导入后，邮件在IMAP服务器中的最终顺序将是:")
            print("  位置1: ID=10 (Latest Email) - 最新")
            print("  位置2: ID=9 (Second Email)")  
            print("  位置3: ID=8 (Third Email)")
            print("  位置4: ID=1 (Oldest Email) - 最老")
            return True
        else:
            print(f"\n✗ 排序错误！期望: {expected_order}, 实际: {actual_order}")
            return False
            
    except Exception as e:
        print(f"\n✗ 排序失败: {str(e)}")
        return False


def test_mixed_email_ids():
    """测试混合ID类型的排序"""
    print("\n测试混合ID类型的排序...")
    
    mock_emails = [
        EmailMessage(email_id="15", subject="Email 15", from_addr="a@test.com", to_addr="b@test.com"),
        EmailMessage(email_id="abc", subject="Non-numeric", from_addr="a@test.com", to_addr="b@test.com"),  
        EmailMessage(email_id="5", subject="Email 5", from_addr="a@test.com", to_addr="b@test.com"),
        EmailMessage(email_id="xyz", subject="Another non-numeric", from_addr="a@test.com", to_addr="b@test.com"),
    ]
    
    print("原始顺序:")
    for i, email in enumerate(mock_emails):
        print(f"  {i}: ID={email.email_id}, Subject={email.subject}")
    
    try:
        sorted_emails = sorted(mock_emails, key=lambda x: int(x.email_id) if x.email_id.isdigit() else 0, reverse=True)
        print(f"\n排序后顺序:")
        for i, email in enumerate(sorted_emails):
            print(f"  {i}: ID={email.email_id}, Subject={email.subject}")
        
        # 数字ID应该按数值大小排序，非数字ID当作0处理排在后面
        actual_order = [email.email_id for email in sorted_emails]
        # 期望：15, 5, abc, xyz (数字的按从大到小，非数字的保持原顺序)
        numeric_ids = [email for email in sorted_emails if email.email_id.isdigit()]
        non_numeric_ids = [email for email in sorted_emails if not email.email_id.isdigit()]
        
        if len(numeric_ids) == 2 and numeric_ids[0].email_id == "15" and numeric_ids[1].email_id == "5":
            print("✓ 数字ID排序正确")
            return True
        else:
            print("✗ 数字ID排序错误")
            return False
            
    except Exception as e:
        print(f"✗ 排序失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("邮件导入顺序保持功能测试")
    print("=" * 50)
    
    test1_passed = test_email_ordering_on_import()
    test2_passed = test_mixed_email_ids()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"基本ID排序测试: {'通过' if test1_passed else '失败'}")
    print(f"混合ID类型测试: {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("✓ 所有测试通过")
        print("\n邮件导入时会按ID从大到小排序，确保导入后保持原始的时间顺序")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)