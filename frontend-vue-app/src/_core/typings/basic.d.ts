interface BasicOption {
  label: string;
  value: string;
}

type SelectOption = BasicOption;

type TabOption = BasicOption;

interface BasicAdminInfo {
  /**
   * 头像
   */
  avatar: string;
  /**
   * 用户昵称
   */
  nickname: string;
  /**
   * 用户角色
   */
  groupId?: number;
  /**
   * 用户id
   */
  userId: string;
  /**
   * 用户名
   */
  username: string;
}

type ClassType = Array<object | string> | object | string;

export type { BasicOption, BasicAdminInfo, ClassType, SelectOption, TabOption };
