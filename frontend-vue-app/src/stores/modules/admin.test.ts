import { createPinia, setActivePinia } from 'pinia';
import { beforeEach, describe, expect, it } from 'vitest';

import { useAdminStore } from './admin';

describe('useAdminStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('returns correct adminInfo', () => {
    const store = useAdminStore();
    const adminInfo: any = { name: 'Jane Doe', roles: [{ value: 'user' }] };
    store.setAdminInfo(adminInfo);
    expect(store.adminInfo).toEqual(adminInfo);
  });

  // 测试重置用户信息时的行为
  it('clears adminInfo and adminRoles when setting null adminInfo', () => {
    const store = useAdminStore();
    store.setAdminInfo({
      roles: [{ roleName: 'User', value: 'user' }],
    } as any);
    expect(store.adminInfo).not.toBeNull();
    expect(store.adminRoles.length).toBeGreaterThan(0);

    store.setAdminInfo(null as any);
    expect(store.adminInfo).toBeNull();
    expect(store.adminRoles).toEqual([]);
  });

  // 测试在没有用户角色时返回空数组
  it('returns an empty array for adminRoles if not set', () => {
    const store = useAdminStore();
    expect(store.adminRoles).toEqual([]);
  });
});
