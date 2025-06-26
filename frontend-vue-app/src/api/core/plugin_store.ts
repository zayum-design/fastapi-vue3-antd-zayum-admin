import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

export async function fetchPluginStore({
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

export async function installPlugin(id: number) {
  return requestClient.delete(`/admin/plugin/install/${id}`);
}

export async function uninstallPlugin(id: number) {
  return requestClient.delete(`/admin/plugin/uninstall/${id}`);
}

export async function enablePlugin(id: number, enabled: number) {
  return requestClient.put(`/admin/plugin/enable/${id}`, { enabled });
}

export async function purchasePlugin(id: number) {
  return requestClient.post(`/admin/plugin/purchase/${id}`);
}