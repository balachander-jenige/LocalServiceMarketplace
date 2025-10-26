// API基础配置
const API_BASE_URL = "https://localservicemarketplace.space/api/v1";

// 通用请求函数
async function request(url, options = {}) {
  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  try {
    console.log("发送请求:", {
      url: `${API_BASE_URL}${url}`,
      method: config.method,
      headers: config.headers,
      body: config.body,
    });

    const response = await fetch(`${API_BASE_URL}${url}`, config);
    let data;
    try {
      data = await response.json();
    } catch (_) {
      data = null;
    }

    if (!response.ok) {
      // 检查是否是Token过期
      if (
        response.status === 401 ||
        (data && data.message && data.message.includes("expired"))
      ) {
        // 清除过期的Token
        tokenManager.removeToken();
        sessionStorage.removeItem("currentUser");

        // 如果是浏览器环境，跳转到登录页
        if (typeof window !== "undefined" && window.location) {
          window.location.href = "/login";
        }
      }

      // 透出后端更详细的错误信息
      let backendMessage = data && (data.error || data.message || data.detail);

      // 如果backendMessage是对象，转换为字符串
      if (backendMessage && typeof backendMessage === "object") {
        backendMessage = JSON.stringify(backendMessage);
      }

      const err = new Error(
        backendMessage || `HTTP error! status: ${response.status}`
      );
      err.status = response.status;
      err.data = data;
      throw err;
    }

    return data;
  } catch (error) {
    console.error("API请求错误:", error);
    throw error;
  }
}

// 认证API
export const authAPI = {
  // 用户注册
  async register(userData) {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username: userData.username,
        email: userData.email,
        password: userData.password,
        role_id: userData.role_id,
      }),
    });
  },

  // 用户登录
  async login(credentials) {
    return request("/auth/login", {
      method: "POST",
      body: JSON.stringify({
        email: credentials.email,
        password: credentials.password,
      }),
    });
  },

  // 获取当前用户信息
  async getCurrentUser() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/auth/me", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

