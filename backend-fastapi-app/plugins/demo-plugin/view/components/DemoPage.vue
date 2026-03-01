<template>
<div class="demo-page">
  <div style="text-align:center; margin: 12px 0; color: #666;">演示插件页面已渲染</div>
    
    <el-card shadow="never">
      <template #header>
        <div style="display: flex; align-items: center;">
          <el-icon style="margin-right: 10px; color: #409EFF;">
            <Promotion />
          </el-icon>
          <span style="font-size: 18px; font-weight: bold;">示例插件</span>
          <el-tag type="success" style="margin-left: 10px;">v1.0.0</el-tag>
        </div>
      </template>
      
      <div style="text-align: center; padding: 40px 20px;">
        <el-icon size="80" color="#409EFF" style="margin-bottom: 20px;">
          <Star />
        </el-icon>
        
        <h1 style="margin-bottom: 30px; color: #333;">
          {{ message || 'Hello World!' }}
        </h1>
        
        <div style="margin-bottom: 30px;">
          <p style="color: #666; line-height: 1.6;">
            这是一个示例插件，展示了插件系统的基本功能。
            消息内容来自后端API接口。
          </p>
        </div>
        
        <el-row :gutter="20" justify="center">
          <el-col :span="8">
            <el-card shadow="hover" style="margin-bottom: 20px;">
              <template #header>
                <div style="text-align: center; font-weight: bold;">
                  <el-icon><Link /></el-icon> API测试
                </div>
              </template>
              <div style="text-align: center;">
                <el-button type="primary" @click="fetchHello" :loading="loading.hello">
                  调用Hello API
                </el-button>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" style="margin-bottom: 20px;">
              <template #header>
                <div style="text-align: center; font-weight: bold;">
                  <el-icon><InfoFilled /></el-icon> 插件信息
                </div>
              </template>
              <div style="text-align: center;">
                <el-button type="info" @click="fetchInfo" :loading="loading.info">
                  获取插件信息
                </el-button>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover" style="margin-bottom: 20px;">
              <template #header>
                <div style="text-align: center; font-weight: bold;">
                  <el-icon><Connection /></el-icon> 健康检查
                </div>
              </template>
              <div style="text-align: center;">
                <el-button type="success" @click="checkHealth" :loading="loading.health">
                  健康检查
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <el-divider></el-divider>
        
        <!-- API响应显示 -->
        <div v-if="apiResponse" style="margin-top: 30px;">
          <h3 style="margin-bottom: 15px;">API响应:</h3>
          <el-card>
            <pre style="text-align: left; overflow: auto; max-height: 300px; padding: 15px; background: #f5f5f5; border-radius: 4px;">{{ apiResponse }}</pre>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Promotion, Star, Link, InfoFilled, Connection } from '@element-plus/icons-vue'

export default {
  name: 'DemoPage',
  components: {
    Promotion,
    Star,
    Link,
    InfoFilled,
    Connection
  },
  data() {
    return {
      message: '',
      loading: {
        hello: false,
        info: false,
        health: false
      },
      apiResponse: null
    }
  },
  mounted() {
    this.fetchHello()
  },
  created() {
    console.log('DemoPage组件创建，$axios可用:', !!this.$axios)
    console.log('组件实例:111111111111111', this)
  },
  methods: {
    async fetchHello() {
      this.loading.hello = true
      try {
        const response = await this.$axios.get('/plugins/demo-plugin/hello')
        this.apiResponse = JSON.stringify(response.data, null, 2)
        if (response.data.code === 0) {
          this.message = response.data.data.message
          this.$message.success('Hello API调用成功5555555')
        }
      } catch (error) {
        console.error('调用Hello API失败:', error)
        this.$message.error('调用API失败')
      } finally {
        this.loading.hello = false
      }
    },
    
    async fetchInfo() {
      this.loading.info = true
      try {
        const response = await this.$axios.get('/plugins/demo-plugin/info')
        this.apiResponse = JSON.stringify(response.data, null, 2)
        this.$message.success('插件信息获取成功')
      } catch (error) {
        console.error('获取插件信息失败:', error)
        this.$message.error('获取插件信息失败')
      } finally {
        this.loading.info = false
      }
    },
    
    async checkHealth() {
      this.loading.health = true
      try {
        const response = await this.$axios.get('/plugins/demo-plugin/health')
        this.apiResponse = JSON.stringify(response.data, null, 2)
        this.$message.success('健康检查成功')
      } catch (error) {
        console.error('健康检查失败:', error)
        this.$message.error('健康检查失败')
      } finally {
        this.loading.health = false
      }
    }
  }
}
</script>

<style scoped>
.demo-page {
  padding: 20px;
}

.el-card {
  border-radius: 8px;
}

.el-card__header {
  border-bottom: 1px solid #f0f0f0;
  padding: 15px 20px;
}

pre {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
