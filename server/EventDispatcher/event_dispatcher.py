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

        # 初始化 AAC Emotion Pipeline（延迟加载）
        self._pipeline = None
        self._pipeline_lock = __import__('threading').Lock()

        logging.info("事件分发器初始化完成")

    def _get_pipeline(self):
        """延迟加载 AAC Emotion Pipeline（线程安全）"""
        if self._pipeline is not None:
            return self._pipeline

        with self._pipeline_lock:
            if self._pipeline is not None:
                return self._pipeline

            # 添加 EmotionClassify 到 sys.path
            emotion_classify_path = "/home/user1/liuduanye/EmotionClassify"
            if emotion_classify_path not in sys.path:
                sys.path.insert(0, emotion_classify_path)

            from aac_emotion_pipeline import AACEmotionPipeline

            logging.info("正在加载 AAC Emotion Pipeline 模型...")

            self._pipeline = AACEmotionPipeline(
                aac_model_path="/home/user1/liuduanye/EmotionClassify/AAC2Text/checkpoints/aac_model",
                aac_base_model_path="/home/user1/liuduanye/qwen/Qwen2_5-1_5B-Instruct",
                emotion_model_path="/home/user1/liuduanye/EmotionClassify/output/cls_final",
                emotion_base_model_path="/home/user1/liuduanye/EmotionClassify/Model/roberta-base",
                device="cuda"
            )

            logging.info("AAC Emotion Pipeline 模型加载完成")
            return self._pipeline

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
        处理AACDisperseIconSend - 客户端发送离散图标，返回翻译文本+情感+预测图标

        客户端传入: repeated string iconLabel (离散AAC图标标签列表)
        返回: AACDisperseIconToText
            - text: 翻译后的自然语言句子
            - textEmotion.currentEmotion: 当前轮情感
            - textEmotion.GlobalEmotion: 全局/主题情感
            - predictIconLabel.iconLabel: 预测的下一个图标标签(逗号分隔)

        Args:
            request: AACDisperseIconSend请求
            context: gRPC上下文

        Returns:
            AACDisperseIconToText响应
        """
        client_ip = self._get_client_ip(context)
        icon_labels = list(request.iconLabel)
        logging.info(f"📨 [{client_ip}] AACDisperseIconSend - 收到{len(icon_labels)}个图标: {icon_labels}")

        try:
            pipeline = self._get_pipeline()

            # 调用 Pipeline: icon labels -> 翻译 + 情感 + 预测
            result = pipeline.process(icon_labels)

            # 提取结果
            text = result['translation']['sentence']
            current_emotion = result['emotion']['current']
            theme_emotion = result['emotion']['theme']
            next_emotion = result['prediction']['next_emotion']

            # 构建预测图标标签: 从 icon_recommendations 中提取推荐的下一个图标
            # 按优先级: actions > entities > emotions > combinations
            predicted_labels = []
            icon_recs = result.get('icon_recommendations', {})

            for category in ['actions', 'entities', 'emotions', 'combinations']:
                for item in icon_recs.get(category, [])[:2]:  # 每类取前2个
                    label = item.get('label', '')
                    if label and label not in predicted_labels:
                        predicted_labels.append(label)

            predict_icon_str = ','.join(predicted_labels[:5])  # 最多5个

            logging.info(
                f"✅ [{client_ip}] Pipeline结果: "
                f"text='{text}', "
                f"current='{current_emotion}', "
                f"theme='{theme_emotion}', "
                f"next='{next_emotion}', "
                f"predict_icons='{predict_icon_str}'"
            )

            return pb2.AACDisperseIconToText(
                csid=pb2.CSID.CSID_AAC_DISPERSES_ICON_TO_TEXT,
                text=text,
                textEmotion=pb2.AACTextEmotion(
                    currentEmotion=current_emotion,
                    GlobalEmotion=theme_emotion
                ),
                predictIconLabel=pb2.AACPredictIconLabel(
                    iconLabel=predict_icon_str
                )
            )

        except Exception as e:
            logging.error(f"❌ [{client_ip}] Pipeline推理失败: {e}", exc_info=True)
            # 推理失败时返回错误提示
            return pb2.AACDisperseIconToText(
                csid=pb2.CSID.CSID_AAC_DISPERSES_ICON_TO_TEXT,
                text=f"[Error] Pipeline inference failed: {str(e)}",
                textEmotion=pb2.AACTextEmotion(
                    currentEmotion="neutral",
                    GlobalEmotion="neutral"
                ),
                predictIconLabel=pb2.AACPredictIconLabel(iconLabel="")
            )

    def _get_client_ip(self, context):
        """从上下文获取客户端IP"""
        peer = context.peer()
        if ':' in peer:
            return peer.split(':')[1]
        return peer
