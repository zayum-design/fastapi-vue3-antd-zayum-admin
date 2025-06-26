import type { DefaultProps, Props } from 'tippy.js';
import type { App, SetupContext } from 'vue';

import { h, watchEffect } from 'vue';
import { setDefaultProps, Tippy as TippyComponent } from 'vue-tippy';

import { usePreferences } from '@/_core/preferences';
import useTippyDirective from './directive';

import 'tippy.js/dist/tippy.css';
import 'tippy.js/dist/backdrop.css';
import 'tippy.js/themes/light.css';
import 'tippy.js/animations/scale.css';
import 'tippy.js/animations/shift-toward.css';
import 'tippy.js/animations/shift-away.css';
import 'tippy.js/animations/perspective.css';

// 获取用户偏好设置
const { isDark } = usePreferences();

/**
 * Tippy 组件的属性类型
 */
export type TippyProps = Partial<
  Props & {
    animation?:
      | 'fade'
      | 'perspective'
      | 'scale'
      | 'shift-away'
      | 'shift-toward'
      | boolean;
    theme?: 'auto' | 'dark' | 'light';
  }
>;

/**
 * 初始化 Tippy 插件
 * @param app Vue 应用实例
 * @param options 默认 Tippy 配置项
 */
export function initTippy(app: App<Element>, options?: DefaultProps) {
  // 设置 Tippy 默认配置
  setDefaultProps({
    allowHTML: true, // 允许 HTML 内容
    delay: [500, 200], // 延迟显示和隐藏时间
    theme: isDark.value ? '' : 'light', // 主题模式
    ...options,
  });

  // 监听主题模式变化，自动更新 Tippy 主题
  if (!options || !Reflect.has(options, 'theme') || options.theme === 'auto') {
    watchEffect(() => {
      setDefaultProps({ theme: isDark.value ? '' : 'light' });
    });
  }

  // 注册 v-tippy 指令
  app.directive('tippy', useTippyDirective(isDark));
}

/**
 * Tippy 组件封装
 * @param props 组件属性
 * @param attrs 组件属性（Vue 透传属性）
 * @param slots 插槽内容
 * @returns Vue 渲染函数 h()
 */
export const Tippy = (props: any, { attrs, slots }: SetupContext) => {
  let theme: string = (attrs.theme as string) ?? 'auto';

  // 根据用户偏好调整主题
  if (theme === 'auto') {
    theme = isDark.value ? '' : 'light';
  }
  if (theme === 'dark') {
    theme = '';

  }
  
  return h(
    TippyComponent,
    {
      ...props,
      ...attrs,
      theme,
    },
    slots,
  );
};
