<template>
  <div class="data-table">
    <h2>数据表管理</h2>
    
    <div class="table-actions">
      <button @click="showCreateModal = true">新增数据</button>
    </div>

    <table>
      <thead>
        <tr>
          <th>名称</th>
          <th>值</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in dataList" :key="item.id">
          <td>{{ item.name }}</td>
          <td>{{ item.value }}</td>
          <td>
            <button @click="editItem(item)">编辑</button>
            <button @click="deleteItem(item.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 新增/编辑模态框 -->
    <div v-if="showCreateModal || showEditModal" class="modal">
      <div class="modal-content">
        <h3>{{ isEditing ? '编辑数据' : '新增数据' }}</h3>
        
        <form @submit.prevent="submitForm">
          <div class="form-group">
            <label>名称:</label>
            <input v-model="formData.name" required>
          </div>
          
          <div class="form-group">
            <label>值:</label>
            <input v-model="formData.value" required>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeModal">取消</button>
            <button type="submit">提交</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import dataAPI from '../main.js';

export default {
  data() {
    return {
      dataList: [],
      showCreateModal: false,
      showEditModal: false,
      isEditing: false,
      formData: {
        id: null,
        name: '',
        value: ''
      }
    };
  },
  async created() {
    await this.fetchData();
  },
  methods: {
    async fetchData() {
      this.dataList = await dataAPI.getData();
    },
    openCreateModal() {
      this.resetForm();
      this.showCreateModal = true;
    },
    editItem(item) {
      this.formData = { ...item };
      this.isEditing = true;
      this.showEditModal = true;
    },
    async deleteItem(id) {
      if (confirm('确定要删除吗？')) {
        await dataAPI.deleteData(id);
        await this.fetchData();
      }
    },
    async submitForm() {
      if (this.isEditing) {
        await dataAPI.updateData(this.formData.id, this.formData);
      } else {
        await dataAPI.createData(this.formData);
      }
      this.closeModal();
      await this.fetchData();
    },
    closeModal() {
      this.showCreateModal = false;
      this.showEditModal = false;
      this.isEditing = false;
      this.resetForm();
    },
    resetForm() {
      this.formData = {
        id: null,
        name: '',
        value: ''
      };
    }
  }
};
</script>

<style scoped>
.data-table {
  padding: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

th, td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

th {
  background-color: #f2f2f2;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-content {
  background: white;
  padding: 20px;
  border-radius: 5px;
  width: 400px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}

.form-actions {
  text-align: right;
  margin-top: 20px;
}

button {
  margin-right: 5px;
  padding: 5px 10px;
  cursor: pointer;
}
</style>