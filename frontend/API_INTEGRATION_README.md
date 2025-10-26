# API 集成说明

## 概述
本项目已经集成了后端API接口，用于用户认证功能。主要修改包括：

## 修改的文件

### 1. 新增文件
- `src/api/auth.js` - API服务文件，包含认证相关的API调用函数

### 2. 修改的文件
- `src/views/Login.vue` - 登录页面，已集成真实API
- `src/views/Register.vue` - 注册页面，已集成真实API
- `src/views/TestAPI.vue` - API测试页面（新增）
- `src/router/index.js` - 路由配置，添加了测试页面路由

## API 配置

### 基础地址
```
https://localservicemarketplace.space/api/v1
```

### 接口说明

#### 1. 用户注册
- **接口**: `POST /auth/register`
- **参数**:
  - `username` (string, 必填): 用户名
  - `email` (string, 必填): 邮箱
  - `password` (string, 必填): 密码
  - `role_id` (integer, 必填): 角色ID (1=Customer, 2=Provider)

#### 2. 用户登录
- **接口**: `POST /auth/login`
- **参数**:
  - `email` (string, 必填): 邮箱
  - `password` (string, 必填): 密码

## 主要变更

### 登录页面变更
1. 移除了角色选择字段（登录时不需要选择角色）
2. 将用户名字段改为邮箱字段
3. 集成了真实的API调用
4. 添加了邮箱格式验证
5. 登录成功后保存access_token到localStorage

### 注册页面变更
1. 添加了邮箱字段
2. 角色选择改为数字ID (1=Customer, 2=Provider)
3. 集成了真实的API调用
4. 添加了邮箱格式验证
5. 移除了本地存储逻辑

## 使用方法

### 1. 启动项目
```bash
npm run serve
```

### 2. 测试API连接
访问 `http://localhost:8080/test-api` 来测试API连接和功能

### 3. 测试注册和登录
1. 访问 `http://localhost:8080/register` 进行用户注册
2. 访问 `http://localhost:8080/login` 进行用户登录

## 注意事项

1. **CORS问题**: 如果遇到跨域问题，需要后端配置CORS允许前端域名
2. **HTTPS**: 生产环境建议使用HTTPS协议
3. **Token管理**: 登录成功后token会保存在localStorage中
4. **错误处理**: 所有API调用都包含了错误处理机制

## 调试建议

1. 首先访问测试页面检查API连接状态
2. 检查浏览器开发者工具的网络面板查看API请求
3. 查看控制台日志获取详细错误信息
4. 确保后端服务正常运行

## 下一步

1. 根据实际API响应调整错误处理逻辑
2. 添加更多的用户反馈（如加载状态、成功提示等）
3. 实现token过期处理
4. 添加表单验证的实时反馈
