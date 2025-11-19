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
              <a-tab-pane key="profile" :tab="$t('general.profile.profile')">
                <a-form-item
                  :label="$t('general.profile.username')"
                  name="username"
                  :rules="formRules.username"
                >
                  <a-input v-model:value="profile.username" :disabled="true" />
                </a-form-item>

                <a-form-item
                  :label="$t('general.profile.nickname')"
                  name="nickname"
                  :rules="[
                    {
                      required: true,
                      message: $t('general.profile.nickname_is_required'),
                    },
                  ]"
                >
                  <a-input v-model:value="profile.nickname" />
                </a-form-item>

                <a-form-item
                  :label="$t('general.profile.email')"
                  name="email"
                  :rules="formRules.email"
                >
                  <a-input v-model:value="profile.email" type="email" />
                </a-form-item>

                <a-form-item
                  :label="$t('general.profile.mobile')"
                  name="mobile"
                  :rules="formRules.mobile"
                >
                  <a-input v-model:value="profile.mobile" />
                </a-form-item>
              </a-tab-pane>

              <a-tab-pane key="password" :tab="$t('general.profile.password')">
                <a-form-item
                  :label="$t('general.profile.password')"
                  name="password"
                  :rules="[
                    {
                      required: false,
                      message: $t('general.profile.password_is_required'),
                    },
                    {
                      min: 6,
                      message: $t(
                        'general.profile.password_must_be_at_least_6_characters'
                      ),
                    },
                  ]"
                >
                  <a-input-password
                    v-model:value="profile.password"
                    :visibilityToggle="true"
                    :placeholder="
                      $t('general.profile.leave_empty_to_keep_current_password')
                    "
                    autocomplete="new-password"
                  />
                </a-form-item>
              </a-tab-pane>

              <a-tab-pane key="avatar" :tab="$t('general.profile.avatar')">
                <a-form-item :label="$t('general.profile.avatar')"
                  ><a-flex gap="middle" vertical align="center">
                    <a-avatar
                      :size="128"
                      :src="displayAvatar(profile.avatar)"
                    ></a-avatar>
                    <a-button
                      @click="triggerAvatarUpload"
                      :loading="uploading"
                      size="small"
                    >
                      {{ $t("general.profile.edit_avatar") }}
                    </a-button>

                    <input
                      ref="avatarInput"
                      type="file"
                      accept="image/*"
                      style="display: none"
                      @change="handleAvatarUpload"
                  /></a-flex>
                </a-form-item>
              </a-tab-pane>
            </a-tabs>
            <a-divider />
            <a-form-item class="text-center">
              <a-button type="primary" :loading="loading" @click="saveProfile">
                {{ $t("general.profile.save") }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>
    </a-row>

    <a-modal
      v-model:open="showCropperModal"
      :title="$t('general.profile.edit_avatar')"
      @ok="cropAndUpload"
      @cancel="cancelCrop"
      :confirmLoading="uploading"
      :width="800"
    >
      <Cropper
        ref="cropper"
        class="cropper"
        :src="cropperImage"
        :stencil-props="{
          aspectRatio: 1,
          handlers: {},
          movable: true,
          resizable: true,
        }"
        :resize-image="{
          adjustStencil: false
        }"
      />
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';
import { useAppConfig } from "@/_core/hooks";
const { webURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

import { getProfileApi, uploadApi, saveProfileApi } from "@/api/admin";
import { $t } from "@/locales";
import { message } from "ant-design-vue";

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
const defaultAvatar = "/src/assets/avatar.png";

const showCropperModal = ref(false);
const cropperImage = ref<string>("");
const cropper = ref<InstanceType<typeof Cropper> | null>(null);
const selectedFile = ref<File | null>(null);

const formRules = {
  username: [
    { required: true, message: $t("general.profile.username_is_required") },
  ],
  nickname: [
    { required: true, message: $t("general.profile.nickname_is_required") },
  ],
  email: [
    { required: true, message: $t("general.profile.email_is_required") },
    { type: "email", message: $t("general.profile.email_must_be_valid") },
  ],
  mobile: [
    { required: true, message: $t("general.profile.mobile_is_required") },
    {
      pattern: /^\+?[0-9]{11,15}$/,
      message: $t("general.profile.mobile_must_be_valid"),
    },
  ],
  password: [
    { required: false, message: $t("general.profile.password_is_required") },
    {
      min: 6,
      message: $t("general.profile.password_must_be_at_least_6_characters"),
    },
  ],
};

async function fetchProfile() {
  try {
    loading.value = true;
    const data = await getProfileApi();
    profile.value = {
      username: data.username,
      nickname: data.nickname,
      email: data.email,
      mobile: data.mobile,
      avatar: data.avatar || defaultAvatar,
      password: "",
    };
  } catch (error) {
    console.error($t("general.profile.error_fetching_profile"), error);
  } finally {
    loading.value = false;
  }
}

function triggerAvatarUpload() {
  if (avatarInput.value) {
    avatarInput.value.click();
  }
}

async function handleAvatarUpload(event: Event) {
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
  if (!cropper.value) return;

  try {
    const { canvas } = cropper.value.getResult();
    if (!canvas) return;

    canvas.toBlob(async (blob: Blob | null) => {
      if (blob) {
        try {
          uploading.value = true;
          const fileName = selectedFile.value?.name || "avatar.jpg";
          const croppedFile = new File([blob], fileName, { type: blob.type });
          const response = await uploadApi(croppedFile, "avatar");
          profile.value.avatar = displayAvatar(response.image_url);
          message.success($t("general.profile.avatar_updated_successfully"));
          saveProfile();
          showCropperModal.value = false;
        } catch (error) {
          console.error($t("general.profile.error_uploading_avatar"), error);
          message.error($t("general.profile.error_uploading_avatar"));
        } finally {
          uploading.value = false;
        }
      }
    }, "image/jpeg", 0.9); // 0.9 是图片质量
  } catch (error) {
    console.error("Error while processing cropper:", error);
    message.error($t("general.profile.error_uploading_avatar"));
  }
}

function cancelCrop() {
  showCropperModal.value = false;
  if (avatarInput.value) {
    avatarInput.value.value = "";
  }
}

function displayAvatar(avatar: string): string {
  // 如果头像为空或无效，使用默认头像
  if (!avatar || avatar.trim() === "") {
    return defaultAvatar;
  }
  
  // 如果头像已经是完整 URL 或本地 assets 路径，直接返回
  if (avatar.startsWith(webURL) || avatar.startsWith("/src/assets/")) {
    return avatar;
  }
  
  // 如果头像路径以 /uploads/ 开头，转换为 API 路径
  if (avatar.startsWith("/uploads/")) {
    return webURL + "/api/common" + avatar;
  }
  
  // 否则，添加 webURL 前缀
  return webURL + avatar;
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
      // 只有当用户输入了新密码时才更新密码
      if (profile.value.password && profile.value.password.trim() !== "") {
        payload.password = profile.value.password;
      }
    } else if (tab.value === "avatar") {
      payload.avatar = profile.value.avatar.startsWith(webURL)
        ? profile.value.avatar.replace(webURL, "")
        : profile.value.avatar;
    }

    await saveProfileApi(payload);
    message.success($t("general.profile.profile_updated_successfully"));
    
    // 保存成功后清空密码字段
    if (tab.value === "password") {
      profile.value.password = "";
    }
  } catch (error: any) {
    console.error($t("general.profile.error_saving_profile"), error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchProfile();
});
</script>

<style scoped>
.cropper {
  height: 500px;
  background: #eee;
}
</style>
