// src/api/user/balance_log.ts
import { userRequestClient } from './request';
import type { SuccessItemsData } from '@/_core/types/api';

// Fetch current user's balance log items
export async function fetchUserBalanceLogItems({
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
  return userRequestClient.get<SuccessItemsData>('/user/balance/log/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}

// Get a single balance log item
export async function getUserBalanceLog(id: number) {
  return userRequestClient.get(`/user/balance/log/${id}`);
}
