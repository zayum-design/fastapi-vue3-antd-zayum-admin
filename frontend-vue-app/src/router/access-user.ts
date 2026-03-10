import type {
  ComponentRecordType,
  GenerateMenuAndRoutesOptions,
} from '@/_core/types';

import { generateAccessible } from '@/_core/access';

import { message } from 'ant-design-vue';

import { getAllUserRouterApi } from '@/api/user/user_router';
import { UserBasicLayout, UserIFrameView } from '@/views/user/layouts';
import { $t } from '@/locales';

const forbiddenComponent = () => import('@/views/_core/fallback/forbidden.vue');

async function generateUserAccess(options: GenerateMenuAndRoutesOptions) {
  const pageMap: ComponentRecordType = import.meta.glob('../views/**/*.vue');

  const layoutMap: ComponentRecordType = {
    UserBasicLayout,
    UserIFrameView,
  };

  // 使用 'backend-user' mode 生成用户端路由
  return await generateAccessible('backend-user', {
    ...options,
    fetchMenuListAsync: async () => {
      message.loading({
        content: `${$t('common.loadingMenu')}...`,
        duration: 1.5,
      });
      return await getAllUserRouterApi();
    },
    // 可以指定没有权限跳转403页面
    forbiddenComponent,
    // 如果 route.meta.menuVisibleWithForbidden = true
    layoutMap,
    pageMap,
  });
}

export { generateUserAccess };
