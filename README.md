# MongoDB MCP Server

基于 FastMCP 和 uv 工具的 MongoDB MCP（Model Context Protocol）服务器，提供完整的 CRUD 操作功能。

## 功能特性

- ✅ **连接管理**: 连接和断开 MongoDB 数据库
- ✅ **创建文档**: 向集合中插入新文档
- ✅ **读取文档**: 从集合中查询文档，支持过滤、分页
- ✅ **更新文档**: 更新集合中的文档，支持 upsert
- ✅ **删除文档**: 从集合中删除文档
- ✅ **错误处理**: 完善的错误处理和日志记录
- ✅ **数据序列化**: 自动处理 ObjectId 等 MongoDB 特殊类型

## 安装依赖

使用 uv 安装项目依赖：

```bash
# 安装 uv（如果还没安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv pip install -e .
```

或者使用 pip：

```bash
pip install -e .
```

## 工具说明

### 1. connect - 连接数据库

连接到 MongoDB 数据库。

**参数：**
- `connection_string` (str): MongoDB 连接字符串
- `database_name` (str): 数据库名称

**示例：**
```json
{
  "connection_string": "mongodb://localhost:27017",
  "database_name": "myapp"
}
```

### 2. disconnect - 断开连接

断开当前的 MongoDB 连接。

**参数：** 无

### 3. create - 创建文档

在指定集合中创建新文档。

**参数：**
- `collection_name` (str): 集合名称
- `document` (dict): 要插入的文档内容

**示例：**
```json
{
  "collection_name": "users",
  "document": {
    "name": "张三",
    "age": 25,
    "email": "zhangsan@example.com"
  }
}
```

### 4. read - 读取文档

从指定集合中读取文档。

**参数：**
- `collection_name` (str): 集合名称
- `filter` (dict, 可选): 查询过滤条件
- `limit` (int, 可选): 限制返回数量
- `skip` (int, 可选): 跳过的文档数量

**示例：**
```json
{
  "collection_name": "users",
  "filter": {"age": {"$gte": 18}},
  "limit": 10,
  "skip": 0
}
```

### 5. update - 更新文档

更新指定集合中的文档。

**参数：**
- `collection_name` (str): 集合名称
- `filter` (dict): 更新条件
- `update` (dict): 更新操作
- `upsert` (bool, 可选): 如果文档不存在是否创建，默认为 false

**示例：**
```json
{
  "collection_name": "users",
  "filter": {"name": "张三"},
  "update": {"$set": {"age": 26}},
  "upsert": false
}
```

### 6. delete - 删除文档

从指定集合中删除文档。

**参数：**
- `collection_name` (str): 集合名称
- `filter` (dict): 删除条件

**示例：**
```json
{
  "collection_name": "users",
  "filter": {"age": {"$lt": 18}}
}
```

## 使用方法

### 作为 MCP 服务器运行

```bash
# 直接运行
python -m my_mongo_mcp.server

# 或者使用安装的脚本
my-mongo-mcp
```

### 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "python",
      "args": ["-m", "my_mongo_mcp.server"],
      "env": {}
    }
  }
}
```

### 编程方式使用

参考 `example_usage.py` 文件：

```bash
python example_usage.py
```

## 使用示例

### 基本 CRUD 操作

1. **连接数据库**
   ```
   工具: connect
   参数: {"connection_string": "mongodb://localhost:27017", "database_name": "testdb"}
   ```

2. **创建用户文档**
   ```
   工具: create
   参数: {
     "collection_name": "users",
     "document": {"name": "李四", "age": 30, "city": "上海"}
   }
   ```

3. **查询用户**
   ```
   工具: read
   参数: {
     "collection_name": "users",
     "filter": {"city": "上海"},
     "limit": 5
   }
   ```

4. **更新用户信息**
   ```
   工具: update
   参数: {
     "collection_name": "users",
     "filter": {"name": "李四"},
     "update": {"$set": {"age": 31}}
   }
   ```

5. **删除用户**
   ```
   工具: delete
   参数: {
     "collection_name": "users",
     "filter": {"name": "李四"}
   }
   ```

6. **断开连接**
   ```
   工具: disconnect
   ```

## 注意事项

- 使用前请确保 MongoDB 服务器正在运行
- 所有操作都需要先连接数据库
- ObjectId 等特殊类型会自动转换为字符串
- 支持所有标准的 MongoDB 查询语法
- 错误信息会以中文形式返回

## 系统要求

- Python 3.8+
- MongoDB 3.6+
- fastmcp 0.2.0+
- pymongo 4.6.0+

## 故障排除

1. **连接失败**
   - 检查 MongoDB 服务是否启动
   - 验证连接字符串是否正确
   - 检查网络连接和防火墙设置

2. **权限错误**
   - 确保 MongoDB 用户有足够的权限
   - 检查数据库和集合的访问权限

3. **数据类型错误**
   - 确保 JSON 数据格式正确
   - 注意 ObjectId 的格式要求 "# mongodb-mcp-server" 
