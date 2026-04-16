"""
启动AAC服务器
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server.aac_server import AACServer

if __name__ == '__main__':
    server = AACServer()
    server.start()
