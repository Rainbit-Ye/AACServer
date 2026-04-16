"""
AACClient - AAC gRPC客户端
用于连接和与AAC服务器通信
"""

import grpc
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from protos import message_pb2 as pb2
from protos import message_pb2_grpc as pb2_grpc


class AACClient:
    """AAC gRPC客户端"""
    
    def __init__(self, server_address='localhost:50051'):
        """
        初始化客户端
        
        Args:
            server_address: 服务器地址，格式为 "host:port"
        """
        self.server_address = server_address
        self.channel = None
        self.stub = None
        
    def connect(self):
        """连接到服务器"""
        try:
            self.channel = grpc.insecure_channel(self.server_address)
            self.stub = pb2_grpc.ServiceStub(self.channel)
            logging.info(f"已连接到服务器: {self.server_address}")
            return True
        except Exception as e:
            logging.error(f"连接服务器失败: {e}")
            return False
    
    def disconnect(self):
        """断开服务器连接"""
        if self.channel:
            self.channel.close()
            logging.info("已断开服务器连接")
    
    def check_connection(self):
        """检查服务器连接状态"""
        try:
            request = pb2.ConnectCheckRequest(msg="ping")
            response = self.stub.ConnectCheck(request)
            return response.connect
        except Exception as e:
            logging.error(f"检查连接失败: {e}")
            return False
    
    def load_icons(self, icon_labels):
        """
        加载图标
        
        Args:
            icon_labels: 图标标签列表
            
        Returns:
            LoadIconRes响应对象
        """
        try:
            request = pb2.LoadIconReq()
            request.csid = pb2.CSID.CSID_LOAD_ICON_REQ
            request.iconLabel.extend(icon_labels)
            
            response = self.stub.LoadIcon(request)
            return response
            
        except grpc.RpcError as e:
            logging.error(f"RPC错误: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            logging.error(f"加载图标失败: {e}")
            return None
    
    def __enter__(self):
        """支持上下文管理器"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.disconnect()
