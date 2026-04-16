"""
LoadIconClientTest - LoadIcon功能测试客户端
测试图标加载功能
"""

import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from client import AACClient


def test_load_icon():
    """测试LoadIcon功能"""
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    print("=" * 60)
    print("LoadIcon 功能测试")
    print("=" * 60)
    
    # 测试图标标签
    test_labels = [
        "Alphabet/A.jpg",  # 具体文件路径
        "Alphabet",        # 目录名
        "winner",          # 文件名
        "winter",          # 文件名
        "yorkshire_pudding",  # 带下划线的文件名
        "InvalidPath"      # 不存在的路径，测试错误处理
    ]
    
    print("\n测试图标标签:")
    for label in test_labels:
        print(f"  - {label}")
    
    # 使用上下文管理器连接客户端
    with AACClient('localhost:50051') as client:
        
        # 检查连接
        print("\n检查服务器连接...")
        if not client.check_connection():
            print("❌ 服务器连接失败")
            return
        
        print("✅ 服务器连接成功")
        
        # 发送LoadIcon请求
        print("\n发送LoadIcon请求...")
        response = client.load_icons(test_labels)
        
        if not response:
            print("❌ 请求失败")
            return
        
        # 显示响应结果
        print("\n" + "=" * 60)
        print("收到响应:")
        print(f"  CSID: {response.csid}")
        print(f"  加载的图标数量: {len(response.iconLabel)}")
        print(f"  图片数据数量: {len(response.imageData)}")
        
        print("\n加载的图标详情:")
        for i, label in enumerate(response.iconLabel):
            data_size = len(response.imageData[i]) if i < len(response.imageData) else 0
            print(f"  [{i+1}] {label} - {data_size} bytes")
        
        # 统计信息
        print(f"\n统计:")
        print(f"  请求总数: {len(test_labels)}")
        print(f"  成功加载: {len(response.iconLabel)}")
        print(f"  加载失败: {len(test_labels) - len(response.iconLabel)}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == '__main__':
    test_load_icon()
