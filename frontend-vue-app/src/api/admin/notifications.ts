import { requestClient } from '@/api/request';

export namespace NotificationsApi {
  /** 通知项接口 */
  export interface NotificationItem {
    id: number;
    avatar: string;
    date: string;
    isRead: boolean;
    message: string;
    title: string;
    type: string;
  }

  /** 通知列表接口返回值 */
  export interface NotificationsListResult {
    notifications: NotificationItem[];
    total: number;
    unread_count: number;
  }

  /** 通用操作接口返回值 */
  export interface OperationResult {
    message: string;
  }
}

/**
 * 获取通知列表
 */
export async function getNotificationsListApi() {
  return requestClient.get<NotificationsApi.NotificationsListResult>('/admin/notifications/list');
}

/**
 * 标记所有通知为已读
 */
export async function markAllNotificationsReadApi() {
  return requestClient.post<NotificationsApi.OperationResult>('/admin/notifications/mark-all-read');
}

/**
 * 清空所有通知
 */
export async function clearAllNotificationsApi() {
  return requestClient.post<NotificationsApi.OperationResult>('/admin/notifications/clear');
}

/**
 * 标记单个通知为已读
 */
export async function markNotificationReadApi(notificationId: number) {
  return requestClient.post<NotificationsApi.OperationResult>(`/admin/notifications/${notificationId}/read`);
}
