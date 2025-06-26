// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchGeneralCategoryItems({
  page = 1,
  perPage = 10,
  search = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/general/category/list', {
    params: {
      page,
      per_page: perPage,
      search,
    },
  });
}


// Create or update an admin group
export async function saveGeneralCategory(data: any) {
  const url = data.id ? `/admin/general/category/update/${data.id}` : '/admin/general/category/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deleteGeneralCategory(id: number) {
  return requestClient.delete(`/admin/general/category/delete/${id}`);
}
