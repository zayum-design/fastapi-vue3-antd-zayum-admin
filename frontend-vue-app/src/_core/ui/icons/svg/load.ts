// 引入图标组件的结构类型定义，用于后续指定svg图标的结构
import type { IconifyIconStructure } from '@/_core/ui/icons/icons';

// 引入添加图标的函数，用于注册解析后的svg图标，使其可以作为组件使用
import { addIcon } from '@/_core/ui/icons/icons';

// 定义一个变量，标识svg图标是否已经加载过，防止重复加载
let loaded = false;

// 检查svg图标是否已加载，如果未加载则调用加载函数，并更新状态
if (!loaded) {
  loadSvgIcons(); // 调用加载svg图标的函数
  loaded = true;  // 标记为已加载，防止后续重复加载
}

/**
 * 解析传入的svg字符串数据，将其转换为Iconify图标组件所需的结构体
 *
 * @param svgData - svg图像的原始字符串数据
 * @returns 返回一个符合IconifyIconStructure结构的对象，其中包含：
 *   - body: svg内部的所有元素节点拼接成的字符串
 *   - left: viewBox属性中定义的左边界值
 *   - top: viewBox属性中定义的上边界值
 *   - width: viewBox属性中定义的宽度
 *   - height: viewBox属性中定义的高度
 */
function parseSvg(svgData: string): IconifyIconStructure {
  // 创建一个DOM解析器实例，用于将svg字符串解析为DOM结构
  const parser = new DOMParser();
  // 使用DOM解析器将svg字符串转换为XML文档对象，指定解析的内容类型为'image/svg+xml'
  const xmlDoc = parser.parseFromString(svgData, 'image/svg+xml');
  // 获取XML文档的根节点，即svg元素
  const svgElement = xmlDoc.documentElement;

  // 遍历svg元素的所有子节点，过滤出节点类型为元素的节点，
  // 然后使用XMLSerializer将每个元素节点转换为字符串，最后将所有字符串拼接为一个完整的svg内部内容
  const svgContent = [...svgElement.childNodes]
    .filter((node) => node.nodeType === Node.ELEMENT_NODE) // 筛选出所有元素节点
    .map((node) => new XMLSerializer().serializeToString(node)) // 将每个元素节点序列化为字符串
    .join(''); // 拼接所有序列化后的字符串，形成完整的svg内容

  // 从svg元素中获取viewBox属性的值，viewBox定义了svg的视口位置和尺寸
  const viewBoxValue = svgElement.getAttribute('viewBox') || '';
  // 按空格拆分viewBox字符串，获取左边界、上边界、宽度和高度四个数值
  const [left, top, width, height] = viewBoxValue.split(' ').map((val) => {
    const num = Number(val); // 尝试将每个部分转换为数字
    return Number.isNaN(num) ? undefined : num; // 如果转换失败则返回undefined，否则返回转换后的数字
  });

  // 返回符合IconifyIconStructure结构的对象
  return {
    body: svgContent, // svg内部拼接后的内容
    height,          // 从viewBox中解析出的高度
    left,            // 从viewBox中解析出的左边界
    top,             // 从viewBox中解析出的上边界
    width,           // 从viewBox中解析出的宽度
  };
}

/**
 * 自定义的svg图片转换为组件的加载函数
 *
 * 该异步函数通过Vite的import.meta.glob方法批量加载指定目录下所有svg图标文件，
 * 并将每个svg文件的原始内容解析后注册为图标组件，使其可以直接在项目中使用。
 *
 * @example 使用方法:
 *   ./svg/avatar.svg 对应 <Icon icon="svg:avatar"></Icon>
 */
async function loadSvgIcons() {
  // 使用import.meta.glob批量加载'./icons/'目录下所有文件，
  // 参数配置：
  //   - eager: true 表示同步加载所有文件
  //   - query: '?raw' 表示以原始文本形式加载文件内容
  const svgEagers = import.meta.glob('./icons/**', {
    eager: true,
    query: '?raw',
  });

  // 遍历所有加载的svg文件，使用Promise.all确保所有图标都被处理完成
  await Promise.all(
    Object.entries(svgEagers).map((svg) => {
      // 解构获取文件路径(key)和文件内容(body)
      // 文件内容可能直接是字符串，也可能是包含default属性的对象
      const [key, body] = svg as [string, string | { default: string }];

      // 解析文件路径，提取文件名作为图标名称
      // 示例: './icons/xxxx.svg' 提取出 'xxxx'
      const start = key.lastIndexOf('/') + 1; // 获取最后一个斜杠后的位置，作为文件名起始索引
      const end = key.lastIndexOf('.');         // 获取最后一个点的位置，作为文件名结束位置
      const iconName = key.slice(start, end);   // 截取文件名部分

      // 注册图标：
      //   - 图标名称格式为 'svg:iconName'
      //   - 解析svg文件内容，得到符合IconifyIconStructure结构的对象
      //   - 使用addIcon函数将图标注册到系统中
      return addIcon(`svg:${iconName}`, {
        ...parseSvg(typeof body === 'object' ? body.default : body),
      });
    }),
  );
}
