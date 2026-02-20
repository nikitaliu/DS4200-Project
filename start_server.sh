#!/bin/bash
# 启动本地服务器的脚本

cd "$(dirname "$0")"

echo "🚀 启动 MA Housing 可视化项目..."
echo "📂 项目目录: $(pwd)"
echo ""
echo "服务器启动在: http://localhost:8080"
echo "按 Ctrl+C 停止服务器"
echo ""

python3 -m http.server 8080
