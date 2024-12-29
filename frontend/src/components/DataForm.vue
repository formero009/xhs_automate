<template>
  <div class="data-form">
    <input v-model="inputData" placeholder="输入一些内容..." />
    <button @click="sendData">提交</button>
    <p v-if="responseMessage">{{ responseMessage }}</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      inputData: '',
      responseMessage: '',
    };
  },
  methods: {
    async sendData() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/api/process', {
          data: this.inputData,
        });
        this.responseMessage = response.data.message;
      } catch (error) {
        console.error("Error:", error);
        this.responseMessage = "请求失败，请检查后端服务！";
      }
    },
  },
};
</script>

<style scoped>
.data-form {
  margin: 20px 0;
}

input {
  padding: 8px;
  margin-right: 10px;
}

button {
  padding: 8px 15px;
  cursor: pointer;
}
</style> 