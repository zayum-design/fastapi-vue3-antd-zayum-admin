import * as monaco from 'monaco-editor';

// 注册 Monaco Editor 的 Python 语言
monaco.languages.register({ id: 'python' });

// 定义主题（可选）
monaco.editor.defineTheme('vs-light-custom', {
  base: 'vs',
  inherit: true,
  rules: [
    { token: 'keyword', foreground: '0000FF', fontStyle: 'bold' },
    { token: 'type.identifier', foreground: '800080' },
    { token: 'number', foreground: '098658' },
    { token: 'string', foreground: 'A31515' },
    { token: 'comment', foreground: '008000', fontStyle: 'italic' },
    { token: 'operator', foreground: '000000' },
    { token: 'delimiter', foreground: '000000' },
  ],
  colors: {
    'editor.background': '#FFFFFF',
  },
});

// 设置默认主题
monaco.editor.setTheme('vs-light-custom');

export default monaco;
