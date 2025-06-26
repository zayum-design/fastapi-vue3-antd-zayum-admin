/* 从 'radix-vue' 模块中导入 AsTag 类型，用于指定渲染元素的类型 */
import type { AsTag } from 'radix-vue';

/* 从 Vue 框架中导入 Component 类型，用于指定组件类型 */
import type { Component } from 'vue';

/* 从 '../../ui' 模块中导入 ButtonVariants 和 ButtonVariantSize 类型，
   分别用于指定按钮的样式变体和尺寸 */
import type { ButtonVariants, ButtonVariantSize } from '../../ui';

/* 定义一个接口 ZayumButtonProps，用于描述 ZayumButton 组件的属性 */
export interface ZayumButtonProps {
  /**
   * 指定组件应当渲染为哪个 HTML 元素或 Vue 组件，
   * 可选值为 AsTag 或 Component 类型。
   * 当设置 asChild 属性为 true 时，该属性可以被覆盖。
   * @defaultValue "div"
   */
  as?: AsTag | Component;
  
  /**
   * 当设置为 true 时，表示将默认的渲染元素替换为传入的子元素，
   * 并且会将子元素的属性和行为进行合并。
   *
   * 更多详细信息，请参阅我们的 [Composition](https://www.radix-vue.com/guides/composition.html) 指南。
   */
  asChild?: boolean;
  
  // 可选的 class 属性，用于添加自定义 CSS 类。类型为 any，允许灵活传入各种值。
  class?: any;
  
  // 可选的 disabled 属性，指示按钮是否处于禁用状态，
  // 当为 true 时，用户将无法与该组件进行交互。
  disabled?: boolean;
  
  // 可选的 loading 属性，指示组件是否处于加载状态，
  // 通常在异步操作期间使用以显示加载指示。
  loading?: boolean;
  
  // 可选的 size 属性，用于设置按钮的尺寸，
  // 类型为 ButtonVariantSize，通常定义如 small、medium、large 等尺寸选项。
  size?: ButtonVariantSize;
  
  // 可选的 variant 属性，用于设置按钮的样式变体，
  // 类型为 ButtonVariants，通常定义如 primary、secondary 等风格。
  variant?: ButtonVariants;
}
