// src/api/user/score_log.ts
import { userRequestClient } from './request';
import type { SuccessItemsData } from '@/_core/types/api';

// Fetch current user's score log items
export async function fetchUserScoreLogItems({
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
  return userRequestClient.get<SuccessItemsData>('/user/score/log/list', {
    params: {
      page,
      per_page: perPage,
      search,
      orderby,
    },
  });
}

// Get a single score log item
export async function getUserScoreLog(id: number) {
  return userRequestClient.get(`/user/score/log/${id}`);
}
