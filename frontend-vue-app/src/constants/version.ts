/**
 * 项目版本号
 * 从全局变量或 VERSION 文件读取，如果读取失败则使用默认值
 */
export const PROJECT_VERSION = (() => {
  try {
    // 首先尝试从全局变量读取（由 vite 插件注入）
    if (typeof window !== 'undefined' && window.__ZAYUM_ADMIN_METADATA__) {
      return window.__ZAYUM_ADMIN_METADATA__.version || 'unknown';
    }
    
    // 在开发环境中，尝试通过 fetch 获取 VERSION 文件
    if (import.meta.env.DEV) {
      return 'unknown'; // 开发环境默认值
    }
    
    return 'unknown';
  } catch (error) {
    console.warn('Failed to read version:', error);
    return 'unknown';
  }
})();

/**
 * 获取版本号的函数（异步方式）
 */
export async function getProjectVersion(): Promise<string> {
  try {
    // 首先检查全局变量
    if (typeof window !== 'undefined' && window.__ZAYUM_ADMIN_METADATA__) {
      return window.__ZAYUM_ADMIN_METADATA__.version || 'unknown';
    }
    
    // 尝试从 /VERSION 路径获取
    const response = await fetch('/VERSION');
    if (response.ok) {
      const version = await response.text();
      return version.trim();
    }
  } catch (error) {
    console.warn('Failed to fetch version:', error);
  }
  
  // 回退到默认值
  return PROJECT_VERSION;
}

// 类型声明
declare global {
  interface Window {
    __ZAYUM_ADMIN_METADATA__?: {
      version: string;
      authorEmail: string;
      authorName: string;
      authorUrl: string;
      buildTime: string;
      dependencies: Record<string, string>;
      description: string;
      devDependencies: Record<string, string>;
      homepage: string;
      license: string;
      repositoryUrl: string;
    };
  }
}
