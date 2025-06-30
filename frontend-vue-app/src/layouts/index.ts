const BasicLayout = () => import('./basic.vue');
const AuthPageLayout = () => import('./auth.vue');

const FullLayout = () => import('./full.vue');
const IFrameView = () => import('@/layouts').then((m) => m.IFrameView);

export { AuthPageLayout, BasicLayout, FullLayout, IFrameView };
