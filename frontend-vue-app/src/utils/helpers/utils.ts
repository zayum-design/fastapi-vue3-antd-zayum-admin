// utils.ts

// 创建一个映射用于处理特殊词汇
const specialCases = new Map<string, string>([
  ['id', 'ID'],
  ['ip', 'IP'], // 如果还有其他需要特别处理的词，可以继续添加
  // 可以根据需求添加更多特殊情况
]);

/**
 * 将下划线分隔的字符串转换为标题格式
 * @param str - 需要转换的字符串
 * @returns 转换后的标题格式字符串
 */
export function convertToTitleCase(str: string): string {
  return str.split('_')
            .map(word => {
              // 检查是否有特殊处理规则，如果有则应用之
              if (specialCases.has(word.toLowerCase())) {
                return specialCases.get(word.toLowerCase())!;
              }
              // 否则按照常规首字母大写处理
              return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
            })
            .join(' ');
}