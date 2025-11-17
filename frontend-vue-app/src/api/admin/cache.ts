import { requestClient } from '@/api/request';

export namespace CacheApi {
  /** 清除缓存接口返回值 */
  export interface ClearCacheResult {
    message: string;
  }
}

/**
 * 清除分析数据缓存
 */
export async function clearAnalyticsCacheApi() {
  return requestClient.post<CacheApi.ClearCacheResult>('/admin/cache/clear');
}
