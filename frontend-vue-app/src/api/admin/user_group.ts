// src/api/core/user.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch user group items
export async function fetchUserGroupItems({
  page = 1,
  perPage = 10,
  search = '',
  orderby = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
  orderby?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/user/group/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}


// Create or update an user group
export async function saveUserGroup(data: any) {
  const url = data.id ? `/admin/user/group/update/${data.id}` : '/admin/user/group/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an user group
export async function deleteUserGroup(id: number) {
  return requestClient.delete(`/admin/user/group/delete/${id}`);
}
