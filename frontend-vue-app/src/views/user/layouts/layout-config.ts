/**
 * 布局配置
 */
export const layoutConfig = {
  // ========== 全局配置 ==========
  /** 应用名称 */
  appName: 'Zayum Admin',
  
  /** 内容区域紧凑模式: 'default' | 'compact' | 'wide' */
  contentCompact: 'default' as const,

  // ========== 应用配置 ==========
  app: {
    /** 布局模式 */
    layout: 'sidebar-nav' as 'sidebar-nav' | 'header-nav' | 'mixed-nav' | 'sidebar-mixed-nav' | 'header-mixed-nav' | 'header-sidebar-nav' | 'full-content',
    /** 是否移动端 */
    isMobile: false,
    /** 是否启用偏好设置按钮 */
    enablePreferences: false,
    /** 偏好设置按钮位置: 'auto' | 'fixed' | 'header' */
    preferencesButtonPosition: 'auto' as 'auto' | 'fixed' | 'header',
    /** 登录页面布局: 'panel-left' | 'panel-right' | 'panel-center' */
    authPageLayout: 'panel-left' as const,
    /** 语言 */
    locale: 'zh_CN'
  },

  // ========== 主题配置 ==========
  theme: {
    /** 是否暗黑模式 */
    darkMode: false,
    /** 头部半暗黑 */
    semiDarkHeader: false,
    /** 侧边栏半暗黑 */
    semiDarkSidebar: false
  },

  // ========== 导航配置 ==========
  navigation: {
    /** 是否手风琴模式 */
    accordion: false,
    /** 菜单样式类型: 'default' | 'rounded' */
    styleType: 'default'
  },

  // ========== 面包屑配置 ==========
  breadcrumb: {
    /** 是否启用 */
    enable: true,
    /** 是否隐藏只有一个时 */
    hideOnlyOne:  true,
    /** 是否显示首页 */
    showHome: true,
    /** 是否显示图标 */
    showIcon: true,
    /** 样式类型: 'background' | 'normal' */
    styleType: 'normal' as const
  },

  // ========== 页面元素配置 ==========
  /** Logo配置 */
  logo: {
    /** 是否启用 */
    enable: true,
    /** Logo图片路径 */
    source: '/src/assets/logo-2.svg'
  },

  /** 标签栏配置 */
  tabbar: {
    /** 是否启用 */
    enable: true,
    /** 高度(px) */
    height: 48,
    /** 是否显示图标 */
    showIcon: true
  },

  /** 头部配置 */
  header: {
    /** 是否启用 */
    enable: true,
    /** 是否隐藏 */
    hidden: false,
    /** 模式: 'default' | 'fixed' | 'absolute' */
    mode: 'default',
    /** 主题: 'light' | 'dark' */
    theme: 'light'
  },

  /** 侧边栏配置 */
  sidebar: {
    /** 是否启用 */
    enable: true,
    /** 是否折叠 */
    collapsed: false,
    /** 折叠时是否显示标题 */
    collapsedShowTitle: true,
    /** 是否悬停展开 */
    expandOnHover: true,
    /** 额外菜单是否折叠 */
    extraCollapse: false,
    /** 是否隐藏 */
    hidden: false,
    /** 主题: 'light' | 'dark' */
    theme: 'light',
    /** 宽度(px) */
    width: 210
  },

  /** 小部件配置 */
  widget: {
    /** 是否显示侧边栏切换按钮 */
    sidebarToggle: true
  },

  /** 页脚配置 */
  footer: {
    /** 是否启用 */
    enable: true,
    /** 是否固定定位 */
    fixed: false
  },

  // ========== 版权信息配置 ==========
  copyright: {
    /** 是否启用 */
    enable: true,
    /** 公司名称 */
    companyName: 'Zayum Design',
    /** 公司网站链接 */
    companySiteLink: '',
    /** 版权日期 */
    date: '2025',
    /** ICP备案号 */
    icp: '',
    /** ICP备案链接 */
    icpLink: ''
  },

  // ========== 认证页面配置 ==========
  auth: {
    /** 是否使用暗黑模式 */
    darkMode: false as boolean,
    /** 是否使用左侧面板布局 */
    panelLeft: true,
    /** 是否使用居中面板布局 */
    panelCenter: false,
    /** 是否使用右侧面板布局 */
    panelRight: false,
    /** 版权信息配置 */
    copyright: {
      /** 是否启用 */
      enable: true,
      /** 公司名称 */
      companyName: 'Zayum Design',
      /** 公司网站链接 */
      companySiteLink: '',
      /** 版权日期 */
      date: '2025',
      /** ICP备案号 */
      icp: '',
      /** ICP备案链接 */
      icpLink: ''
    }
  }
}
