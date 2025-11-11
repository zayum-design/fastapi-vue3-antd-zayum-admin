import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it } from 'vitest';

import { useAdminAccessStore } from './admin-access';

describe('useAdminAccessStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('updates accessMenus state', () => {
    const store = useAdminAccessStore();
    expect(store.accessMenus).toEqual([]);
    store.setAccessMenus([{ name: 'Dashboard', path: '/dashboard' }]);
    expect(store.accessMenus).toEqual([
      { name: 'Dashboard', path: '/dashboard' },
    ]);
  });

  it('updates adminAccessToken state correctly', () => {
    const store = useAdminAccessStore();
    expect(store.adminAccessToken).toBeNull(); // 初始状态
    store.setAccessToken('abc123');
    expect(store.adminAccessToken).toBe('abc123');
  });

  it('returns the correct adminAccessToken', () => {
    const store = useAdminAccessStore();
    store.setAccessToken('xyz789');
    expect(store.adminAccessToken).toBe('xyz789');
  });

  // 测试设置空的访问菜单列表
  it('handles empty accessMenus correctly', () => {
    const store = useAdminAccessStore();
    store.setAccessMenus([]);
    expect(store.accessMenus).toEqual([]);
  });

  // 测试设置空的访问路由列表
  it('handles empty accessRoutes correctly', () => {
    const store = useAdminAccessStore();
    store.setAccessRoutes([]);
    expect(store.accessRoutes).toEqual([]);
  });
});
