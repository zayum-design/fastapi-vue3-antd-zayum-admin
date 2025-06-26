// src/api/core/admin.ts
import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

// Fetch admin group items
export async function fetchAttachmentItems({
  page = 1,
  perPage = 10,
  search = '',
}: {
  page?: number;
  perPage?: number;
  search?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/attachment/list', {
    params: {
      page,
      per_page: perPage,
      search,
    },
  });
}


// Create or update an admin group
export async function saveAttachment(data: any) {
  const url = data.id ? `/admin/attachment/update/${data.id}` : '/admin/attachment/create';
  return requestClient[data.id ? 'put' : 'post'](url, data);
}

// Delete an admin group
export async function deleteAttachment(id: number) {
  return requestClient.delete(`/admin/attachment/delete/${id}`);
}
