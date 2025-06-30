// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchAdminLogItems({
  page = 1,
  perPage = -1,
  search = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/admin/log/list', {
    params: {
      page,
      per_page: perPage,
      search,
    },
  });
}


// Create or update an admin group
export async function saveAdminLog(data: any) {
  const url = data.id ? `/admin/admin/log/update/${data.id}` : '/admin/admin/log/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deleteAdminLog(id: number) {
  return requestClient.delete(`/admin/admin/log/delete/${id}`);
}
