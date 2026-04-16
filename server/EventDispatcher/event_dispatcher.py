"""
EventDispatcher - 事件分发器
基于CSID路由请求到不同的处理器
"""

import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from protos import message_pb2 as pb2
from server.LoadIconManager import LoadIconManager


class EventDispatcher:
    """事件分发器 - 基于CSID路由请求到不同的处理器"""
    
    def __init__(self):
        self.handlers = {
            pb2.CSID.CSID_LOAD_ICON_REQ: self._handle_load_icon_req,
            pb2.CSID.CSID_AAC_DISPERSES_ICON_SEND: self._handle_aac_disperse_icon_send,
        }
        self.load_icon_manager = LoadIconManager()
        logging.info("事件分发器初始化完成")
    
    def dispatch(self, csid, request, context):
        """
        根据CSID分发请求到对应的处理器
        
        Args:
            csid: 请求类型ID
            request: 请求数据
            context: gRPC上下文
            
        Returns:
            响应数据
        """
        handler = self.handlers.get(csid)
        
        if handler is None:
            logging.error(f"❌ 未知CSID: {csid}")
            response = pb2.LoadIconRes()
            response.csid = pb2.CSID.CSID_LOAD_ICON_RES
            return response
        
        try:
            return handler(request, context)
        except Exception as e:
            logging.error(f"❌ 处理请求失败 (CSID={csid}): {e}", exc_info=True)
            response = pb2.LoadIconRes()
            response.csid = pb2.CSID.CSID_LOAD_ICON_RES
            return response
    
    def _handle_load_icon_req(self, request, context):
        """
        处理LoadIconReq - 从JPGDataset读取图片并返回
        
        Args:
            request: LoadIconReq请求
            context: gRPC上下文
            
        Returns:
            LoadIconRes响应
        """
        client_ip = self._get_client_ip(context)
        logging.info(f"📨 [{client_ip}] LoadIconReq - 请求{len(request.iconLabel)}个图标")
        
        return self.load_icon_manager.load_icons(list(request.iconLabel))
    
    def _handle_aac_disperse_icon_send(self, request, context):
        """
        处理AACDisperseIconSend - AAC图标发送请求
        
        Args:
            request: AACDisperseIconSend请求
            context: gRPC上下文
            
        Returns:
            AACDisperseIconToText响应
        """
        logging.info("📨 收到AAC图标发送请求")
        # 这里可以添加对AACDisperseIconSend的处理逻辑
        return pb2.AACDisperseIconToText(
            csid=pb2.CSID.CSID_AAC_DISPERSES_ICON_TO_TEXT,
            text="Processing...",
            textEmotion=pb2.AACTextEmotion(currentEmotion="neutral", GlobalEmotion="neutral"),
            predictIconLabel=pb2.AACPredictIconLabel(iconLabel="")
        )
    
    def _get_client_ip(self, context):
        """从上下文获取客户端IP"""
        peer = context.peer()
        if ':' in peer:
            return peer.split(':')[1]
        return peer
