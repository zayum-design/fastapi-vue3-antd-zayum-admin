import type { RouteRecordStringComponent } from '@/_core/types';

import { requestClient } from '@/api/request';

/**
 * 获取用户所有菜单
 */
export async function getAllUserRouterApi() {
  return requestClient.get<RouteRecordStringComponent[]>('/user/auth/all_router');
}
