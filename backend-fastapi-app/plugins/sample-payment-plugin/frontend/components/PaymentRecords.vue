<template>
  <div class="payment-detail">
    <h2>支付记录 (远程组件)7777</h2>
    <div class="payment-info">
      <p><strong>订单号:</strong> {{ paymentData?.payment_id || 'ORD-2025031301' }}</p>
      <p><strong>金额:</strong> ¥{{ paymentData?.amount || '299.00' }}</p>
      <p>
        <strong>状态:</strong>
        <span :class="`status-${paymentData?.status || 'success'}`">
          {{ paymentData?.status === 'failed' ? '支付失败' : '支付成功' }}
        </span>
      </p>
      <p><strong>支付时间:</strong> {{ formatDate(paymentData?.created_at) || '2025-03-13 17:30:45' }}</p>
      <p><strong>支付方式:</strong> {{ paymentData?.payment_method || '微信支付' }}</p>
    </div>
    <button 
      class="btn-primary"
      :disabled="loading"
      @click="getPaymentDetails"
    >
      {{ loading ? '加载中...' : '刷新数据' }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'PaymentRecords',
  data() {
    return {
      paymentData: null,
      loading: false
    }
  },
  mounted() {
    this.getPaymentDetails();
  },
  methods: {
    async getPaymentDetails() {
      this.loading = true;
      try {
        const response = await fetch('http://localhost:8000/api/payment/create');
        const result = await response.json();
        
        if (result.status === 'success' && result.data) {
          this.paymentData = result.data;
        }
      } catch (error) {
        console.error('获取支付数据失败:', error);
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        });
      } catch (e) {
        return dateString;
      }
    }
  }
}
</script>

<style scoped>
.payment-detail {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.payment-info p {
  margin: 10px 0;
}

.status-success {
  color: #67c23a;
}

.status-failed {
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