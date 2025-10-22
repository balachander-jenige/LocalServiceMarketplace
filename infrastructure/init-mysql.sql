-- 创建微服务数据库 / Create microservice databases
CREATE DATABASE IF NOT EXISTS auth_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS order_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS payment_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 显示创建的数据库 / Show created databases
SHOW DATABASES;

-- 授权用户访问数据库 / Grant user access to databases
GRANT ALL PRIVILEGES ON auth_db.* TO 'freelancer'@'%';
GRANT ALL PRIVILEGES ON order_db.* TO 'freelancer'@'%';
GRANT ALL PRIVILEGES ON payment_db.* TO 'freelancer'@'%';
FLUSH PRIVILEGES;

-- 验证权限 / Verify permissions
SELECT User, Host FROM mysql.user WHERE User = 'freelancer';