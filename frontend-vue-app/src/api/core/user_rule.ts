// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchUserRuleItems({
  page = 1,
  perPage = 10,
  search = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/user/rule/list', {
    params: {
      page,
      per_page: perPage,
      search,
    },
  });
}


// Create or update an admin group
export async function saveUserRule(data: any) {
  const url = data.id ? `/admin/user/rule/update/${data.id}` : '/admin/user/rule/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deleteUserRule(id: number) {
  return requestClient.delete(`/admin/user/rule/delete/${id}`);
}
