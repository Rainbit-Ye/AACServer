# 工具脚本

本项目包含用于Protocol Buffers文件生成的工具脚本。

## 工具说明

### protobufCSharp.cmd
生成C# Protocol Buffers文件

**要求:**
- 已安装protoc编译器
- protoc在系统PATH中

**使用方法:**
```bash
cd tools
protobufCSharp.cmd
```

**输出:**
- `Message.cs` - C#消息类（生成到根目录）

---

### protobufpython.cmd
生成Python Protocol Buffers文件

**要求:**
- 已安装protoc编译器
- protoc在系统PATH中

**使用方法:**
```bash
cd tools
protobufpython.cmd
```

**输出:**
- `protos/message_pb2.py` - Python消息类

---

### generate_grpc_python.bat  
生成Python gRPC服务文件

**要求:**
- 已安装protoc编译器
- 已安装grpcio-tools (`pip install grpcio-tools`)

**使用方法:**
```bash
cd tools
generate_grpc_python.bat
```

**输出:**
- `protos/message_pb2.py` - Python消息类
- `protos/message_pb2_grpc.py` - Python gRPC服务类

---

### generate_python.sh
Linux/Mac版本的Python Protocol Buffers生成脚本

**使用方法:**
```bash
cd tools
chmod +x generate_python.sh
./generate_python.sh
```

---

## 安装依赖

### 安装protoc编译器
Windows: 下载并安装 Protocol Buffers编译器
https://github.com/protocolbuffers/protobuf/releases

### 安装grpcio-tools
```bash
pip install grpcio-tools
```

---

## 开发流程

1. 修改`protos/message.proto`文件
2. 根据需要运行对应的生成脚本：
   - C#项目：运行 `protobufCSharp.cmd`
   - Python项目：运行 `protobufpython.cmd` 或 `generate_grpc_python.bat`
3. 更新服务器和客户端代码

---

## 脚本对比

| 脚本 | 输出格式 | 输出位置 | 用途 |
|------|----------|----------|------|
| protobufCSharp.cmd | C# | Message.cs (根目录) | C#客户端/服务端 |
| protobufpython.cmd | Python | protos/message_pb2.py | Python消息类 |
| generate_grpc_python.bat | Python + gRPC | protos/message_pb2.py<br>protos/message_pb2_grpc.py | Python gRPC服务 |

---

## 注意事项

- 生成脚本会覆盖现有的文件
- 生成前确保备份重要代码
- 修改proto文件后需要重新生成
- C#文件生成到根目录，Python文件生成到protos目录
