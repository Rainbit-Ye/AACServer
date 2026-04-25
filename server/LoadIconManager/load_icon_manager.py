"""
LoadIconManager - 图标加载管理器
负责从JPGDataset加载图片并返回二进制数据
"""

import logging
from pathlib import Path
from typing import List, Tuple
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from protos import message_pb2 as pb2


class LoadIconManager:
    """图标加载管理器"""
    
    def __init__(self, dataset_path: str = None):
        """
        初始化图标加载管理器
        
        Args:
            dataset_path: 数据集路径，默认为 AACDataset/JPGDataset
        """
        self.dataset_path = Path(dataset_path) if dataset_path else Path(__file__).resolve().parent.parent.parent / "AACDataset" / "JPGDataset"
        self._path_cache = None
        self._build_path_cache()
        logging.info(f"LoadIconManager 初始化完成，数据集路径: {self.dataset_path}")
    
    def _build_path_cache(self):
        """构建文件路径缓存，提高查找效率"""
        self._path_cache = {}
        
        if not self.dataset_path.exists():
            logging.error(f"数据集路径不存在: {self.dataset_path}")
            return
        
        for root, dirs, files in os.walk(self.dataset_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    filename = Path(file).stem
                    normalized_name = filename.replace(' ', '_').lower()
                    full_path = Path(root) / file
                    
                    # 存储多种变体以支持灵活匹配
                    self._path_cache[filename.lower()] = full_path
                    self._path_cache[normalized_name] = full_path
        
        logging.info(f"路径缓存构建完成，共 {len(self._path_cache)} 个文件")
    
    def load_icons(self, icon_labels: List[str]) -> pb2.LoadIconRes:
        """
        加载多个图标
        
        Args:
            icon_labels: 图标标签列表
            
        Returns:
            LoadIconRes响应对象
        """
        response = pb2.LoadIconRes()
        response.csid = pb2.CSID.CSID_LOAD_ICON_RES
        
        image_data_list = []
        found_labels = []
        
        for icon_label in icon_labels:
            try:
                image_path = self._find_image(icon_label)
                
                if image_path and image_path.exists():
                    image_data = self._read_image(image_path)
                    if image_data:
                        image_data_list.append(image_data)
                        found_labels.append(icon_label)
                        logging.info(f"  ✅ 成功加载: {icon_label} ({len(image_data)} bytes)")
                else:
                    logging.warning(f"  ⚠️  未找到: {icon_label}")
                    
            except Exception as e:
                logging.error(f"  ❌ 读取失败: {icon_label}, 错误: {e}")
                continue
        
        response.iconLabel.extend(found_labels)
        response.imageData.extend(image_data_list)
        
        if not image_data_list:
            logging.warning(f"  ⚠️  没有成功加载任何图片")
        else:
            logging.info(f"  ✅ 总计加载 {len(image_data_list)} 张图片")
        
        return response
    
    def _find_image(self, icon_label: str) -> Path:
        """
        查找图片文件
        
        Args:
            icon_label: 图标标签
            
        Returns:
            图片文件路径，找不到返回None
        """
        # 尝试直接作为路径
        direct_path = self.dataset_path / icon_label
        if direct_path.exists():
            # 如果是目录，查找第一个图片文件
            if direct_path.is_dir():
                image_files = list(direct_path.glob("*.jpg")) + list(direct_path.glob("*.jpeg")) + list(direct_path.glob("*.png"))
                if image_files:
                    return image_files[0]
                else:
                    logging.warning(f"目录为空: {icon_label}")
                    return None
            # 如果是文件，直接返回
            elif direct_path.is_file():
                return direct_path
        
        # 尝试通过缓存查找
        label_lower = icon_label.lower()
        variations = [
            label_lower,
            label_lower.replace('_', ' '),
            label_lower.replace(' ', '_'),
        ]
        
        for variation in variations:
            if variation in self._path_cache:
                return self._path_cache[variation]
        
        return None
    
    def _read_image(self, image_path: Path) -> bytes:
        """
        读取图片文件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            图片二进制数据
        """
        try:
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logging.error(f"读取图片失败: {image_path}, 错误: {e}")
            return None
    
    def refresh_cache(self):
        """刷新路径缓存"""
        logging.info("刷新路径缓存...")
        self._build_path_cache()
