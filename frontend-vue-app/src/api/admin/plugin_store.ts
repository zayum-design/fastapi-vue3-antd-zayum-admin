import { requestClient } from '@/api/request';
import { type SuccessItemsData } from '@/_core/types/api';

export async function fetchPluginStore({
  page = 1,
  perPage = 10,
  search = '',
  type = 'all', // all, store, local
}: {
  page?: number;
  perPage?: number;
  search?: string;
  type?: string;
}) {
  return requestClient.get<SuccessItemsData>('/admin/plugin_store/list', {
    params: {
      page,
      per_page: perPage,
      search,
      type,
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