const UserBasicLayout = () => import('./basic.vue');
const UserAuthPageLayout = () => import('./auth.vue');

const UserFullLayout = () => import('./full.vue');
const UserIFrameView = () => import('@/layouts').then((m) => m.IFrameView);

export { UserAuthPageLayout, UserBasicLayout, UserFullLayout, UserIFrameView };
