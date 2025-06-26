<!-- src/components/CodeBlock.vue -->
<template>
  <div class="monaco-editor-container">
    <div ref="editorContainer" class="editor"></div>
    <a-button class="copy-button" size="small" @click="copyCode" :loading="isCopying" :disabled="isCopying" aria-label="复制代码">
      复制代码
    </a-button>
    <a-message v-if="snackbar" type="success" show-icon>
      代码已复制！
    </a-message>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, onBeforeUnmount, ref, watch, defineProps } from 'vue';
import monaco from '@/monaco'; // 导入配置好的 Monaco 实例

// 定义 props
const props = defineProps<{
  code: string;
  language: string;
  height?: string;
  width?: string;
}>();

const editorContainer = ref<HTMLElement | null>(null);
let editorInstance: monaco.editor.IStandaloneCodeEditor | null = null;

// 状态管理
const isCopying = ref(false);
const copyIcon = ref('mdi-content-copy'); // 默认图标
const snackbar = ref(false);

// 初始化 Monaco Editor
onMounted(() => {
  if (editorContainer.value) {
    editorInstance = monaco.editor.create(editorContainer.value, {
      value: props.code,
      language: props.language,
      readOnly: true,
      minimap: { enabled: false },
      automaticLayout: true,
      scrollBeyondLastLine: false,
      wordWrap: 'on',
      theme: 'vs-light', // 可选 'vs-dark'
      fontSize: 14,
      fontFamily: 'Roboto, sans-serif',
      lineNumbers: 'on',
      renderLineHighlight: 'none',
    });
  }
});

// 销毁 Monaco Editor 实例
onBeforeUnmount(() => {
  if (editorInstance) {
    editorInstance.dispose();
    editorInstance = null;
  }
});

// 监听代码或语言的变化，更新编辑器内容
watch(
  () => [props.code, props.language],
  ([newCode, newLanguage]) => {
    if (editorInstance) {
      const currentModel = editorInstance.getModel();
      if (currentModel) {
        if (monaco.languages.getLanguages().some(lang => lang.id === newLanguage)) {
          monaco.editor.setModelLanguage(currentModel, newLanguage);
        } else {
          console.warn(`Monaco Editor 不支持语言: ${newLanguage}`);
        }
        editorInstance.setValue(newCode);
      }
    }
  }
);

// 复制代码功能
const copyCode = async () => {
  if (isCopying.value) return;

  isCopying.value = true;
  copyIcon.value = 'mdi-check'; // 更改图标以指示成功

  try {
    await navigator.clipboard.writeText(props.code);
    snackbar.value = true; // 显示 Snackbar
  } catch (error) {
    console.error('复制失败:', error);
  }

  // 恢复图标和状态
  setTimeout(() => {
    copyIcon.value = 'mdi-content-copy';
    isCopying.value = false;
  }, 1000);
};
</script>

<style scoped>
.monaco-editor-container {
  position: relative;
  width: 100%;
  height: 400px;
  /* 可根据需要调整 */
  border-radius: 5px;
  overflow: hidden;
}

.editor {
  width: 100%;
  height: 100%;
}

.copy-button {
  position: absolute;
  top: 10px;
  right: 10px; 
  border-radius: 4px;
}

.copy-button:hover {
  background-color: rgba(255, 255, 255, 1);
}
</style>
