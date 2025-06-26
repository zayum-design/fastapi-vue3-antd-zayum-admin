import type { ComputedRef, Directive } from 'vue';
import { useTippy } from 'vue-tippy';

/**
 * 自定义 Vue 指令封装 Tippy.js 以提供提示功能
 * 
 * @param isDark - 计算属性，判断当前是否处于暗黑模式
 * @returns 自定义指令
 */
export default function useTippyDirective(isDark: ComputedRef<boolean>) {
  const directive: Directive = {
    // 指令绑定到元素时调用
    mounted(el, binding, vnode) {
      // 获取绑定的选项
      const opts =
        typeof binding.value === 'string'
          ? { content: binding.value } // 如果绑定值是字符串，则作为提示内容
          : binding.value || {}; // 否则使用对象值

      // 处理指令修饰符
      const modifiers = Object.keys(binding.modifiers || {});
      const placement = modifiers.find((modifier) => modifier !== 'arrow'); // 获取方位修饰符
      const withArrow = modifiers.includes('arrow'); // 是否显示箭头

      // 设置提示的显示方位
      if (placement) {
        opts.placement = opts.placement || placement;
      }

      // 设置箭头显示
      if (withArrow) {
        opts.arrow = opts.arrow === undefined ? true : opts.arrow;
      }

      // 处理事件监听
      if (vnode.props) {
        if (vnode.props.onTippyShow) {
          opts.onShow = (...args: any[]) => vnode.props?.onTippyShow(...args);
        }
        if (vnode.props.onTippyShown) {
          opts.onShown = (...args: any[]) => vnode.props?.onTippyShown(...args);
        }
        if (vnode.props.onTippyHide) {
          opts.onHide = (...args: any[]) => vnode.props?.onTippyHide(...args);
        }
        if (vnode.props.onTippyHidden) {
          opts.onHidden = (...args: any[]) => vnode.props?.onTippyHidden(...args);
        }
        if (vnode.props.onTippyMount) {
          opts.onMount = (...args: any[]) => vnode.props?.onTippyMount(...args);
        }
      }

      // 获取元素的 `title` 或 `content` 作为提示内容
      if (el.getAttribute('title') && !opts.content) {
        opts.content = el.getAttribute('title');
        el.removeAttribute('title'); // 避免默认浏览器提示
      }

      if (el.getAttribute('content') && !opts.content) {
        opts.content = el.getAttribute('content');
      }

      // 应用 Tippy.js
      useTippy(el, opts);
    },

    // 指令解绑时调用，销毁 Tippy 实例
    unmounted(el) {
      if (el.$tippy) {
        el.$tippy.destroy();
      } else if (el._tippy) {
        el._tippy.destroy();
      }
    },

    // 组件更新时调用，更新 Tippy 配置
    updated(el, binding) {
      // 重新获取绑定值，并根据主题模式更新 `theme`
      const opts =
        typeof binding.value === 'string'
          ? { content: binding.value, theme: isDark.value ? '' : 'light' }
          : Object.assign({ theme: isDark.value ? '' : 'light' }, binding.value);

      // 再次检查 `title` 或 `content` 作为提示内容
      if (el.getAttribute('title') && !opts.content) {
        opts.content = el.getAttribute('title');
        el.removeAttribute('title');
      }

      if (el.getAttribute('content') && !opts.content) {
        opts.content = el.getAttribute('content');
      }

      // 更新 Tippy 实例的配置
      if (el.$tippy) {
        el.$tippy.setProps(opts || {});
      } else if (el._tippy) {
        el._tippy.setProps(opts || {});
      }
    },
  };

  return directive;
}
