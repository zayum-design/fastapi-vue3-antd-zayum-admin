// src/api/core/user.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch user group items
export async function fetchUserItems({
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
  return requestClient.get<SuccessItemsData>('/admin/user/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}


// Create or update an user group
export async function saveUser(data: any) {
  const url = data.id ? `/admin/user/update/${data.id}` : '/admin/user/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an user group
export async function deleteUser(id: number) {
  return requestClient.delete(`/admin/user/delete/${id}`);
}
