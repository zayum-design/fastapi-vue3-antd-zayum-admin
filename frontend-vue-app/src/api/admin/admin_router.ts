import type { RouteRecordStringComponent } from '@/_core/types';

import { requestClient } from '@/api/request';

/**
 * 获取用户所有菜单
 */
export async function getAllAdminRouterApi() {
  return requestClient.get<RouteRecordStringComponent[]>('/admin/auth/all_router');
}
