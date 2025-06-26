import type { RouteRecordRaw } from 'vue-router';

import {
  ZAYUM_DOC_URL,
  ZAYUM_GITHUB_URL,
  ZAYUM_LOGO_URL,
} from '@/constants';

import { IFrameView } from '@/layouts';
import { $t } from '@/locales';

const routes: RouteRecordRaw[] = [
  {
    meta: {
      badgeType: 'dot',
      icon: ZAYUM_LOGO_URL,
      order: 9998,
      title: $t('demos.zayum.title'),
    },
    name: 'ZayumProject',
    path: '/zayum-admin',
    children: [
      {
        name: 'ZayumDocument',
        path: '/zayum-admin/document',
        component: IFrameView,
        meta: {
          icon: 'lucide:book-open-text',
          link: ZAYUM_DOC_URL,
          title: $t('demos.zayum.document'),
        },
      },
      {
        name: 'ZayumGithub',
        path: '/zayum-admin/github',
        component: IFrameView,
        meta: {
          icon: 'mdi:github',
          link: ZAYUM_GITHUB_URL,
          title: 'Github',
        },
      },
    ],
  },
  {
    name: 'ZayumAbout',
    path: '/zayum-admin/about',
    component: () => import('@/views/_core/about/index.vue'),
    meta: {
      icon: 'lucide:copyright',
      title: $t('demos.zayum.about'),
      order: 9999,
    },
  },
];

export default routes;
