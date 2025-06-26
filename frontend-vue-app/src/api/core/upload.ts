import { requestClient } from '@/api/request';

interface UploadResponse {
  image_url: string;
}

// UploadApi
export async function uploadApi(file: File, sub_dir: string = "images") {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('sub_dir', sub_dir);  // 将 sub_dir 参数添加到 FormData 中

  return requestClient.post<UploadResponse>('/admin/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
}
