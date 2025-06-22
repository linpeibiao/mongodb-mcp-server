#!/usr/bin/env python3
"""简单的 MongoDB MCP 服务器测试脚本"""

import sys
import subprocess
import time
import json

def test_server():
    """测试服务器基本功能"""
    
    print("=== MongoDB MCP 服务器测试 ===\n")
    
    # 检查依赖是否安装
    try:
        import fastmcp
        import pymongo
        import pydantic
        print("✅ 所有依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: uv pip install -e .")
        return False
    
    # 测试导入服务器模块
    try:
        from my_mongo_mcp.server import mcp, mongo_server
        print("✅ 服务器模块导入成功")
    except ImportError as e:
        print(f"❌ 服务器模块导入失败: {e}")
        return False
    
    # 测试工具注册
    tools = mcp.get_tools()
    expected_tools = {'connect', 'disconnect', 'create', 'read', 'update', 'delete'}
    actual_tools = {tool.name for tool in tools}
    
    if expected_tools.issubset(actual_tools):
        print("✅ 所有工具已正确注册")
        print(f"   注册的工具: {', '.join(sorted(actual_tools))}")
    else:
        missing = expected_tools - actual_tools
        print(f"❌ 缺少工具: {', '.join(missing)}")
        return False
    
    # 测试连接状态
    if not mongo_server.is_connected():
        print("✅ 初始连接状态正确（未连接）")
    else:
        print("⚠️  初始连接状态异常（已连接）")
    
    print("\n=== 测试完成 ===")
    print("✅ 基本功能测试通过")
    print("\n📋 使用方法:")
    print("1. 启动 MongoDB 服务器")
    print("2. 运行: python -m my_mongo_mcp.server")
    print("3. 或者查看 example_usage.py 了解编程使用方法")
    
    return True

def check_mongodb_connection():
    """检查 MongoDB 连接"""
    try:
        from pymongo import MongoClient
        client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✅ MongoDB 服务器连接正常")
        client.close()
        return True
    except Exception as e:
        print(f"⚠️  MongoDB 服务器连接失败: {e}")
        print("   请确保 MongoDB 服务器正在运行")
        return False

if __name__ == "__main__":
    print("开始测试 MongoDB MCP 服务器...\n")
    
    # 基本功能测试
    if test_server():
        print("\n" + "="*50)
        # MongoDB 连接测试
        check_mongodb_connection()
    else:
        print("\n❌ 测试失败")
        sys.exit(1) 