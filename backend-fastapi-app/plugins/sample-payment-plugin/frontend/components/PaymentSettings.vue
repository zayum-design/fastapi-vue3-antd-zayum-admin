<template>
  <div class="payment-settings">
    <h2>支付设置 (远程组件)888</h2>
    <div class="settings-form">
      <div class="form-group">
        <label>支付网关:</label>
        <select v-model="settings.gateway">
          <option value="wechat">微信支付</option>
          <option value="alipay">支付宝</option>
          <option value="bank">银行卡</option>
        </select>
      </div>

      <div class="form-group">
        <label>商户ID:</label>
        <input
          type="text"
          v-model="settings.merchantId"
          placeholder="请输入商户ID"
        />
      </div>

      <div class="form-group">
        <label>API密钥:</label>
        <input
          type="password"
          v-model="settings.apiKey"
          placeholder="请输入API密钥"
        />
      </div>

      <div class="form-group">
        <label>回调URL:</label>
        <input
          type="text"
          v-model="settings.callbackUrl"
          placeholder="请输入回调URL"
        />
      </div>

      <button
        class="btn-primary"
        :disabled="loading"
        @click="saveSettings"
      >
        {{ loading ? '保存中...' : '保存设置' }}
      </button>

      <div v-if="message" :class="['message', messageType]">
        {{ message }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PaymentSettings',
  data() {
    return {
      settings: {
        gateway: 'wechat',
        merchantId: 'MERCHANT_123456',
        apiKey: '********',
        callbackUrl: 'https://example.com/api/payment/callback'
      },
      loading: false,
      message: '',
      messageType: 'success'
    }
  },
  mounted() {
    this.getSettings();
  },
  methods: {
    async getSettings() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:8000/api/payment/settings');
        const result = await response.json();
        
        if (result.status === 'success' && result.data) {
          this.settings = {
            ...this.settings,
            ...result.data
          };
        }
      } catch (error) {
        console.error('获取设置失败:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async saveSettings() {
      this.loading = true;
      this.message = '';
      
      try {
        const response = await fetch('http://localhost:8000/api/payment/settings', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.settings)
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
          this.message = '设置已保存';
          this.messageType = 'success';
        } else {
          this.message = result.message || '保存失败';
          this.messageType = 'error';
        }
      } catch (error) {
        console.error('保存设置失败:', error);
        this.message = '保存设置失败: ' + (error.message || '未知错误');
        this.messageType = 'error';
      } finally {
        this.loading = false;
        
        setTimeout(() => {
          this.message = '';
        }, 3000);
      }
    }
  }
}
</script>

<style scoped>
.payment-settings {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.message.success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.message.error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.btn-primary {
  margin-top: 20px;
  padding: 8px 16px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>