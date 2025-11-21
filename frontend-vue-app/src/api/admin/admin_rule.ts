// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchAdminRuleItems({
  page = 1,
  perPage = -1,
  search = '',
  orderby = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
  orderby?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/admin/rule/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}


// Create or update an admin group
export async function saveAdminRule(data: any) {
  const url = data.id ? `/admin/admin/rule/update/${data.id}` : '/admin/admin/rule/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deleteAdminRule(id: number) {
  return requestClient.delete(`/admin/admin/rule/delete/${id}`);
}
