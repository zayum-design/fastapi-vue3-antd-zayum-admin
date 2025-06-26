<!-- src/components/CodeEditor.vue -->
<template>
    <div ref="editorContainer" class="monaco-editor-container"></div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch, onBeforeUnmount, defineProps, defineEmits } from 'vue';
  import * as monaco from 'monaco-editor';
  
  const props = defineProps({
    code: {
      type: String,
      required: true,
    },
    language: {
      type: String,
      required: true,
    },
  });
  
  const emit = defineEmits(['update:code']);
  
  const editorContainer = ref<HTMLElement | null>(null);
  let editor: monaco.editor.IStandaloneCodeEditor;
  
  onMounted(() => {
    if (editorContainer.value) {
      editor = monaco.editor.create(editorContainer.value, {
        value: props.code,
        language: props.language,
        automaticLayout: true,
        theme: 'vs-light', // 可选：'vs-dark', 'hc-black' 等
      });
  
      // 监听编辑器内容变化
      editor.onDidChangeModelContent(() => {
        const value = editor.getValue();
        emit('update:code', value);
      });
    }
  });
  
  // 监听 `code` 属性变化，更新编辑器内容
  watch(
    () => props.code,
    (newCode) => {
      if (editor && newCode !== editor.getValue()) {
        const model = editor.getModel();
        if (model) {
          editor.pushUndoStop();
          model.setValue(newCode);
          editor.pushUndoStop();
        }
      }
    }
  );
  
  // 清理编辑器实例
  onBeforeUnmount(() => {
    if (editor) {
      editor.dispose();
    }
  });
  </script>
  
  <style scoped>
  .monaco-editor-container {
    width: 100%;
    height: 400px; /* 根据需要调整高度 */
    border: 1px solid #ddd;
    border-radius: 5px;
    overflow: hidden;
  }
  </style>
  