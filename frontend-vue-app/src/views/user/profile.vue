<template>
  <div>
    <a-row justify="center">
      <a-col :span="24" :bg="12">
        <a-card :loading="loading" bordered="false">
          <a-form
            ref="form"
            layout="vertical"
            :model="profile"
            :rules="formRules"
          >
            <a-tabs v-model:activeKey="tab" tabPosition="left" animated>
              <a-tab-pane key="profile" tab="基本信息">
                <a-form-item label="用户名" name="username">
                  <a-input v-model:value="profile.username" :disabled="true" />
                </a-form-item>

                <a-form-item label="昵称" name="nickname">
                  <a-input v-model:value="profile.nickname" />
                </a-form-item>

                <a-form-item label="邮箱" name="email">
                  <a-input v-model:value="profile.email" type="email" />
                </a-form-item>

                <a-form-item label="手机号" name="mobile">
                  <a-input v-model:value="profile.mobile" />
                </a-form-item>
              </a-tab-pane>

              <a-tab-pane key="password" tab="修改密码">
                <a-form-item label="新密码" name="password">
                  <a-input-password
                    v-model:value="profile.password"
                    :visibilityToggle="true"
                    placeholder="留空则不修改密码"
                  />
                </a-form-item>
              </a-tab-pane>

              <a-tab-pane key="avatar" tab="头像设置">
                <a-form-item label="头像">
                  <a-flex gap="middle" vertical align="center">
                    <a-avatar
                      :size="128"
                      :src="profile.avatar || '/uploads/avatar/avatar.png'"
                    ></a-avatar>
                    <a-button
                      @click="triggerAvatarUpload"
                      :loading="uploading"
                      size="small"
                    >
                      修改头像
                    </a-button>

                    <input
                      ref="avatarInput"
                      type="file"
                      accept="image/*"
                      style="display: none"
                      @change="handleAvatarUpload"
                    />
                  </a-flex>
                </a-form-item>
              </a-tab-pane>
            </a-tabs>
            <a-divider />
            <a-form-item class="text-center">
              <a-button type="primary" :loading="loading" @click="saveProfile">
                保存
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>

    <a-modal
      v-model:open="showCropperModal"
      title="编辑头像"
      @ok="cropAndUpload"
      @cancel="cancelCrop"
      :confirmLoading="uploading"
      :width="800"
    >
      <div class="cropper-container">
        <img ref="cropperImage" :src="cropperImage" style="max-width: 100%" />
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { message } from "ant-design-vue";
import { getProfileApi } from "@/api/user/auth";
import { saveProfileApi, uploadApi } from "@/api/user/profile";

interface Profile {
  username: string;
  nickname: string;
  email: string;
  mobile: string;
  avatar: string;
  password: string;
}

const profile = ref<Profile>({
  username: "",
  nickname: "",
  email: "",
  mobile: "",
  avatar: "",
  password: "",
});

const loading = ref(false);
const uploading = ref(false);
const tab = ref("profile");
const form = ref();
const avatarInput = ref<HTMLInputElement | null>(null);

const showCropperModal = ref(false);
const cropperImage = ref<string>("");
const selectedFile = ref<File | null>(null);

const formRules = {
  username: [{ required: true, message: "用户名不能为空" }],
  nickname: [{ required: true, message: "昵称不能为空" }],
  email: [
    { required: true, message: "邮箱不能为空" },
    { type: "email", message: "请输入有效的邮箱地址" },
  ],
  mobile: [
    { required: true, message: "手机号不能为空" },
    { pattern: /^1[3-9]\d{9}$/, message: "请输入有效的手机号" },
  ],
  password: [
    { required: false },
    { min: 6, message: "密码长度不能少于6位" },
  ],
};

async function fetchProfile() {
  try {
    loading.value = true;
    const response = await getProfileApi();
    profile.value = {
      username: response.username,
      nickname: response.nickname,
      email: response.email,
      mobile: response.mobile,
      avatar: response.avatar,
      password: "",
    };
  } catch (error) {
    message.error("获取用户信息失败");
  } finally {
    loading.value = false;
  }
}

function triggerAvatarUpload() {
  if (avatarInput.value) {
    avatarInput.value.click();
  }
}

function handleAvatarUpload(event: Event) {
  const fileInput = event.target as HTMLInputElement;
  const file = fileInput.files?.[0];
  if (file) {
    selectedFile.value = file;
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") {
        cropperImage.value = reader.result;
        showCropperModal.value = true;
      }
    };
    reader.readAsDataURL(file);
  }
}

async function cropAndUpload() {
  try {
    uploading.value = true;
    if (!selectedFile.value) return;

    const formData = new FormData();
    formData.append("file", selectedFile.value);
    formData.append("type", "avatar");

    const { data } = await uploadApi(selectedFile.value, "avatar");
    profile.value.avatar = data.url;
    message.success("头像更新成功");
    showCropperModal.value = false;
  } catch (error) {
    message.error("头像上传失败");
  } finally {
    uploading.value = false;
  }
}

function cancelCrop() {
  showCropperModal.value = false;
  if (avatarInput.value) {
    avatarInput.value.value = "";
  }
}

async function saveProfile() {
  try {
    await form.value.validateFields();
    loading.value = true;

    const payload: any = {};

    if (tab.value === "profile") {
      payload.nickname = profile.value.nickname;
      payload.email = profile.value.email;
      payload.mobile = profile.value.mobile;
    } else if (tab.value === "password") {
      payload.password = profile.value.password || undefined;
    } else if (tab.value === "avatar") {
      payload.avatar = profile.value.avatar;
    }

    await saveProfileApi(payload);
    message.success("资料更新成功");
  } catch (error) {
    message.error("资料更新失败");
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchProfile();
});
</script>

<style scoped>
.cropper-container {
  height: 500px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #eee;
}
</style>
