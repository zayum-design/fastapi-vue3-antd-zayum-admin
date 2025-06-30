import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { $t } from '@/locales';

export function useUserMenu() {
  const router = useRouter();

  const menuItems = computed(() => {
    const routes = router.getRoutes();
    const userRoute = routes.find(route => route.name === 'UserCenter');
    
    // 如果找不到路由，返回虚拟菜单数据
    if (!userRoute || userRoute.children.length === 0) {
      return [
      {
        path: '/user/home',
        name: 'home',
        meta: {
          title: '首页',
          icon: 'home'
        },
        children: []
      },
      {
        path: '/user/profile',
        name: 'profile', 
        meta: {
          title: '个人中心',
          icon: 'user'
        },
        children: []
      },
      {
        path: '/user/settings',
        name: 'settings',
        meta: {
          title: '设置',
          icon: 'settings'
        },
        children: []
      }
    ];
    }
    
    return userRoute.children
      .filter(route => {
        const { meta } = route;
        return meta && !meta.hideInMenu;
      })
      .map(route => {
        const { meta, name, path } = route;
        return {
          key: name as string,
          label: meta?.title || '',
          icon: meta?.icon,
          path
        };
      });
  });

  return { menuItems };
}
