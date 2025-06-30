import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export async function saveProfileApi(data: any) {
  return axios.post(`${API_BASE_URL}/auth/profile`, data)
}

export async function uploadApi(file: File, type: string) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('type', type)
  return axios.post(`${API_BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
