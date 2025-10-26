# Provider历史订单功能实现说明

## 功能概述
实现了Provider用户获取历史订单的功能，并在My Tasks页面的三个任务显示栏中根据订单状态分类显示任务。

## 实现的功能

### 1. API接口集成
- 在 `src/api/auth.js` 中添加了 `providerAPI.getHistoryOrders()` 方法
- 接口地址：`GET /provider/orders/history`
- 需要Provider角色认证
- 基础地址：`http://k8s-default-freelanc-6fc05b4e03-1086062305.ap-southeast-1.elb.amazonaws.com/api/v1`

### 2. MyTasks.vue组件更新
- 添加了API调用逻辑，在组件mounted时自动加载Provider历史订单
- 实现了数据转换函数 `transformOrderToTask()`，将API响应格式转换为组件所需格式
- 根据订单状态自动分类任务到对应的三个任务栏：
  - **Accepted Tasks**: 状态为 `accepted` 的订单
  - **Tasks in Progress**: 状态为 `in_progress` 的订单  
  - **Historical Tasks**: 状态为 `completed`、`cancelled`、`paid` 的订单

### 3. 用户体验优化
- 添加了loading状态指示器，显示"正在加载任务数据..."
- 添加了错误处理，API调用失败时显示错误信息
- 保持了原有的Customer角色功能不变

### 4. 测试功能
- 在 `src/views/TestAPI.vue` 中添加了Provider历史订单的测试按钮
- 可以通过测试页面验证API调用是否正常工作

## API响应格式
```json
{
  "success": true,
  "data": [
    {
      "id": 3,
      "customer_id": 5,
      "title": "家电维修",
      "description": "冰箱不制冷",
      "service_type": "cleaning_repair",
      "status": "completed",
      "price": 250.0,
      "location": "EAST",
      "address": "789 Pine Street",
      "service_start_time": "2025-10-18T14:00:00",
      "service_end_time": "2025-10-18T16:00:00",
      "created_at": "2025-10-17T12:00:00",
      "updated_at": "2025-10-18T16:30:00",
      "provider_id": 2,
      "payment_status": "paid"
    }
  ],
  "message": "Success",
  "error": null
}
```

## 使用方法
1. 确保用户已登录且角色为Provider
2. 访问My Tasks页面（URL参数不包含 `?role=customer`）
3. 页面会自动调用API获取历史订单数据
4. 任务会根据状态自动分类显示在对应的任务栏中

## 注意事项
- 目前任务操作（取消、开始、完成）暂时使用重新加载数据的方式
- 后续可以添加对应的API接口来实现真正的任务状态更新
- 保持了与现有UI组件的完全兼容性
