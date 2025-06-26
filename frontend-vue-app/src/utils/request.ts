// 👇 request.ts（最终版本）
import axios, {
    type AxiosInstance,
    type AxiosResponse,
    type InternalAxiosRequestConfig
  } from "axios";
  import { message } from "ant-design-vue";
  
  export interface ApiResponse<T = any> {
    code: number;
    data: T;
    msg: string;
  }
  
  const request: AxiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
    timeout: 10000,
    headers: {
      "Content-Type": "application/json",
    },
  });
  
  // ✅ 请求拦截器
  request.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = localStorage.getItem("token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );
  
  // ✅ 响应拦截器：只返回 res.data，但用类型断言处理
  request.interceptors.response.use(
    (response: AxiosResponse<ApiResponse>) => {
      const res = response.data;
      if (res.code !== 200 && res.code !== 0) {
        message.error(res.msg || "请求失败");
        return Promise.reject(res);
      }
      // 👇 这里做断言或调整函数返回类型
      return res as any;
    },
    (error) => {
      if (error.response) {
        message.error(error.response.data?.msg || "服务器错误");
      } else if (error.message.includes("timeout")) {
        message.error("请求超时，请稍后重试");
      } else {
        message.error("网络错误");
      }
      return Promise.reject(error);
    }
  );
  
  export default request;
