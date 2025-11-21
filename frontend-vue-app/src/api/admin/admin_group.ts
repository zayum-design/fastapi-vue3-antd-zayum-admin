// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchAdminGroupItems({
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
  return requestClient.get<SuccessItemsData>('/admin/admin/group/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}


// Create or update an admin group
export async function saveAdminGroup(data: any) {
  // Just ensure rules and access are arrays (no conversion needed)
  const processedData = {
    ...data,
    rules: Array.isArray(data.rules) ? data.rules : data.rules,
    access: Array.isArray(data.access) ? data.access : data.access
  };
  
  const url = data.id ? `/admin/admin/group/update/${data.id}` : '/admin/admin/group/create';
  return requestClient[data.id ? 'put' : 'post'](url, processedData);
}

// Delete an admin group
export async function deleteAdminGroup(id: number) {
  return requestClient.delete(`/admin/admin/group/delete/${id}`);
}
