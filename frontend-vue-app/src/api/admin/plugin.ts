// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type ApiResponseComponent, type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchPluginItems({
  page = 1,
  perPage = 10,
  search = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/plugin/list', {
    params: {
      page,
      per_page: perPage,
      search,
    },
  });
}



export async function fetchPluginLists() {
  return requestClient.get<ApiResponseComponent>('/admin/plugin/list');
}


// Create or update an admin group
export async function savePlugin(data: any) {
  const url = data.id ? `/admin/plugin/update/${data.id}` : '/admin/plugin/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deletePlugin(id: number) {
  return requestClient.delete(`/admin/plugin/delete/${id}`);
}
