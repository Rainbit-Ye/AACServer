# VRConnect Project

VRConnect项目 - AAC图标加载和通信系统

## 项目结构

```
VRConnect/
├── protos/                 # Protocol Buffers定义和生成的文件
│   ├── __init__.py
│   ├── message.proto      # Protobuf消息定义
│   ├── message_pb2.py     # 生成的Python消息类
│   └── message_pb2_grpc.py # 生成的gRPC服务类
├── server/                 # 服务器模块
│   ├── __init__.py
│   ├── aac_server.py      # 主服务器启动文件
│   ├── EventDispatcher/   # 事件分发器
│   │   ├── __init__.py
│   │   └── event_dispatcher.py
│   └── LoadIconManager/   # 图标加载管理器
│       ├── __init__.py
│       └── load_icon_manager.py
├── client/                 # 客户端模块
│   ├── __init__.py
│   └── aac_client.py      # AAC客户端类
├── tests/                  # 测试模块
│   ├── __init__.py
│   └── load_icon_client_test.py  # LoadIcon功能测试
├── AACDataset/             # AAC数据集
│   └── JPGDataset/         # 图标数据集
└── connect_server.py       # 旧版服务器（已废弃）
```

## 快速开始

### 启动服务器

```bash
# 方式1: 使用模块化服务器
cd D:/2526/VRConnect
python -m server.aac_server

# 方式2: 直接运行服务器文件
python server/aac_server.py
```

### 运行测试

```bash
# 运行LoadIcon功能测试
python tests/load_icon_client_test.py
```

### 使用客户端

```python
from client import AACClient

# 连接服务器
client = AACClient('localhost:50051')
client.connect()

# 加载图标
response = client.load_icons(['winner', 'winter', 'yorkshire_pudding'])

# 处理响应
for i, label in enumerate(response.iconLabel):
    print(f"{label}: {len(response.imageData[i])} bytes")

# 断开连接
client.disconnect()
```

## 模块说明

### LoadIconManager
负责从JPGDataset加载图片文件，支持：
- 灵活的路径匹配（文件名/路径/目录）
- 大小写不敏感搜索
- 空格和下划线兼容
- 路径缓存提高性能

### EventDispatcher
基于CSID的事件分发器，路由不同的请求到对应的处理器：
- `CSID_LOAD_ICON_REQ` → LoadIconManager处理
- `CSID_AAC_DISPERSES_ICON_SEND` → AAC图标处理

### AACClient
gRPC客户端，提供简洁的API与服务器通信：
- 连接管理
- 图标加载
- 连接检查

## 开发指南

### 添加新的处理器

1. 在`EventDispatcher`中添加新的CSID处理器
2. 实现对应的处理函数
3. 在proto文件中定义新的消息类型

### 扩展LoadIconManager

可以扩展LoadIconManager来支持：
- 图片格式转换
- 图片压缩
- 缓存机制
- 多线程加载

## 协议定义

参见`protos/message.proto`文件，包含：
- `LoadIconReq/LoadIconRes`: 图标加载请求和响应
- `AACDisperseIconSend/AACDisperseIconToText`: AAC图标处理
- `ConnectCheckRequest/ConnectCheckResponse`: 连接检查

## 注意事项

- 确保JPGDataset路径正确
- 服务器监听端口50051，确保防火墙允许
- 支持局域网访问，IP地址根据网络配置调整
