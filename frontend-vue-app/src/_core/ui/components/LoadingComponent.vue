<!-- src/components/LoadingComponent.vue -->
<template>
    <div class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>
  </template>
  
  <script lang="ts">
  import { defineComponent } from 'vue'
  
  export default defineComponent({
    name: 'LoadingComponent'
  })
  </script>
  
  <style scoped>
  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px;
  }
  
  .spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #42b983;
    animation: spin 1s linear infinite;
    margin-bottom: 10px;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .loading p {
    font-size: 16px;
    color: #42b983;
  }
  </style>
  