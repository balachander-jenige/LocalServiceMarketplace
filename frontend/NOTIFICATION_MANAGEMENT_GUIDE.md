# Admin Notification Management Feature User Guide

## Feature Overview

The Admin Notification Management module allows administrators to send system announcements to platform users. It supports the following features:

- Send system announcements to all users
- Send notifications to specific customer users
- Send notifications to specific provider users
- Batch select users for notification sending
- Real-time preview of notification content

## How to Use

### 1. Access Notification Management Page

After logging in as an administrator, navigate to the `/admin/notifications` page.

### 2. Publish System Announcement

1. Click the "Publish System Announcement" button in the top-right corner of the page
2. Fill in the notification content in the popup modal
3. Select target user type:
   - **All Users**: Send notification to all customers and providers
   - **Customer Users**: Send notification only to customers
   - **Provider Users**: Send notification only to providers

### 3. Select Specific Users (Optional)

When selecting "Customer Users" or "Provider Users":

1. Enter username or email in the user search box to search
2. Check the users you want to send notifications to from the search results
3. You can select multiple users for batch sending

### 4. Fill in Notification Content

- Enter notification content in the text box (maximum 500 characters)
- The system will display character count in real-time
- You can preview how the notification will appear

### 5. Publish Notification

1. After confirming the notification content is correct, click the "Publish Notification" button
2. The system will display publishing progress
3. Success message will be shown after successful publishing
4. If publishing fails, an error message will be displayed

## Technical Implementation

### API Endpoints

Uses the following API endpoints:

- `POST /admin/notifications/customer/{user_id}` - Send notification to customer
- `POST /admin/notifications/provider/{user_id}` - Send notification to provider

### Component Structure

- `NotificationManagement.vue` - Main page component
- `PublishNotificationModal.vue` - Publish notification modal component

### Feature Highlights

- Responsive design, supports mobile devices
- Real-time user search and filtering
- Batch user selection
- Notification content preview
- Success/error status notifications
- Auto-hide notification messages

## Important Notes

1. Notification content cannot exceed 500 characters
2. Even if user ID doesn't exist, the API will return success (notification will be saved in database)
3. Sent notifications will appear in users' inbox
4. The order_id field of notifications is null, indicating this is a platform notification rather than an order notification
5. The system will automatically handle sending failures without affecting other users' notifications

## Permission Requirements

- Requires Administrator (Admin) role permissions
- Requires valid authentication token
