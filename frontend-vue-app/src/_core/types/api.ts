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
  data: SuccessItemsData;
}

export interface ErrorResponse extends ApiResponseBase {
  code: number; // 非1
  data: ErrorData;
}

export type ApiResponse = SuccessResponse | ErrorResponse;

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
