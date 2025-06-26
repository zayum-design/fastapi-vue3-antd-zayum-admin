import type { RouteRecordRaw } from 'vue-router';

import { $t } from '@/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      icon: 'ic:baseline-view-in-ar',
      title: $t('user.user'),
    },
    name: 'User',
    path: '/user',
    children: [
      {
        name: 'UserManage',
        path: '/user/user',
        component: () => import('@/views/_core/user/user.vue'),
        meta: {
          icon: 'lucide:area-chart',
          title: $t('user.user_manage'),
        },
      },
      {
        name: 'UserGroup',
        path: '/user/group',
        component: () => import('@/views/_core/user/group.vue'),
        meta: {
          icon: 'lucide:area-chart',
          title: $t('user_group.user_group'),
        },
      },
      {
        name: 'UserRule',
        path: '/user/rule',
        component: () => import('@/views/_core/user/rule.vue'),
        meta: {
          icon: 'lucide:area-chart',
          title: $t('user_rule.user_rule'),
        },
      },
       
    ],
  },
];

export default routes;
