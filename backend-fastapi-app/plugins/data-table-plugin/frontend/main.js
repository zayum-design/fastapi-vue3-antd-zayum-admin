import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export default {
  async createData(item) {
    const response = await axios.post(`${API_BASE}/data`, item);
    return response.data;
  },

  async getData() {
    const response = await axios.get(`${API_BASE}/data`);
    return response.data;
  },

  async updateData(id, item) {
    const response = await axios.put(`${API_BASE}/data/${id}`, item);
    return response.data;
  },

  async deleteData(id) {
    const response = await axios.delete(`${API_BASE}/data/${id}`);
    return response.data;
  }
};