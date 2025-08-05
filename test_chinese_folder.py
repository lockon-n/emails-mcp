#!/usr/bin/env python3
"""
测试中文文件夹名创建功能
"""
import sys
import os
import unittest.mock

# 添加src路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from emails_mcp.services.folder_service import FolderService
from emails_mcp.backends.imap_backend import IMAPBackend
from emails_mcp.models.config import EmailConfig
from emails_mcp.utils.exceptions import FolderError


class MockIMAPConnection:
    """模拟IMAP连接"""
    def __init__(self, utf8_enabled=False, should_succeed=True):
        self.utf8_enabled = utf8_enabled
        self.should_succeed = should_succeed
        self.created_folders = []
    
    def create(self, folder_name):
        """模拟创建文件夹"""
        self.created_folders.append(folder_name)
        if self.should_succeed:
            return ('OK', b'CREATE completed')
        else:
            return ('NO', b'CREATE failed')


def test_chinese_folder_creation():
    """测试创建中文文件夹名"""
    print("开始测试中文文件夹名创建功能...")
    
    try:
        # 创建模拟配置
        config = EmailConfig(
            email="test@example.com",
            password="password",
            imap_server="imap.example.com",
            smtp_server="smtp.example.com"
        )
        
        # 测试用例1: UTF-8支持的服务器
        print("\n1. 测试UTF-8支持的服务器...")
        mock_connection_utf8 = MockIMAPConnection(utf8_enabled=True, should_succeed=True)
        
        with unittest.mock.patch('emails_mcp.backends.imap_backend.IMAPBackend') as mock_backend:
            mock_backend_instance = mock_backend.return_value
            mock_backend_instance.ensure_connected.return_value = None
            mock_backend_instance.connection = mock_connection_utf8
            mock_backend_instance.utf8_enabled = True
            
            folder_service = FolderService(mock_backend_instance)
            
            # 测试创建中文文件夹
            chinese_folder = "测试文件夹"
            success = folder_service.create_folder(chinese_folder)
            
            if success and chinese_folder in mock_connection_utf8.created_folders:
                print(f"✓ UTF-8服务器成功创建中文文件夹: {chinese_folder}")
            else:
                print(f"✗ UTF-8服务器创建中文文件夹失败")
                return False
        
        # 测试用例2: 不支持UTF-8的服务器
        print("\n2. 测试不支持UTF-8的服务器...")
        mock_connection_no_utf8 = MockIMAPConnection(utf8_enabled=False, should_succeed=True)
        
        with unittest.mock.patch('emails_mcp.backends.imap_backend.IMAPBackend') as mock_backend:
            mock_backend_instance = mock_backend.return_value
            mock_backend_instance.ensure_connected.return_value = None
            mock_backend_instance.connection = mock_connection_no_utf8
            mock_backend_instance.utf8_enabled = False
            
            folder_service = FolderService(mock_backend_instance)
            
            # 测试创建中文文件夹
            chinese_folder = "中文目录"
            success = folder_service.create_folder(chinese_folder)
            
            if success:
                print(f"✓ 非UTF-8服务器成功创建中文文件夹: {chinese_folder}")
                # 检查是否尝试了UTF-7编码
                utf7_encoded = chinese_folder.encode('utf-7').decode('ascii')
                if utf7_encoded in mock_connection_no_utf8.created_folders:
                    print(f"✓ 使用UTF-7编码: {utf7_encoded}")
            else:
                print(f"✗ 非UTF-8服务器创建中文文件夹失败")
                return False
        
        # 测试用例3: 英文文件夹名
        print("\n3. 测试英文文件夹名...")
        mock_connection_english = MockIMAPConnection(utf8_enabled=True, should_succeed=True)
        
        with unittest.mock.patch('emails_mcp.backends.imap_backend.IMAPBackend') as mock_backend:
            mock_backend_instance = mock_backend.return_value
            mock_backend_instance.ensure_connected.return_value = None
            mock_backend_instance.connection = mock_connection_english
            mock_backend_instance.utf8_enabled = True
            
            folder_service = FolderService(mock_backend_instance)
            
            # 测试创建英文文件夹
            english_folder = "TestFolder"
            success = folder_service.create_folder(english_folder)
            
            if success and english_folder in mock_connection_english.created_folders:
                print(f"✓ 成功创建英文文件夹: {english_folder}")
            else:
                print(f"✗ 创建英文文件夹失败")
                return False
        
        print("\n✓ 中文文件夹名创建功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_encoding_methods():
    """测试不同编码方法"""
    print("\n开始测试编码方法...")
    
    try:
        test_folders = [
            "测试",
            "中文文件夹",
            "工作目录",
            "项目文档"
        ]
        
        for folder in test_folders:
            # UTF-7编码测试
            try:
                utf7_encoded = folder.encode('utf-7').decode('ascii')
                print(f"✓ UTF-7编码 '{folder}' -> '{utf7_encoded}'")
            except Exception as e:
                print(f"✗ UTF-7编码失败 '{folder}': {e}")
                return False
            
            # UTF-8编码测试
            try:
                utf8_encoded = folder.encode('utf-8')
                print(f"✓ UTF-8编码 '{folder}' -> {len(utf8_encoded)} bytes")
            except Exception as e:
                print(f"✗ UTF-8编码失败 '{folder}': {e}")
                return False
        
        print("✓ 编码方法测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 编码方法测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    print("中文文件夹名创建功能测试")
    print("=" * 50)
    
    # 运行测试
    test1_passed = test_chinese_folder_creation()
    test2_passed = test_encoding_methods()
    
    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"中文文件夹创建测试: {'通过' if test1_passed else '失败'}")
    print(f"编码方法测试: {'通过' if test2_passed else '失败'}")
    
    if test1_passed and test2_passed:
        print("✓ 所有测试通过")
        sys.exit(0)
    else:
        print("✗ 部分测试失败")
        sys.exit(1)