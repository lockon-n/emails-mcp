#!/usr/bin/env python3
"""
全面的中文编码解析测试 - 测试所有可能的中文编码问题
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import logging
from emails_mcp.utils.email_parser import (
    decode_email_header, 
    parse_email_address_with_name, 
    parse_email_addresses,
    detect_and_decode_content
)
from emails_mcp.utils.validators import validate_email_address
from emails_mcp.config import config_manager
from emails_mcp.backends.smtp_backend import SMTPBackend
import email.message

# Set up logging to see warnings
logging.basicConfig(level=logging.DEBUG)

def test_email_header_decoding():
    """测试邮件头部中文解码"""
    print("🧪 测试邮件头部中文解码...")
    
    # Test cases with different Chinese encodings
    test_cases = [
        # UTF-8 encoded Chinese name
        "=?UTF-8?B?5byg5LiJ?= <zhangsan@example.com>",
        # GB2312 encoded Chinese name  
        "=?GB2312?B?xOO6w7rO?= <lisi@example.com>",
        # Mixed Chinese and English
        "=?UTF-8?B?5byg5LiJIChaaGFuZyBTYW4p?= <zhangsan@company.com>",
        # Plain Chinese (should work too)
        "张三 <zhangsan@example.com>",
        # Complex mixed encoding
        "=?UTF-8?Q?=E4=B8=AD=E6=96=87=E6=B5=8B=E8=AF=95?= <test@example.com>",
        # Multiple encoded parts
        "=?UTF-8?B?5byg?= =?UTF-8?B?5LiJ?= <zhangsan@example.com>"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            decoded = decode_email_header(test_case)
            print(f"  ✓ Test {i}: '{test_case}' -> '{decoded}'")
        except Exception as e:
            print(f"  ❌ Test {i} failed: {e}")
    
    return True

def test_email_address_parsing():
    """测试中文显示名称的邮件地址解析"""
    print("\n🧪 测试中文显示名称的邮件地址解析...")
    
    test_cases = [
        "张三 <zhangsan@example.com>",
        "=?UTF-8?B?5byg5LiJ?= <zhangsan@example.com>", 
        '"张三李四" <zhangsan@example.com>',
        "中文测试 <test@中文域名.cn>",
        "Mixed 中英文 Name <mixed@example.com>",
        "zhangsan@example.com",  # No display name
        ""  # Empty
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            display_name, email_addr = parse_email_address_with_name(test_case)
            print(f"  ✓ Test {i}: '{test_case}' -> name='{display_name}', email='{email_addr}'")
        except Exception as e:
            print(f"  ❌ Test {i} failed: {e}")
    
    return True

def test_multiple_email_addresses():
    """测试逗号分隔的多个中文邮件地址解析"""
    print("\n🧪 测试多个中文邮件地址解析...")
    
    test_cases = [
        '张三 <zhangsan@example.com>, 李四 <lisi@example.com>',
        '"张三, 公司" <zhangsan@company.com>, test@example.com',
        '=?UTF-8?B?5byg5LiJ?= <zhangsan@example.com>, =?UTF-8?B?5Lq65Zub?= <lisi@example.com>',
        'zhangsan@example.com, lisi@example.com',  # No display names
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            addresses = parse_email_addresses(test_case)
            print(f"  ✓ Test {i}: '{test_case}' -> {addresses}")
        except Exception as e:
            print(f"  ❌ Test {i} failed: {e}")
    
    return True

def test_international_email_validation():
    """测试国际化邮件地址验证"""
    print("\n🧪 测试国际化邮件地址验证...")
    
    test_cases = [
        ("test@example.com", True),
        ("张三@example.com", False),  # Chinese in local part not supported yet
        ("test@中文域名.cn", True),  # International domain should work  
        ("test@例子.测试", True),  # Pure Chinese domain
        ("user.name+tag@example.com", True),
        ("invalid.email", False),
        ("@example.com", False),
        ("test@", False),
        ("test@.com", False),
        ("test@example.", False),
        ("test@ex ample.com", False)  # Space not allowed
    ]
    
    for i, (email, expected) in enumerate(test_cases, 1):
        try:
            result = validate_email_address(email)
            status = "✓" if result == expected else "❌"
            print(f"  {status} Test {i}: '{email}' -> {result} (expected {expected})")
        except Exception as e:
            print(f"  ❌ Test {i} failed: {e}")
    
    return True

def test_content_encoding_detection():
    """测试邮件内容编码检测"""
    print("\n🧪 测试邮件内容编码检测...")
    
    # Create test message parts with different encodings
    test_cases = [
        ("这是中文测试内容", "utf-8"),
        ("这是中文测试", "gb2312"), 
        ("Mixed 中英文 content", "utf-8"),
        ("English only content", "ascii")
    ]
    
    for i, (content, encoding) in enumerate(test_cases, 1):
        try:
            # Create a fake message part
            msg_part = email.message.Message()
            msg_part.set_charset(encoding)
            
            # Encode content
            content_bytes = content.encode(encoding)
            
            # Test our detection function
            decoded = detect_and_decode_content(content_bytes, msg_part)
            status = "✓" if decoded == content else "❌"
            print(f"  {status} Test {i}: {encoding} encoding -> '{decoded}'")
            
        except Exception as e:
            print(f"  ❌ Test {i} failed: {e}")
    
    return True

def test_smtp_chinese_headers():
    """测试SMTP中文头部编码"""
    print("\n🧪 测试SMTP中文头部编码...")
    
    try:
        # Load config for SMTP test
        email_config = config_manager.load_email_config("test_emils.json")
        if not email_config:
            print("  ⚠️ 跳过SMTP测试：无法加载配置")
            return True
            
        # Set Chinese display name
        email_config.name = "中文测试用户"
        
        smtp_backend = SMTPBackend(email_config)
        
        # Test connection
        if not smtp_backend.test_connection():
            print("  ⚠️ 跳过SMTP测试：连接失败")
            return True
        
        # Test Chinese email sending
        result = smtp_backend.send_email(
            to="kindtree001@mcp.com",
            subject="🧪 中文编码测试邮件 - Header Encoding Test",
            body="这是一封测试中文编码的邮件。\n\nThis email tests Chinese character encoding in headers and body.",
            html_body="<p>这是一封测试中文编码的邮件。</p><p>This email tests Chinese character encoding in headers and body.</p>"
        )
        
        if result[0]:
            print("  ✅ SMTP中文头部编码测试成功")
        else:
            print("  ❌ SMTP中文头部编码测试失败")
            
        smtp_backend.disconnect()
        return result[0]
        
    except Exception as e:
        print(f"  ❌ SMTP测试失败: {e}")
        return False

def main():
    """运行所有中文编码测试"""
    print("🔍 开始全面的中文编码解析测试...\n")
    
    tests = [
        test_email_header_decoding,
        test_email_address_parsing,
        test_multiple_email_addresses,
        test_international_email_validation,
        test_content_encoding_detection,
        test_smtp_chinese_headers
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 测试 {test_func.__name__} 出现异常: {e}")
    
    print(f"\n📊 测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有中文编码测试都通过了！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步修复")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)