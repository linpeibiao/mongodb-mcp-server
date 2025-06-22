#!/usr/bin/env python3
"""MongoDB MCP Server 使用示例"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def example_usage():
    """示例用法"""
    
    # 启动 MCP 服务器
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "my_mongo_mcp.server"],
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # 初始化
            await session.initialize()
            
            # 1. 连接到 MongoDB
            print("=== 连接到 MongoDB ===")
            connect_result = await session.call_tool(
                "connect",
                {
                    "connection_string": "mongodb://localhost:27017",
                    "database_name": "testdb"
                }
            )
            print(f"连接结果: {connect_result.content[0].text}")
            
            # 2. 创建文档
            print("\n=== 创建文档 ===")
            create_result = await session.call_tool(
                "create",
                {
                    "collection_name": "users",
                    "document": {
                        "name": "张三",
                        "age": 25,
                        "email": "zhangsan@example.com",
                        "city": "北京"
                    }
                }
            )
            print(f"创建结果: {create_result.content[0].text}")
            
            # 3. 读取文档
            print("\n=== 读取文档 ===")
            read_result = await session.call_tool(
                "read",
                {
                    "collection_name": "users",
                    "filter": {"name": "张三"},
                    "limit": 10
                }
            )
            print(f"读取结果: {read_result.content[0].text}")
            
            # 4. 更新文档
            print("\n=== 更新文档 ===")
            update_result = await session.call_tool(
                "update",
                {
                    "collection_name": "users",
                    "filter": {"name": "张三"},
                    "update": {"$set": {"age": 26, "city": "上海"}},
                    "upsert": False
                }
            )
            print(f"更新结果: {update_result.content[0].text}")
            
            # 5. 再次读取验证更新
            print("\n=== 验证更新 ===")
            read_result2 = await session.call_tool(
                "read",
                {
                    "collection_name": "users",
                    "filter": {"name": "张三"}
                }
            )
            print(f"验证结果: {read_result2.content[0].text}")
            
            # 6. 删除文档
            print("\n=== 删除文档 ===")
            delete_result = await session.call_tool(
                "delete",
                {
                    "collection_name": "users",
                    "filter": {"name": "张三"}
                }
            )
            print(f"删除结果: {delete_result.content[0].text}")
            
            # 7. 断开连接
            print("\n=== 断开连接 ===")
            disconnect_result = await session.call_tool("disconnect", {})
            print(f"断开结果: {disconnect_result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(example_usage()) 