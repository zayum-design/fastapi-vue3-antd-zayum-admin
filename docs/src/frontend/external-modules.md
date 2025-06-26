# 外部模块

## UI框架

### Ant Design Vue
```vue
<template>
  <a-button type="primary">按钮</a-button>
</template>

<script setup>
import { Button } from 'ant-design-vue'
</script>
```

## 图表库

### ECharts
```vue
<template>
  <EchartsUI :option="chartOption" />
</template>

<script setup>
import { EchartsUI } from '@/plugins/echarts'
import { ref } from 'vue'

const chartOption = ref({
  xAxis: {
    type: 'category',
    data: ['Mon', 'Tue', 'Wed']
  },
  yAxis: {
    type: 'value'
  },
  series: [{
    data: [120, 200, 150],
    type: 'bar'
  }]
})
</script>
```

## 日期处理

### Day.js
```javascript
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const now = dayjs().tz('Asia/Shanghai').format('YYYY-MM-DD HH:mm:ss')
```

## 文件处理

### JSZip
```javascript
import JSZip from 'jszip'
import { saveAs } from 'file-saver'

const zip = new JSZip()
zip.file('hello.txt', 'Hello World')
zip.generateAsync({ type: 'blob' }).then(content => {
  saveAs(content, 'example.zip')
})
```

## 网络请求

### Axios
```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: '/api'
})

api.get('/users').then(response => {
  console.log(response.data)
})
```

## 实用工具

### VueUse
```vue
<script setup>
import { useMouse, useTitle } from '@vueuse/core'

const { x, y } = useMouse()
useTitle('新标题')
</script>
```

## 图片裁剪

### Vue Advanced Cropper
```vue
<template>
  <Cropper
    :src="image"
    :stencil-props="{
      aspectRatio: 1
    }"
  />
</template>

<script setup>
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

const image = ref('')
</script>
```

## 最佳实践

1. **按需引入**
   ```javascript
   // 推荐
   import { Button } from 'ant-design-vue'
   
   // 不推荐
   import Antd from 'ant-design-vue'
   ```

2. **统一管理**
   ```javascript
   // src/utils/dayjs.ts
   import dayjs from 'dayjs'
   import utc from 'dayjs/plugin/utc'
   
   dayjs.extend(utc)
   
   export default dayjs
   ```

3. **错误处理**
   ```javascript
   api.get('/data').catch(error => {
     console.error('请求失败:', error)
     message.error('加载失败')
   })
   ```

4. **性能优化**
   ```javascript
   // 懒加载组件
   const Cropper = defineAsyncComponent(() => 
     import('vue-advanced-cropper').then(m => m.Cropper)
   )
