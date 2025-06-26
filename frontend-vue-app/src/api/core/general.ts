// src/api/core/admin.ts
import { requestClient } from "@/api/request";
import { type SuccessItemsData } from "@/_core/types/api";

// Fetch admin group items
export async function fetchGeneralConfig() {
  return requestClient.get<SuccessItemsData>("/admin/general/config", {});
}

export async function deleteGeneralConfig(id: number) {
  return requestClient.delete(`/admin/general/config/delete/${id}`);
}
export async function createGeneralConfig(payload: any) {
  return requestClient.post("/admin/general/config/create", payload);
}
export async function saveGeneralConfig(payload: any) {
  return requestClient.post("/admin/general/config/save", payload);
}