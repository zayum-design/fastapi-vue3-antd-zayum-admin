// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchAdminItems({
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
  return requestClient.get<SuccessItemsData>('/admin/admin/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}


// Create or update an admin group
export async function saveAdmin(data: any) {
  const url = data.id ? `/admin/admin/update/${data.id}` : '/admin/admin/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deleteAdmin(id: number) {
  return requestClient.delete(`/admin/admin/delete/${id}`);
}
