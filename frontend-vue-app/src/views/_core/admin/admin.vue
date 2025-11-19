<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['admin.add', 'all']" type="code">
                <a-button
                  type="primary"
                  success
                  @click="openDialog(currentItem, 'add')"
                >
                  <template #icon>
                    <FileAddOutlined />
                  </template>
                  {{ $t("common.add_item") }}
                </a-button>
              </AccessControl>
              <AccessControl :codes="['admin.delete', 'all']" type="code">
                <a-popconfirm
                  :title="$t('common.confirm_delete')"
                  :ok-text="$t('common.yes')"
                  :cancel-text="$t('common.no')"
                  @confirm="deleteSelectedItems"
                >
                  <a-button
                    type="primary"
                    danger
                    :disabled="state.selectedRowIds.length === 0"
                    shape="round"
                    :size="size"
                  >
                    <template #icon>
                      <DeleteOutlined />
                    </template>
                    {{ $t("common.delete_selected") }}
                  </a-button>
                </a-popconfirm>
              </AccessControl>
              <a-input-search
                v-model:value="search"
                :placeholder="$t('common.search')"
                @search="fetchItems"
                enter-button
                class="w-1/3"
              />
            </a-space>
          </a-card-header>

          <a-divider />

          <a-table
            :columns="columns"
            :dataSource="items"
            :loading="loading"
            :rowKey="rowKey"
            :pagination="pagination"
            @change="onTableChange"
            :row-selection="{
              selectedRowIds: state.selectedRowIds,
              onChange: onSelectChange,
            }"
            :scroll="{ x: true }"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'avatar'">
                <a-avatar
                  :size="32"
                  :src="displayAvatar(record.avatar)"
                  @error="handleImageError"
                />
              </template>
              <template v-if="column.key === 'actions'">
                <a-space>
                  <a-button
                    size="small"
                    type="primary"
                    @click="openDialog(record, 'view')"
                  >
                    <EyeOutlined />
                  </a-button>
                  <AccessControl :codes="['admin.edit', 'all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
                  <AccessControl :codes="['admin.delete', 'all']" type="code">
                    <a-popconfirm
                      :title="$t('common.confirm_delete')"
                      :ok-text="$t('common.yes')"
                      :cancel-text="$t('common.no')"
                      @confirm="deleteItem(record.id)"
                    >
                      <a-button size="small" type="primary" danger>
                        <template #icon>
                          <DeleteOutlined />
                        </template>
                      </a-button>
                    </a-popconfirm>
                  </AccessControl>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>

    <!-- Add/Edit/View/Delete Dialogs -->
    <a-modal
      v-model:open="isDialogVisible"
      :title="dialogTitle"
      @cancel="closeDialog"
      :confirm-loading="confirmLoading"
      @ok="onSubmit"
      :destroyOnClose="true"
      :maskClosable="false"
    >
      <a-form
        :model="currentItem"
        :label-col="labelCol"
        :wrapper-col="wrapperCol"
        ref="form"
        :rules="formRules"
      >
        <a-form-item :label="$t('admin.admin.field.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.group_id')"
          name="group_id"
          :rules="formRules.group_id"
        >
          <a-select
            v-model:value="currentItem.group_id"
            :disabled="mode === 'view'"
            placeholder="请选择管理员组"
          >
            <a-select-option :value="0">根管理员组</a-select-option>
            <a-select-option
              v-for="group in allGroups"
              :key="group.id"
              :value="group.id"
            >
              {{ group.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.username')"
          name="username"
          :rules="formRules.username"
        >
          <a-input
            v-model:value="currentItem.username"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.nickname')"
          name="nickname"
          :rules="formRules.nickname"
        >
          <a-input
            v-model:value="currentItem.nickname"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.password')"
          name="password"
          :rules="formRules.password"
        >
          <a-input-password
            v-model:value="currentItem.password"
            :disabled="mode === 'view'"
            :placeholder="mode === 'edit' ? '留空不修改密码' : '请输入密码'"
            autocomplete="new-password"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.admin.field.avatar')">
          <a-flex gap="middle" vertical align="center">
            <a-avatar
              :size="128"
              :src="displayAvatar(currentItem.avatar)"
            ></a-avatar>
            <a-button
              @click="triggerAvatarUpload"
              :loading="uploading"
              size="small"
              :disabled="mode === 'view'"
            >
              {{ $t("general.profile.edit_avatar") }}
            </a-button>

            <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              style="display: none"
              @change="handleAvatarUpload"
            />
            <a-input
              v-model:value="currentItem.avatar"
              :disabled="mode === 'view'"
              placeholder="头像URL（自动填充）"
            />
          </a-flex>
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.email')"
          name="email"
          :rules="formRules.email"
        >
          <a-input
            v-model:value="currentItem.email"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.mobile')"
          name="mobile"
          :rules="formRules.mobile"
        >
          <a-input
            v-model:value="currentItem.mobile"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.login_failure')"
          name="login_failure"
          :rules="formRules.login_failure"
        >
          <a-input
            v-model:value="currentItem.login_failure"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.admin.field.login_at')" name="login_at">
          <a-date-picker
            v-model:value="currentItem.login_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.admin.field.login_ip')">
          <a-input
            v-model:value="currentItem.login_ip"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.admin.field.token')">
          <a-input
            v-model:value="currentItem.token"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.status')"
          name="status"
          :rules="formRules.status"
        >
          <a-select
            v-model:value="currentItem.status"
            :disabled="mode === 'view'"
          >
            <a-select-option value="normal">{{
              $t("common.normal")
            }}</a-select-option>
            <a-select-option value="hidden">{{
              $t("common.hidden")
            }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.created_at')"
          name="created_at"
        >
          <a-date-picker
            v-model:value="currentItem.created_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.admin.field.updated_at')"
          name="updated_at"
        >
          <a-date-picker
            v-model:value="currentItem.updated_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Avatar Cropper Modal -->
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

<style scoped>
.cropper {
  height: 500px;
  background: #eee;
}
</style>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from "@/_core/access";
import { fetchAdminItems, saveAdmin, deleteAdmin } from "@/api/admin/admin";
import { fetchAdminGroupItems } from "@/api/admin/admin_group";
import { uploadApi } from "@/api/admin";
import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
} from "@ant-design/icons-vue";
import { message, type FormInstance } from "ant-design-vue";

import dayjs from "dayjs";
import timezone from "dayjs/plugin/timezone";
import utc from "dayjs/plugin/utc";
import { useAppConfig } from "@/_core/hooks";
const { webURL } = useAppConfig(import.meta.env, import.meta.env.PROD);
import { Cropper } from 'vue-advanced-cropper';
import 'vue-advanced-cropper/dist/style.css';

// Setup dayjs plugins
dayjs.extend(utc);
dayjs.extend(timezone);

const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || "Asia/Shanghai";
const form = ref<FormInstance | null>(null);
const defaultAvatar = "/src/assets/avatar.png";
const errorImage = "/src/assets/image-error.png";

// Avatar upload related variables
const uploading = ref(false);
const avatarInput = ref<HTMLInputElement | null>(null);
const showCropperModal = ref(false);
const cropperImage = ref<string>("");
const cropper = ref<InstanceType<typeof Cropper> | null>(null);
const selectedFile = ref<File | null>(null);

interface Admin {
  id: number;
  group_id: number;
  username: string;
  nickname: string;
  password: string;
  avatar: string | null;
  email: string;
  mobile: string;
  login_failure: number;
  login_at: string | null;
  login_ip: string | null;
  token: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

const currentItem: UnwrapRef<Admin> = reactive({
  id: 0,
  group_id: 0,
  username: "",
  nickname: "",
  password: "",
  avatar: "",
  email: "",
  mobile: "",
  login_failure: 0,
  login_at: dayjs().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
  login_ip: "",
  token: "",
  status: "normal",
  created_at: dayjs().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
  updated_at: dayjs().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
});

const isDialogVisible = ref(false);
const confirmLoading = ref(false);
const dialogTitle = computed(() => {
  switch (mode.value) {
    case "view":
      return $t("common.view_item");
    case "add":
      return $t("common.add_item");
    case "edit":
      return $t("common.edit_item");
    default:
      return "";
  }
});

const mode = ref<"add" | "edit" | "view">("add"); // Mode for Add, Edit, View

type Key = string | number;
const state = reactive<{
  selectedRowIds: Key[];
  loading: boolean;
}>({
  selectedRowIds: [],
  loading: false,
});

const size = ref("middle");
const loading = ref(false);
const rowKey = ref("id");
const items = ref([]);
interface AdminGroupItem {
  id: number;
  pid: number;
  name: string;
  rules: (number | string)[];
  access: string[];
  created_at: string;
  updated_at: string;
  status: string;
}
const allGroups = ref<AdminGroupItem[]>([]); // 所有管理员组用于下拉选择
const pagination = ref({ current: 1, pageSize: 10, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

// Validation rules
const formRules = computed(() => ({
  group_id: [
    { required: true, message: $t("admin.admin.rules.id.required") },
    {
      validator: (_: any, value: number) => {
        if (isNaN(value) || value <= 0)
          return Promise.reject(
            $t("admin.admin.rules.group_id.must_be_positive")
          );
        return Promise.resolve();
      },
    },
  ],
  username: [
    { required: true, message: $t("admin.admin.rules.username.required") },
    { min: 3, message: $t("admin.admin.rules.username.min_length") },
    { max: 20, message: $t("admin.admin.rules.username.max_length") },
    {
      pattern: /^[a-zA-Z0-9_]+$/,
      message: $t("admin.admin.rules.username.invalid_chars"),
    },
  ],
  nickname: [
    { required: true, message: $t("admin.admin.rules.nickname.required") },
    { min: 2, message: $t("admin.admin.rules.nickname.min_length") },
    { max: 30, message: $t("admin.admin.rules.nickname.max_length") },
  ],
  password: [
    {
      required: mode.value === "add",
      message: $t("admin.admin.rules.password.required"),
    },
    {
      validator: (_: any, value: string) => {
        const errors = [];
        // 在编辑模式下，密码为空时直接通过验证
        if (mode.value === "edit" && (!value || value.trim() === "")) return Promise.resolve();
        if (value && value.length < 6)
          errors.push($t("admin.admin.rules.password.min_length"));
        if (value && !/[A-Z]/.test(value))
          errors.push(
            $t("admin.admin.rules.password.uppercase_required")
          );
        if (value && !/[a-z]/.test(value))
          errors.push(
            $t("admin.admin.rules.password.lowercase_required")
          );
        if (value && !/\d/.test(value))
          errors.push($t("admin.admin.rules.password.digit_required"));
        return errors.length > 0
          ? Promise.reject(errors.join("，"))
          : Promise.resolve();
      },
    },
  ],
  email: [
    { required: true, message: $t("admin.admin.rules.email.required") },
    { type: "email", message: $t("admin.admin.rules.email.invalid_format") },
  ],
  mobile: [
    { required: true, message: $t("admin.admin.rules.mobile.required") },
    {
      pattern: /^1[3-9]\d{9}$/,
      message: $t("admin.admin.rules.mobile.invalid_format"),
    },
  ],
  login_failure: [
    { required: true, message: $t("admin.admin.rules.login_failure.required") },
    {
      validator: (_: any, value: number) => {
        if (isNaN(value))
          return Promise.reject(
            $t("admin.admin.rules.login_failure.must_be_number")
          );
        return Promise.resolve();
      },
    },
  ],
  status: [
    { required: true, message: $t("admin.admin.rules.status.required") },
  ],
  created_at: [
    { required: true, message: $t("admin.admin.rules.created_at.required") },
  ],
  updated_at: [
    { required: true, message: $t("admin.admin.rules.updated_at.required") },
  ],
}));

const columns = computed(() => [
  { title: $t("admin.admin.field.id"), dataIndex: "id", key: "id" },
  {
    title: $t("admin.admin.field.group_id"),
    dataIndex: "group_id",
    key: "group_id",
    customRender: ({ text }: { text: number }) => getGroupName(text)
  },
  {
    title: $t("admin.admin.field.username"),
    dataIndex: "username",
    key: "username",
  },
  {
    title: $t("admin.admin.field.nickname"),
    dataIndex: "nickname",
    key: "nickname",
  },
  { title: $t("admin.admin.field.avatar"), dataIndex: "avatar", key: "avatar" },
  { title: $t("admin.admin.field.email"), dataIndex: "email", key: "email" },
  { title: $t("admin.admin.field.mobile"), dataIndex: "mobile", key: "mobile" },
  {
    title: $t("admin.admin.field.login_failure"),
    dataIndex: "login_failure",
    key: "login_failure",
  },
  {
    title: $t("admin.admin.field.login_at"),
    dataIndex: "login_at",
    key: "login_at",
  },
  {
    title: $t("admin.admin.field.login_ip"),
    dataIndex: "login_ip",
    key: "login_ip",
  },
  { title: $t("admin.admin.field.status"), dataIndex: "status", key: "status" },
  {
    title: $t("admin.admin.field.created_at"),
    dataIndex: "created_at",
    key: "created_at",
  },
  {
    title: $t("admin.admin.field.updated_at"),
    dataIndex: "updated_at",
    key: "updated_at",
  },
  {
    title: $t("common.actions"),
    key: "actions",
    fixed: "right",
    align: "center",
  },
]);

const onSelectChange = (selectedRowIds: Key[]) => {
  state.selectedRowIds = selectedRowIds;
};

const onTableChange = (pag: any, filters: any, sorter: any) => {
  console.log("onTableChange", pag, filters, sorter);
  pagination.value.current = pag.current;
  pagination.value.pageSize = pag.pageSize;
  fetchItems();
};

const openDialog = async (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    Object.assign(currentItem, item);
    // 在编辑模式下，密码字段设置为空
    currentItem.password = "";

    if (currentItem.login_at) {
      item.login_at = dayjs(currentItem.login_at).tz(TIME_ZONE);
    }

    if (currentItem.created_at) {
      item.created_at = dayjs(currentItem.created_at).tz(TIME_ZONE);
    }

    if (currentItem.updated_at) {
      item.updated_at = dayjs(currentItem.updated_at).tz(TIME_ZONE);
    }
  }
  isDialogVisible.value = true;
  await fetchAllGroups(); // 确保获取所有管理员组数据
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    group_id: 0,
    username: "",
    nickname: "",
    password: "",
    avatar: "",
    email: "",
    mobile: "",
    login_failure: 0,
    login_at: dayjs().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
    login_ip: "",
    token: "",
    status: "normal",
    created_at: dayjs().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
    updated_at: dayjs().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
  });
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const onSubmit = async () => {
  try {
    // Validate the form before submission
    await form.value?.validate();
    confirmLoading.value = true;
    if (mode.value === "add") {
      await saveItem();
    } else if (mode.value === "edit") {
      await updateItem();
    }
  } catch (error) {
    console.log($t("common.error"), error);
  } finally {
    confirmLoading.value = false;
  }
};

const saveItem = async () => {
  try {
    await saveAdmin({
      group_id: currentItem.group_id,
      username: currentItem.username,
      nickname: currentItem.nickname,
      password: currentItem.password,
      avatar: currentItem.avatar,
      email: currentItem.email,
      mobile: currentItem.mobile,
      login_failure: currentItem.login_failure,
      login_at: currentItem.login_at
        ? dayjs(currentItem.login_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
      login_ip: currentItem.login_ip,
      token: currentItem.token,
      status: currentItem.status,
      created_at: currentItem.created_at
        ? dayjs(currentItem.created_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
      updated_at: currentItem.updated_at
        ? dayjs(currentItem.updated_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
    });
    resetCurrentItem();
    fetchItems();
    closeDialog();
    message.success($t("common.save_success"));
  } catch (error) {
    console.error($t("common.save_item_failed"), error);
  }
};

const updateItem = async () => {
  try {
    // 构建更新数据，如果密码为空则不包含密码字段
    const updateData: any = {
      id: currentItem.id,
      group_id: currentItem.group_id,
      username: currentItem.username,
      nickname: currentItem.nickname,
      avatar: currentItem.avatar,
      email: currentItem.email,
      mobile: currentItem.mobile,
      login_failure: currentItem.login_failure,
      login_at: currentItem.login_at
        ? dayjs(currentItem.login_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
      login_ip: currentItem.login_ip,
      token: currentItem.token,
      status: currentItem.status,
      created_at: currentItem.created_at
        ? dayjs(currentItem.created_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
      updated_at: currentItem.updated_at
        ? dayjs(currentItem.updated_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
    };
    
    // 只有在密码不为空时才包含密码字段
    if (currentItem.password && currentItem.password.trim() !== "") {
      updateData.password = currentItem.password;
    }
    
    await saveAdmin(updateData);
    fetchItems();
    closeDialog();
    message.success($t("common.update_success"));
  } catch (error) {
    console.error($t("common.update_item_failed"), error);
  }
};

const deleteItem = async (id: number) => {
  try {
    await deleteAdmin(id);
    message.success($t("common.delete_success"));
    fetchItems();
  } catch (error) {
    console.error($t("common.delete_item_failed"), error);
  }
};

const deleteSelectedItems = async () => {
  try {
    state.loading = true;
    const ids = Array.from(state.selectedRowIds);
    for (const id of ids) {
      const numericId = typeof id === "string" ? parseInt(id) : id;
      await deleteAdmin(numericId);
    }
    fetchItems();
    state.selectedRowIds = [];
    message.success($t("common.delete_selected_success"));
  } catch (error) {
    console.error($t("common.delete_selected_failed"), error);
  } finally {
    state.loading = false;
  }
};

function displayAvatar(avatar: string | null): string {
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
          
          // 直接存储服务器返回的相对地址，不转换为完整URL
          currentItem.avatar = response.image_url;
          
          message.success($t("general.profile.avatar_updated_successfully"));
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

function handleImageError(event: Event) {
  const img = event.target as HTMLImageElement;
  img.src = errorImage;
}

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchAdminItems({
      page: pagination.value.current,
      perPage: pagination.value.pageSize,
      search: search.value,
    });
    items.value = response.items;
    pagination.value.total = response.total;
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  } finally {
    loading.value = false;
  }
};

// 获取所有管理员组用于下拉选择
const fetchAllGroups = async () => {
  try {
    const response = await fetchAdminGroupItems({
      page: 1,
      perPage: -1,
      search: "",
    });
    allGroups.value = response.items.map((item: any) => ({
      ...item,
      rules: item.rules || [],
      access: item.access || [],
    }));
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  }
};

// 根据管理员组ID获取组名称
const getGroupName = (groupId: number): string => {
  if (groupId === 0) {
    return "根管理员组";
  }
  const group = allGroups.value.find(group => group.id === groupId);
  return group ? group.name : `未知组(${groupId})`;
};

onMounted(() => {
  fetchItems();
});
</script>
