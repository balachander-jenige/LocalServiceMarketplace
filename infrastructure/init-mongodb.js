// 初始化 MongoDB 数据库 / Initialize MongoDB databases
// 此脚本在 MongoDB 容器启动时自动执行 / This script runs automatically when MongoDB container starts

// 创建微服务数据库 / Create microservice databases
db = db.getSiblingDB('user_db');
db.createCollection('users');
print("✅ user_db 数据库已创建 / user_db database created");

db = db.getSiblingDB('review_db');  
db.createCollection('reviews');
print("✅ review_db 数据库已创建 / review_db database created");

db = db.getSiblingDB('notification_db');
db.createCollection('notifications');
print("✅ notification_db 数据库已创建 / notification_db database created");

print("🎉 MongoDB 初始化完成 / MongoDB initialization completed");