/** 管理员状态枚举 */
export enum AdminStatus {
  NORMAL = 'normal',
  HIDDEN = 'hidden'
}

/** 管理员信息 */
export interface AdminInfo {
  id: number
  groupId: number
  username: string  // 用户名(20字符限制,只允许字母数字)
  nickname: string  // 昵称(50字符限制,允许字母数字、空格、连字符和点号)
  password?: string // 密码(128字符限制)
  avatar?: string   // 头像URL(255字符限制)
  email: string     // 邮箱(100字符限制)
  mobile: string    // 手机号(11位数字)
  loginFailure: number
  loginAt?: string  // 最后登录时间
  loginIp?: string  // 最后登录IP(50字符限制)
  token?: string    // 认证令牌(512字符限制)
  status: AdminStatus
  createdAt: string
  updatedAt: string
}

/** 管理员创建/更新DTO */
export interface AdminDTO {
  username: string  // 用户名(20字符限制,只允许字母数字)
  nickname: string  // 昵称(50字符限制,允许字母数字、空格、连字符和点号)
  password?: string // 密码(至少8位)
  email: string     // 邮箱(100字符限制)
  mobile: string    // 手机号(11位数字)
  avatar?: string   // 头像URL(255字符限制)
  groupId?: number
  status?: AdminStatus
}

/** 管理员登录DTO */
export interface AdminLoginDTO {
  username: string
  password: string
  remember?: boolean
}

/** 管理员登录响应 */
export interface AdminLoginResponse {
  token: string
  adminInfo: AdminInfo
}
