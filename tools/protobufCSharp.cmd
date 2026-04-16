.\plugin\protoc-33.0-win64\bin\protoc.exe ^
  --proto_path=./protos ^
  --csharp_out=./protos ^
  --grpc_out=./protos ^
  --plugin=protoc-gen-grpc="C:\Users\admin\.nuget\packages\grpc.tools\2.80.0\tools\windows_x64\grpc_csharp_plugin.exe" ^
  message.proto
@pause