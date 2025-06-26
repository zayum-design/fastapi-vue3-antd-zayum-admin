import type {
  AnyZodObject,
  ZodDefault,
  ZodEffects,
  ZodNumber,
  ZodString,
  ZodTypeAny,
} from 'zod';

import { isObject, isString } from '@/_core/shared/utils';

/**
 * 获取 Zod 类型的最底层规则。
 * 这会解包可选类型、细化类型等。
 * @param schema 任意 Zod 对象或 Zod 类型
 * @returns 返回基础的 Zod 类型或空
 */
export function getBaseRules<
  ChildType extends AnyZodObject | ZodTypeAny = ZodTypeAny,
>(schema: ChildType | ZodEffects<ChildType>): ChildType | null {
  if (!schema || isString(schema)) return null; // 如果 schema 为空或为字符串，则返回空
  if ('innerType' in schema._def) // 如果定义中有内部类型
    return getBaseRules(schema._def.innerType as ChildType);

  if ('schema' in schema._def) // 如果定义中有 schema 属性
    return getBaseRules(schema._def.schema as ChildType);

  return schema as ChildType; // 返回当前 Zod 类型
}

/**
 * 在 Zod 类型栈中寻找“ZodDefault”，返回其默认值。
 * @param schema 任意 Zod 类型
 * @returns 返回默认值或未定义
 */
export function getDefaultValueInZodStack(schema: ZodTypeAny): any {
  if (!schema || isString(schema)) {
    return;
  }
  const typedSchema = schema as unknown as ZodDefault<ZodNumber | ZodString>;

  if (typedSchema._def.typeName === 'ZodDefault') // 如果是 ZodDefault 类型
    return typedSchema._def.defaultValue(); // 返回默认值

  if ('innerType' in typedSchema._def) { // 如果有内部类型
    return getDefaultValueInZodStack(
      typedSchema._def.innerType as unknown as ZodTypeAny,
    );
  }
  if ('schema' in typedSchema._def) { // 如果定义中有 schema 属性
    return getDefaultValueInZodStack(
      (typedSchema._def as any).schema as ZodTypeAny,
    );
  }

  return undefined; // 如果没有找到，默认返回 undefined
}

/**
 * 判断一个对象是否像事件对象。
 * @param obj 任意对象
 * @returns 布尔值，如果对象有 target 和 stopPropagation 属性，则返回真
 */
export function isEventObjectLike(obj: any) {
  if (!obj || !isObject(obj)) {
    return false;
  }
  return Reflect.has(obj, 'target') && Reflect.has(obj, 'stopPropagation');
}
