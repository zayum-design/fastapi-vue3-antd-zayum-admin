/** 用户性别枚举 */
export enum UserGender {
  MALE = 'male',
  FEMALE = 'female'
}

/** 用户状态枚举 */
export enum UserStatus {
  NORMAL = 'normal',
  HIDDEN = 'hidden',
  DELETE = 'delete'
}

/** 用户信息 */
export interface UserInfo {
  id: number
  userGroupId: number
  username: string
  nickname: string
  password?: string
  email: string
  mobile: string
  avatar?: string
  level: number
  gender: UserGender
  birthday?: string
  bio?: string
  balance?: number
  score: number
  successions: number
  maxSuccessions: number
  prevTime?: string
  loginTime?: string
  loginIp?: string
  loginFailure: number
  joinIp?: string
  verification?: string
  token?: string
  status: UserStatus
  createdAt: string
  updatedAt: string
}

/** 用户创建/更新DTO */
export interface UserDTO {
  username: string
  nickname: string
  password?: string
  email: string
  mobile: string
  avatar?: string
  level?: number
  gender?: UserGender
  birthday?: string
  bio?: string
  userGroupId?: number
  status?: UserStatus
}

/** 用户登录DTO */
export interface LoginDTO {
  username: string
  password: string
  remember?: boolean
}

/** 用户登录响应 */
export interface LoginResponse {
  token: string
  userInfo: UserInfo
}
