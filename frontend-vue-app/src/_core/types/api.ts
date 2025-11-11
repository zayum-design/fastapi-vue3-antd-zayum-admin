// src/types/api.ts

export interface ApiResponseBase {
  code: number;
  msg: string;
}

export interface ApiResponseComponent {
  code: number;
  msg: string;
}

export interface SuccessItemsData {
  items: [];
  total: number;
  page: number;
  per_page: number;
}

export interface Success {
  data: any;
  msg: string;
  code: number;
}


export interface ErrorData {
  errors: { message: string }[];
}

export interface SuccessResponse extends ApiResponseBase {
  code: 0;
  data: any;
}

export interface ErrorResponse extends ApiResponseBase {
  code: number; // 非1
  data: ErrorData;
}

export type ApiResponse = SuccessResponse | ErrorResponse;

// Analytics related interfaces
export interface MonthlyLoginData {
  month: string;
  count: number;
}

export interface AnalyticsOverviewData {
  totalUsers: number;
  activeUsers: number;
  newUsers: number;
  totalVisits: number;
  bounceRate: number;
  avgSessionDuration: number;
}

export interface AnalyticsTrendsData {
  userTrends: Array<{
    date: string;
    count: number;
  }>;
  visitTrends: Array<{
    date: string;
    count: number;
  }>;
}

export interface AnalyticsVisitsData {
  period: string;
  visits: number;
  uniqueVisitors: number;
  pageViews: number;
  avgDuration: number;
}

export interface AnalyticsSourcesData {
  source: string;
  visits: number;
  percentage: number;
}

export interface AnalyticsRegionsData {
  region: string;
  visits: number;
  percentage: number;
}

/**
 * 类型守卫：判断是否为 SuccessResponse
 * @param response - API 响应
 * @returns 如果是 SuccessResponse 则返回 true
 */
export function isSuccessResponse(
  response: ApiResponse
): response is SuccessResponse {
  return response.code === 0;
}

/**
 * 类型守卫：判断是否为 ErrorResponse
 * @param response - API 响应
 * @returns 如果是 ErrorResponse 则返回 true
 */
export function isErrorResponse(
  response: ApiResponse
): response is ErrorResponse {
  return response.code !== 0;
}
