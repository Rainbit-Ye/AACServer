"""
AACService - AAC gRPC服务
基于gRPC的AAC通信服务器
"""

import grpc
from concurrent import futures
import socket
import threading
import time
from datetime import datetime
import psutil
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from protos import message_pb2 as pb2
from protos import message_pb2_grpc as pb2_grpc
from server.EventDispatcher import EventDispatcher


class AACService(pb2_grpc.ServiceServicer):
    """AAC gRPC服务"""
    
    def __init__(self):
        self.request_count = 0
        self.start_time = datetime.now()
        self.active_connections = 0
        self.lock = threading.Lock()
        self.dispatcher = EventDispatcher()
        logging.info("AAC服务初始化完成")
        
    def ConnectCheck(self, request, context):
        """客户端连接检查 - 支持局域网连接"""
        with self.lock:
            self.active_connections += 1
        
        client_ip = self._get_client_ip(context)
        logging.info(f"🔗 客户端连接: {client_ip}")
        
        # 返回服务器信息和IP地址
        server_ip = self._get_server_ip()
        return pb2.ConnectCheckResponse(
            connect=True,
            result=pb2.RESULT.SUCCESS,
            errormsg=f"Connected to server at {server_ip}",
        )
    
    def LoadIcon(self, request, context):
        """使用事件分发器处理LoadIcon请求"""
        with self.lock:
            self.request_count += 1
            req_id = self.request_count
        
        client_ip = self._get_client_ip(context)
        logging.info(f"📨 [{client_ip}] 请求#{req_id}: LoadIcon (CSID={request.csid})")
        
        # 使用事件分发器处理请求
        return self.dispatcher.dispatch(request.csid, request, context)
    
    def ProcessAACMessage(self, request, context):
        """处理AAC消息 - 支持多设备并发"""
        logging.info("ProcessAACMessage 测试模式：返回测试成功消息")
        return pb2.AACDisperseIconToText(
            csid=pb2.CSID.CSID_AAC_DISPERSES_ICON_TO_TEXT,
            text="测试成功",
            textEmotion=pb2.AACTextEmotion(currentEmotion="neutral", GlobalEmotion="neutral"),
            predictIconLabel=pb2.AACPredictIconLabel(iconLabel="")
        )
    
    def _get_client_ip(self, context):
        """从上下文获取客户端IP"""
        peer = context.peer()
        if ':' in peer:
            return peer.split(':')[1]
        return peer
    
    def _get_server_ip(self):
        """获取服务器IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"


class AACServer:
    """AAC gRPC服务器管理类"""
    
    def __init__(self, host='0.0.0.0', port=50051):
        """
        初始化服务器
        
        Args:
            host: 监听主机地址
            port: 监听端口
        """
        self.host = host
        self.port = port
        self.service = AACService()
        self.server = None
    
    def start(self):
        """启动服务器"""
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler('aac_server_lan.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        # 打印网络信息
        self._print_network_info()
        
        # 创建gRPC服务器
        self.server = grpc.server(
            futures.ThreadPoolExecutor(
                max_workers=50,
                thread_name_prefix="aac_worker"
            ),
            options=[
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_concurrent_streams', 100),
                ('grpc.http2.max_ping_strikes', 0),
                ('grpc.keepalive_time_ms', 30000),
                ('grpc.keepalive_timeout_ms', 10000),
                ('grpc.keepalive_permit_without_calls', True),
            ]
        )
        
        # 注册服务
        pb2_grpc.add_ServiceServicer_to_server(self.service, self.server)
        
        # 绑定端口
        server_address = f'{self.host}:{self.port}'
        self.server.add_insecure_port(server_address)
        
        logging.info(f"🚀 启动gRPC服务器: {server_address}")
        
        try:
            # 启动服务器
            self.server.start()
            
            # 启动状态监控线程
            status_thread = threading.Thread(target=self._monitor_status, daemon=True)
            status_thread.start()
            
            # 保持服务器运行
            self.server.wait_for_termination()
            
        except KeyboardInterrupt:
            logging.info("⏹️  接收到停止信号，正在关闭服务器...")
            self.stop()
        except Exception as e:
            logging.error(f"❌ 服务器启动失败: {e}", exc_info=True)
            raise
    
    def stop(self):
        """停止服务器"""
        if self.server:
            self.server.stop(grace=5)
            logging.info("✅ 服务器已停止")
    
    def _monitor_status(self):
        """定期记录系统状态"""
        while True:
            time.sleep(60)
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory()
            logging.info(f"📊 系统状态: CPU={cpu}%, 内存={mem.percent}%, 连接数={self.service.active_connections}")
    
    def _print_network_info(self):
        """打印网络连接信息"""
        print("═" * 60)
        print("🏆 AAC gRPC 服务器 - 局域网部署版")
        print("═" * 60)
        
        # 获取本机IP
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
        except:
            local_ip = "127.0.0.1"
        
        # 显示所有网络接口
        print("📡 网络接口信息:")
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                        print(f"   {interface}: {addr.address}")
        except:
            pass
        
        print("\n🔌 连接方式:")
        print(f"  🌐 本机测试:   grpc://localhost:{self.port}")
        print(f"  💻 本机访问:   grpc://{local_ip}:{self.port}")
        print(f"  🌍 局域网访问: grpc://<您的IP>:{self.port}")
        print(f"  📊 监听端口:   {self.host}:{self.port}")
        
        print("\n📋 示例客户端连接命令:")
        print(f"  Python客户端: AACClient('{local_ip}:{self.port}')")
        print(f"  gRPCurl测试:  grpcurl -plaintext {local_ip}:{self.port} list")
        
        print("\n⚠️  确保防火墙已允许端口 50051/TCP")
        print("═" * 60)
        print("按 Ctrl+C 停止服务器")
        print("═" * 60)


if __name__ == '__main__':
    server = AACServer()
    server.start()
