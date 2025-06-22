#!/usr/bin/env python3
"""MongoDB MCP Server with CRUD operations"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError
from bson import ObjectId, json_util

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionInfo(BaseModel):
    """MongoDB 连接信息"""
    connection_string: str = Field(description="MongoDB 连接字符串")
    database_name: str = Field(description="数据库名称")


class CreateDocumentRequest(BaseModel):
    """创建文档请求"""
    collection_name: str = Field(description="集合名称")
    document: Dict[str, Any] = Field(description="要插入的文档")


class ReadDocumentsRequest(BaseModel):
    """读取文档请求"""
    collection_name: str = Field(description="集合名称")
    filter: Optional[Dict[str, Any]] = Field(default=None, description="查询过滤条件")
    limit: Optional[int] = Field(default=None, description="限制返回数量")
    skip: Optional[int] = Field(default=0, description="跳过的文档数量")


class UpdateDocumentRequest(BaseModel):
    """更新文档请求"""
    collection_name: str = Field(description="集合名称")
    filter: Dict[str, Any] = Field(description="更新条件")
    update: Dict[str, Any] = Field(description="更新操作")
    upsert: bool = Field(default=False, description="如果不存在是否创建")


class DeleteDocumentRequest(BaseModel):
    """删除文档请求"""
    collection_name: str = Field(description="集合名称")
    filter: Dict[str, Any] = Field(description="删除条件")


class MongoDBMCPServer:
    """MongoDB MCP 服务器"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        self.connection_info: Optional[ConnectionInfo] = None
        
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self.client is not None and self.database is not None
    
    def serialize_document(self, doc: Any) -> Any:
        """序列化 MongoDB 文档，处理 ObjectId 等特殊类型"""
        if isinstance(doc, dict):
            result = {}
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    result[key] = str(value)
                elif isinstance(value, dict):
                    result[key] = self.serialize_document(value)
                elif isinstance(value, list):
                    result[key] = [self.serialize_document(item) for item in value]
                else:
                    result[key] = value
            return result
        elif isinstance(doc, list):
            return [self.serialize_document(item) for item in doc]
        elif isinstance(doc, ObjectId):
            return str(doc)
        else:
            return doc


# 创建服务器实例
mongo_server = MongoDBMCPServer()

# 创建 FastMCP 应用
mcp = FastMCP("MongoDB MCP Server")


@mcp.tool()
def connect(connection_info: ConnectionInfo) -> str:
    """
    连接到 MongoDB 数据库
    
    Args:
        connection_info: MongoDB 连接信息，包含连接字符串和数据库名称
        
    Returns:
        连接状态消息
    """
    try:
        # 如果已连接，先断开
        if mongo_server.is_connected():
            mongo_server.client.close()
            
        # 创建新连接
        mongo_server.client = MongoClient(connection_info.connection_string)
        mongo_server.database = mongo_server.client[connection_info.database_name]
        mongo_server.connection_info = connection_info
        
        # 测试连接
        mongo_server.client.admin.command('ping')
        
        logger.info(f"已连接到 MongoDB 数据库: {connection_info.database_name}")
        return f"成功连接到 MongoDB 数据库: {connection_info.database_name}"
        
    except PyMongoError as e:
        logger.error(f"连接 MongoDB 失败: {e}")
        mongo_server.client = None
        mongo_server.database = None
        mongo_server.connection_info = None
        return f"连接失败: {str(e)}"


@mcp.tool()
def disconnect() -> str:
    """
    断开 MongoDB 连接
    
    Returns:
        断开连接状态消息
    """
    try:
        if mongo_server.client:
            mongo_server.client.close()
            mongo_server.client = None
            mongo_server.database = None
            mongo_server.connection_info = None
            logger.info("已断开 MongoDB 连接")
            return "已成功断开 MongoDB 连接"
        else:
            return "当前没有活动的 MongoDB 连接"
    except Exception as e:
        logger.error(f"断开连接时出错: {e}")
        return f"断开连接时出错: {str(e)}"


