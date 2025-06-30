// src/api/core/user.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch user group items
export async function fetchUserBalanceLogItems({
  page = 1,
  perPage = 10,
  search = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/user/balance/log/list', {
    params: {
      page,
      per_page: perPage,
      search,
    },
  });
}


// Create or update an user group
export async function saveUserBalanceLog(data: any) {
  const url = data.id ? `/admin/user/balance/log/update/${data.id}` : '/admin/user/balance/log/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an user group
export async function deleteUserBalanceLog(id: number) {
  return requestClient.delete(`/admin/user/balance/log/delete/${id}`);
}
