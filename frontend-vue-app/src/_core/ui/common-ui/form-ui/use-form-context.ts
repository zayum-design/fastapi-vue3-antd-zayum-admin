// 从 zod 中导入 ZodRawShape 类型，用于描述 zod 验证规则对象的结构
import type { ZodRawShape } from 'zod';

// 从 vue 中导入 ComputedRef 类型，用于描述计算属性的引用类型
import type { ComputedRef } from 'vue';

// 从本地 types 文件中导入 ExtendedFormApi、FormActions 以及 ZayumFormProps 类型定义
import type { ExtendedFormApi, FormActions, ZayumFormProps } from './types';

// 从 vue 中导入 computed、unref 和 useSlots 函数
import { computed, unref, useSlots } from 'vue';

// 从 shadcn-ui 中导入 createContext，用于创建组件上下文
import { createContext } from '@/_core/ui/common-ui/shadcn-ui';
// 从共享工具函数中导入 isString，用于判断一个值是否为字符串
import { isString } from '@/_core/shared/utils';

// 从 vee-validate 中导入 useForm，用于表单验证和处理
import { useForm } from 'vee-validate';
// 从 zod 中导入 object，用于构建 zod 对象模式
import { object } from 'zod';
// 从 zod-defaults 中导入 getDefaultsForSchema，用于从 zod schema 获取默认值
import { getDefaultsForSchema } from 'zod-defaults';

// 定义 ExtendFormProps 类型，继承自 ZayumFormProps，并增加一个 formApi 属性，类型为 ExtendedFormApi
type ExtendFormProps = ZayumFormProps & { formApi: ExtendedFormApi };

// 使用 createContext 创建一个上下文，泛型参数为一个包含两项的元组：
// 第一项可以是 ExtendFormProps 的计算属性或直接对象，第二项为 FormActions 类型
// 这里传入的 'ZayumFormProps' 是上下文的标识符
export const [injectFormProps, provideFormProps] =
  createContext<[ComputedRef<ExtendFormProps> | ExtendFormProps, FormActions]>(
    'ZayumFormProps',
  );

// 定义 useFormInitial 函数，用于初始化表单相关逻辑
// 参数 props 可以是 ComputedRef<ZayumFormProps> 或直接的 ZayumFormProps 对象
export function useFormInitial(
  props: ComputedRef<ZayumFormProps> | ZayumFormProps,
) {
  // 使用 vue 的 useSlots 函数获取当前组件的插槽信息
  const slots = useSlots();
  // 调用 generateInitialValues 函数生成表单的初始值对象
  const initialValues = generateInitialValues();

  // 使用 vee-validate 的 useForm 初始化表单
  // 如果 initialValues 对象有键，则将其作为初始值传入表单，否则不传入初始值
  const form = useForm({
    ...(Object.keys(initialValues)?.length ? { initialValues } : {}),
  });

  // 定义 delegatedSlots 计算属性，用于过滤出除 default 插槽之外的所有插槽名称
  const delegatedSlots = computed(() => {
    // 定义一个数组用于存储过滤后的插槽名称
    const resultSlots: string[] = [];

    // 遍历所有插槽的键名
    for (const key of Object.keys(slots)) {
      // 如果插槽名称不是 'default'，则将其添加到结果数组中
      if (key !== 'default') {
        resultSlots.push(key);
      }
    }
    // 返回过滤后的插槽名称数组
    return resultSlots;
  });

  // 定义 generateInitialValues 函数，用于生成表单初始值
  function generateInitialValues() {
    // 定义一个空对象 initialValues，用于存储字段的初始值
    const initialValues: Record<string, any> = {};

    // 定义一个空的 zodObject 对象（类型为 ZodRawShape），用于存储 zod 验证规则
    const zodObject: ZodRawShape = {};
    // 遍历 props 中的 schema 数组（如果不存在则使用空数组）
    (unref(props).schema || []).forEach((item) => {
      // 如果当前字段对象包含 defaultValue 属性，则将该默认值赋给 initialValues 对应的字段
      if (Reflect.has(item, 'defaultValue')) {
        initialValues[item.fieldName] = item.defaultValue;
      } else if (item.rules && !isString(item.rules)) {
        // 否则如果存在 rules 属性且该属性不是字符串，则将该规则存入 zodObject 中
        zodObject[item.fieldName] = item.rules;
      }
    });

    // 利用 zod 的 object 方法创建一个 schema 对象，并调用 getDefaultsForSchema 获取 schema 定义的默认值
    const schemaInitialValues = getDefaultsForSchema(object(zodObject));

    // 返回 initialValues 和 schemaInitialValues 合并后的对象，确保所有初始值都被包含
    return { ...initialValues, ...schemaInitialValues };
  }

  // 返回包含 delegatedSlots 和 form 对象的对象，供组件内部使用
  return {
    delegatedSlots,
    form,
  };
}
