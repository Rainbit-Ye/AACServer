"""
启动AAC服务器
"""
import sys
import os
import subprocess
import logging

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def auto_select_gpu():
    """
    在 PyTorch import 之前自动选择剩余显存最多的 GPU，
    通过设置 CUDA_VISIBLE_DEVICES 让 PyTorch 只能看到这块 GPU。
    必须在 import torch 之前调用才有效。
    """
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=index,memory.used,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            print("[GPU] nvidia-smi 执行失败，使用默认 GPU")
            return

        best_gpu = None
        best_free = -1
        for line in result.stdout.strip().split('\n'):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) == 3:
                idx, used, total = int(parts[0]), int(parts[1]), int(parts[2])
                free = total - used
                print(f"[GPU] GPU {idx}: 已用 {used}MiB / 总计 {total}MiB, 剩余 {free}MiB")
                if free > best_free:
                    best_free = free
                    best_gpu = idx

        if best_gpu is not None:
            os.environ['CUDA_VISIBLE_DEVICES'] = str(best_gpu)
            print(f"[GPU] 自动选择 GPU {best_gpu} (剩余显存 {best_free}MiB)")
            print(f"[GPU] CUDA_VISIBLE_DEVICES={best_gpu}")
        else:
            print("[GPU] 未检测到可用 GPU")
    except Exception as e:
        print(f"[GPU] 自动选择GPU失败: {e}，使用默认配置")


# ★ 必须在 import torch / transformers 之前调用
auto_select_gpu()

from server.aac_server import AACServer

if __name__ == '__main__':
    server = AACServer()
    server.start()
