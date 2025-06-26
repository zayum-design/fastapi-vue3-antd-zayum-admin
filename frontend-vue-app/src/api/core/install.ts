// src/api/core/install.ts
import { requestClient } from '@/api/request';
import {type Success} from '@/_core/types/api';


interface ImportResponse {
  next_table: string | null;
  progress?: string;
  error_table?: string;
}

interface InstallCheckResponse {
  installed: boolean;
}

// 测试数据库连接
export async function installCheck(): Promise<InstallCheckResponse> {
  return requestClient.post<InstallCheckResponse>('/install_check');
}

// 测试数据库连接
export async function testDatabaseConnection(dbForm: any): Promise<String> {
  return requestClient.post<String>('/install/test-db', dbForm);
}

// 导入数据库
export async function importDatabase(dbForm: any, importOptions: string[]): Promise<ImportResponse> {
  return requestClient.post<ImportResponse>('/install/import-db', {
    ...dbForm,
    importOptions
  });
}

// 完成安装
export async function completeInstallation(adminData: any): Promise<Success> {
  return requestClient.post<Success>('/install/complete', adminData);
}

export async function restart(): Promise<Success> {
  return requestClient.post<Success>('/install/restart');
}

import request from "@/utils/request";

export function startImportDb(): Promise<ApiResponse<{
  progress: string;
  next_table: string;
  skipped?: boolean;
}>> {
  return request.post("http://127.0.0.1:8000/api/install/import-db?action=start");
}

import type { ApiResponse } from "@/utils/request";

export function getNextImportDb(): Promise<ApiResponse<{
  progress: string;
  next_table: string;
  skipped?: boolean;
}>> {
  return request.post("http://127.0.0.1:8000/api/install/import-db?action=next");
}