@mcp.tool()
def create(request: CreateDocumentRequest) -> str:
    """
    在指定集合中创建文档
    
    Args:
        request: 创建文档请求，包含集合名称和文档内容
        
    Returns:
        创建结果消息
    """
    if not mongo_server.is_connected():
        return "错误: 未连接到 MongoDB。请先使用 connect 工具连接数据库。"
    
    try:
        collection: Collection = mongo_server.database[request.collection_name]
        result = collection.insert_one(request.document)
        
        logger.info(f"在集合 {request.collection_name} 中创建了文档，ID: {result.inserted_id}")
        return f"成功创建文档，ID: {result.inserted_id}"
        
    except PyMongoError as e:
        logger.error(f"创建文档失败: {e}")
        return f"创建文档失败: {str(e)}"


@mcp.tool()
def read(request: ReadDocumentsRequest) -> str:
    """
    从指定集合中读取文档
    
    Args:
        request: 读取文档请求，包含集合名称、过滤条件等
        
    Returns:
        查询结果的 JSON 字符串
    """
    if not mongo_server.is_connected():
        return "错误: 未连接到 MongoDB。请先使用 connect 工具连接数据库。"
    
    try:
        collection: Collection = mongo_server.database[request.collection_name]
        
        # 构建查询
        cursor = collection.find(request.filter or {})
        
        if request.skip:
            cursor = cursor.skip(request.skip)
        if request.limit:
            cursor = cursor.limit(request.limit)
            
        # 获取结果并序列化
        documents = list(cursor)
        serialized_docs = [mongo_server.serialize_document(doc) for doc in documents]
        
        logger.info(f"从集合 {request.collection_name} 中读取了 {len(documents)} 个文档")
        
        result = {
            "collection": request.collection_name,
            "count": len(documents),
            "documents": serialized_docs
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except PyMongoError as e:
        logger.error(f"读取文档失败: {e}")
        return f"读取文档失败: {str(e)}"


@mcp.tool()
def update(request: UpdateDocumentRequest) -> str:
    """
    更新指定集合中的文档
    
    Args:
        request: 更新文档请求，包含集合名称、过滤条件和更新操作
        
    Returns:
        更新结果消息
    """
    if not mongo_server.is_connected():
        return "错误: 未连接到 MongoDB。请先使用 connect 工具连接数据库。"
    
    try:
        collection: Collection = mongo_server.database[request.collection_name]
        
        # 执行更新操作
        result = collection.update_many(
            request.filter,
            request.update,
            upsert=request.upsert
        )
        
        logger.info(f"在集合 {request.collection_name} 中更新了 {result.modified_count} 个文档")
        
        if result.upserted_id:
            return f"成功更新，匹配: {result.matched_count}, 修改: {result.modified_count}, 新增: {result.upserted_id}"
        else:
            return f"成功更新，匹配: {result.matched_count}, 修改: {result.modified_count}"
        
    except PyMongoError as e:
        logger.error(f"更新文档失败: {e}")
        return f"更新文档失败: {str(e)}"


@mcp.tool()
def delete(request: DeleteDocumentRequest) -> str:
    """
    从指定集合中删除文档
    
    Args:
        request: 删除文档请求，包含集合名称和删除条件
        
    Returns:
        删除结果消息
    """
    if not mongo_server.is_connected():
        return "错误: 未连接到 MongoDB。请先使用 connect 工具连接数据库。"
    
    try:
        collection: Collection = mongo_server.database[request.collection_name]
        
        # 执行删除操作
        result = collection.delete_many(request.filter)
        
        logger.info(f"从集合 {request.collection_name} 中删除了 {result.deleted_count} 个文档")
        return f"成功删除 {result.deleted_count} 个文档"
        
    except PyMongoError as e:
        logger.error(f"删除文档失败: {e}")
        return f"删除文档失败: {str(e)}"


def main():
    """主函数"""
    mcp.run(transport="sse")


if __name__ == "__main__":
    connect("mongodb://public_hub_user:e6ewGLXN1CdeV1bsyoyV@34.126.81.6:27017/public_hub?authSource=public_hub")