// Customer API
export const customerAPI = {
  // 获取客户资料信息
  async getProfile() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/customer/profile", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 更新客户资料信息
  async updateProfile(profileData) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/customer/profile", {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(profileData),
    });
  },

  // 发布订单
  async publishOrder(orderData) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/customer/orders/publish", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(orderData),
    });
  },

  // 获取客户历史订单
  async getHistoryOrders() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取客户历史订单请求:", {
      url: "/customer/orders/history",
      method: "GET",
    });

    return request("/customer/orders/history", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取客户当前进行中的订单
  async getCurrentOrders() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取客户当前订单请求:", {
      url: "/customer/orders",
      method: "GET",
    });

    return request("/customer/orders", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取客户指定订单详情
  async getOrderDetail(orderId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取客户订单详情请求:", {
      url: `/customer/orders/my/${orderId}`,
      method: "GET",
      orderId: orderId,
    });

    return request(`/customer/orders/my/${orderId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 取消订单
  async cancelOrder(orderId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送取消订单请求:", {
      url: `/customer/orders/cancel/${orderId}`,
      method: "POST",
      orderId: orderId,
    });

    return request(`/customer/orders/cancel/${orderId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
  },

  // 支付订单
  async payOrder(orderId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送支付订单请求:", {
      url: "/customer/payments/pay",
      method: "POST",
      orderId: orderId,
    });

    return request("/customer/payments/pay", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ order_id: orderId }),
    });
  },

  // 获取客户收件箱
  async getInbox() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取客户收件箱请求:", {
      url: "/customer/inbox",
      method: "GET",
    });

    return request("/customer/inbox", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

// Provider API
export const providerAPI = {
  // 获取服务商资料信息
  async getProfile() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/provider/profile", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 更新服务商资料信息
  async updateProfile(profileData) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/provider/profile", {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(profileData),
    });
  },

  // 获取可接取的订单列表
  async getAvailableOrders(filters = {}) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    // 构建查询参数
    const queryParams = new URLSearchParams();

    // 添加筛选参数
    if (filters.location) {
      queryParams.append("location", filters.location);
    }
    if (filters.service_type) {
      queryParams.append("service_type", filters.service_type);
    }
    if (filters.min_price !== undefined && filters.min_price !== null) {
      queryParams.append("min_price", filters.min_price);
    }
    if (filters.max_price !== undefined && filters.max_price !== null) {
      queryParams.append("max_price", filters.max_price);
    }
    if (filters.keyword) {
      queryParams.append("keyword", filters.keyword);
    }

    // 构建URL
    let url = "/provider/orders/available";
    if (queryParams.toString()) {
      url += `?${queryParams.toString()}`;
    }

    console.log("发送获取可接取订单请求:", {
      url: url,
      method: "GET",
      filters: filters,
    });

    return request(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 接取订单
  async acceptOrder(orderId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送接取订单请求:", {
      url: `/provider/orders/accept/${orderId}`,
      method: "POST",
      orderId: orderId,
    });

    return request(`/provider/orders/accept/${orderId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });
  },

  // 获取服务商历史订单
  async getHistoryOrders() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取历史订单请求:", {
      url: "/provider/orders/history",
      method: "GET",
    });

    return request("/provider/orders/history", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 更新订单状态
  async updateOrderStatus(orderId, status) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送更新订单状态请求:", {
      url: `/provider/orders/status/${orderId}`,
      method: "POST",
      orderId: orderId,
      new_status: status,
    });

    return request(`/provider/orders/status/${orderId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ new_status: status }),
    });
  },

  // 获取服务商的评分信息
  async getMyRating() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取服务商评分请求:", {
      url: "/reviews/provider/me/rating",
      method: "GET",
    });

    return request("/reviews/provider/me/rating", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取服务商的评价列表
  async getMyReviews() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取服务商评价列表请求:", {
      url: "/reviews/provider/me/reviews",
      method: "GET",
    });

    return request("/reviews/provider/me/reviews", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取服务商收件箱
  async getInbox() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取服务商收件箱请求:", {
      url: "/provider/inbox",
      method: "GET",
    });

    return request("/provider/inbox", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

// Task Review API
export const reviewAPI = {
  // Submit task review - 使用新的接口
  async submitReview(orderId, reviewData) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送评价请求:", {
      url: "/reviews",
      method: "POST",
      orderId: orderId,
      reviewData: reviewData,
    });

    return request("/reviews", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        order_id: orderId,
        stars: reviewData.rating,
        content: reviewData.comment || "",
      }),
    });
  },

  // Get task review - 保持原有接口
  async getTaskReview(taskId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request(`/tasks/${taskId}/review`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

// 通知管理API
export const notificationAPI = {
  // 获取所有通知
  async getNotifications() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/admin/notifications", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 创建通知
  async createNotification(notificationData) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/admin/notifications", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: notificationData.title,
        content: notificationData.content,
        priority: notificationData.priority,
        status: notificationData.status,
      }),
    });
  },

  // 更新通知
  async updateNotification(notificationId, notificationData) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request(`/admin/notifications/${notificationId}`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        title: notificationData.title,
        content: notificationData.content,
        priority: notificationData.priority,
        status: notificationData.status,
      }),
    });
  },

  // 发布通知
  async publishNotification(notificationId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request(`/admin/notifications/${notificationId}/publish`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 归档通知
  async archiveNotification(notificationId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request(`/admin/notifications/${notificationId}/archive`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 删除通知
  async deleteNotification(notificationId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request(`/admin/notifications/${notificationId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },
};

// 管理员API
export const adminAPI = {
  // 获取所有用户列表
  async getAllUsers(roleId = null) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    let url = "/admin/users";
    if (roleId) {
      url += `?role_id=${roleId}`;
    }

    return request(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取用户详情
  async getUserDetail(userId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request(`/admin/users/${userId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 删除用户
  async deleteUser(userId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送删除用户请求:", {
      url: `/admin/users/${userId}`,
      method: "DELETE",
      userId: userId,
    });

    return request(`/admin/users/${userId}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取所有订单列表
  async getAllOrders(status = null) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    let url = "/admin/orders";
    if (status) {
      url += `?status=${status}`;
    }

    return request(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取订单详情
  async getOrderDetail(orderId) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送获取订单详情请求:", {
      url: `/admin/orders/${orderId}`,
      method: "GET",
      orderId: orderId,
    });

    return request(`/admin/orders/${orderId}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 获取待审核订单列表
  async getPendingReviewOrders() {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    return request("/admin/orders/pending-review", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  },

  // 审批订单（批准或拒绝）
  async approveOrder(orderId, approved, rejectReason = null) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    const requestBody = {
      approved: approved,
    };

    // 如果是拒绝，添加拒绝原因
    if (!approved && rejectReason) {
      requestBody.reject_reason = rejectReason;
    }

    console.log("发送审批请求:", {
      url: `/admin/orders/${orderId}/approve`,
      body: requestBody,
      jsonString: JSON.stringify(requestBody),
    });

    return request(`/admin/orders/${orderId}/approve`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });
  },

  // 发送通知给客户
  async sendNotificationToCustomer(userId, message) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送通知给客户:", {
      url: `/admin/notifications/customer/${userId}`,
      method: "POST",
      userId: userId,
      message: message,
    });

    return request(`/admin/notifications/customer/${userId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
  },

  // 发送通知给服务商
  async sendNotificationToProvider(userId, message) {
    const token = tokenManager.getToken();
    if (!token) {
      throw new Error("No token found");
    }

    console.log("发送通知给服务商:", {
      url: `/admin/notifications/provider/${userId}`,
      method: "POST",
      userId: userId,
      message: message,
    });

    return request(`/admin/notifications/provider/${userId}`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    });
  },
};

// Token管理
export const tokenManager = {
  // 保存token
  setToken(token) {
    localStorage.setItem("access_token", token);
  },

  // 获取token
  getToken() {
    return localStorage.getItem("access_token");
  },

  // 删除token
  removeToken() {
    localStorage.removeItem("access_token");
  },

  // 检查是否已登录
  isLoggedIn() {
    return !!this.getToken();
  },
};
