<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['user.add','all']" type="code">
              <a-button
                type="primary"
                @click="openDialog(currentItem, 'add')"
              >
                <FileAddOutlined />
                {{ $t("common.add_item") }}
              </a-button>
            </AccessControl>
              <AccessControl :codes="['user.delete','all']" type="code">
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
              <template v-if="column.key === 'actions'">
                <a-space>
                  <a-button
                    size="small"
                    type="primary"
                    @click="openDialog(record, 'view')"
                  >
                    <EyeOutlined />
                  </a-button>
                  <AccessControl :codes="['user.edit','all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
<AccessControl
                    :codes="['user.delete','all']"
                    type="code"
                  >
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
        
        <a-form-item :label="$t('user.field.id')" v-if="mode !== 'add'">
        <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.user_group')" name="user_group_id" :rules="formRules.user_group_id">
        <a-select
            v-model:value="currentItem.user_group_id"
            :disabled="mode === 'view'"
            :options="userGroupOptions"
            :placeholder="$t('user.field.user_group')"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.username')" name="username" :rules="formRules.username">
        <a-input v-model:value="currentItem.username" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.nickname')" name="nickname" :rules="formRules.nickname">
        <a-input v-model:value="currentItem.nickname" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.password')" name="password" :rules="formRules.password" v-if="mode === 'add'">
        <a-input-password
            v-model:value="currentItem.password"
            placeholder="请输入密码"
            autocomplete="off"
        />
        </a-form-item>
        <a-form-item :label="$t('user.field.password')" name="password" :rules="formRules.password" v-else>
        <a-input-password
            v-model:value="currentItem.password"
            :disabled="mode === 'view'"
            placeholder="留空表示不修改密码"
            autocomplete="off"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.email')" name="email" :rules="formRules.email">
        <a-input v-model:value="currentItem.email" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.mobile')" name="mobile" :rules="formRules.mobile">
        <a-input v-model:value="currentItem.mobile" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.avatar')" >
        <a-input v-model:value="currentItem.avatar" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.level')" name="level" :rules="formRules.level">
        <a-input v-model:value="currentItem.level" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.gender')" name="gender" :rules="formRules.gender">
        <a-select
            v-model:value="currentItem.gender"
            :disabled="mode === 'view'"
        >
            <a-select-option value="male">{{ $t("common.male") }}</a-select-option>
<a-select-option value="female">{{ $t("common.female") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('user.field.birthday')" name="birthday">
        <a-date-picker
            v-model:value="currentItem.birthday"
            :disabled="mode === 'view'"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.bio')" >
        <a-input v-model:value="currentItem.bio" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.balance')" >
        <a-input v-model:value="currentItem.balance" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.score')" name="score" :rules="formRules.score">
        <a-input v-model:value="currentItem.score" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.successions')" >
        <a-input v-model:value="currentItem.successions" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.max_successions')" >
        <a-input v-model:value="currentItem.max_successions" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.prev_time')" name="prev_time">
        <a-date-picker
            v-model:value="currentItem.prev_time"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.login_time')" name="login_time">
        <a-date-picker
            v-model:value="currentItem.login_time"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.login_ip')" >
        <a-input v-model:value="currentItem.login_ip" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.login_failure')" >
        <a-input v-model:value="currentItem.login_failure" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.join_ip')" >
        <a-input v-model:value="currentItem.join_ip" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.verification')" >
        <a-input v-model:value="currentItem.verification" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.token')" >
        <a-input v-model:value="currentItem.token" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.status')" >
        <a-select
            v-model:value="currentItem.status"
            :disabled="mode === 'view'"
        >
            <a-select-option value="normal">{{ $t("common.normal") }}</a-select-option>
<a-select-option value="hidden">{{ $t("common.hidden") }}</a-select-option>
<a-select-option value="delete">{{ $t("common.delete") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('user.field.platform')" name="platform">
        <a-select
            v-model:value="currentItem.platform"
            :disabled="mode === 'view'"
        >
            <a-select-option value="ios">{{ $t("common.platform.ios") }}</a-select-option>
            <a-select-option value="mac">{{ $t("common.platform.mac") }}</a-select-option>
            <a-select-option value="android">{{ $t("common.platform.android") }}</a-select-option>
            <a-select-option value="web">{{ $t("common.platform.web") }}</a-select-option>
            <a-select-option value="pc">{{ $t("common.platform.pc") }}</a-select-option>
            <a-select-option value="other">{{ $t("common.platform.other") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('user.field.created_at')" name="created_at">
        <a-date-picker
            v-model:value="currentItem.created_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.field.updated_at')" name="updated_at">
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
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from '@/_core/access';
import {
  fetchUserItems,
  saveUser,
  deleteUser,
} from "@/api/admin/user";
import { fetchUserGroupItems } from "@/api/admin/user_group";
import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
} from "@ant-design/icons-vue";
import { message, type FormInstance } from "ant-design-vue";

import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';

// Setup dayjs plugins
dayjs.extend(utc);
dayjs.extend(timezone);

const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || "Asia/Shanghai";
const form = ref<FormInstance | null>(null);
const userGroupOptions = ref<{ value: number; label: string }[]>([]);
const userGroups = ref<any[]>([]);

interface User {
  id: number;
  user_group_id: number;
  username: string;
  nickname: string;
  password: string;
  email: string;
  mobile: string;
  avatar: string | null;
  level: number;
  gender: string;
  birthday: string | null;
  bio: string | null;
  balance: any | null;
  score: number;
  successions: number | null;
  max_successions: number | null;
  prev_time: string | null;
  login_time: string | null;
  login_ip: string | null;
  login_failure: number | null;
  join_ip: string | null;
  verification: string | null;
  token: string | null;
  status: string | null;
  platform: string;
  created_at: string;
  updated_at: string;
  
}

const currentItem: UnwrapRef<User> = reactive({
  id: 0,
      user_group_id: 0,
      username: '',
      nickname: '',
      password: '',
      email: '',
      mobile: '',
      avatar: '',
      level: 0,
      gender: 'male',
      birthday: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD'),
      bio: '',
      balance: 0.0,
      score: 0,
      successions: 0,
      max_successions: 0,
      prev_time: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      login_time: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      login_ip: '',
      login_failure: 0,
      join_ip: '',
      verification: '',
      token: '',
      status: 'normal',
      platform: 'web',
      created_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      updated_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      
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
const pagination = ref({ current: 1, pageSize: 10, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

// Validation rules
const formRules = computed(() => ({
    user_group_id: [
    { required: true, message: $t('user.rules.id.required') },
    { validator: (_: any, value: number) => {  if (isNaN(value) || value <= 0) return Promise.reject($t('user.rules.group_id.must_be_positive'));  return Promise.resolve();}}
  ],
  username: [
    { required: true, message: $t('user.rules.username.required') },
    { min: 3, message: $t('user.rules.username.min_length') },
    { max: 20, message: $t('user.rules.username.max_length') },
    { pattern: /^[a-zA-Z0-9_]+$/, message: $t('user.rules.username.invalid_chars') }
  ],
  nickname: [
    { required: true, message: $t('user.rules.nickname.required') },
    { min: 2, message: $t('user.rules.nickname.min_length') },
    { max: 30, message: $t('user.rules.nickname.max_length') }
  ],
  password: [
    { required: mode.value === 'add', message: $t('user.rules.password.required') },
    { validator: (_: any, value: string) => {  
      const errors = [];  
      if (mode.value === 'edit' && !value) return Promise.resolve();  
      if (mode.value === 'add' && !value) errors.push($t('user.rules.password.required'));
      if (value && value.length < 6) errors.push($t('user.rules.password.password_min_length'));  
      if (value && !/[A-Z]/.test(value)) errors.push($t('user.rules.password.password_uppercase_required'));  
      if (value && !/[a-z]/.test(value)) errors.push($t('user.rules.password.password_lowercase_required'));  
      if (value && !/\d/.test(value)) errors.push($t('user.rules.password.password_digit_required'));  
      return errors.length > 0 ? Promise.reject(errors.join('，')) : Promise.resolve();
    }}
  ],
  email: [
    { required: true, message: $t('user.rules.email.required') },
    { type: 'email', message: $t('user.rules.email.invalid_format') }
  ],
  mobile: [
    { required: true, message: $t('user.rules.mobile.required') },
    { pattern: /^1[3-9]\d{9}$/, message: $t('user.rules.mobile.invalid_format') }
  ],
  level: [
    { required: true, message: $t('user.rules.level.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('user.rules.level.must_be_number'));
    return Promise.resolve();
    }}
  ],
  gender: [
    { required: true, message: $t('user.rules.gender.required') }
  ],
  score: [
    { required: true, message: $t('user.rules.score.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('user.rules.score.must_be_number'));
    return Promise.resolve();
    }}
  ],
  created_at: [
    { required: true, message: $t('user.rules.created_at.required') }
  ],
  updated_at: [
    { required: true, message: $t('user.rules.updated_at.required') }
  ],

}));

const columns = computed(() => [
  { title: $t('user.field.id'), dataIndex: 'id', key: 'id' },
  { 
    title: $t('user.field.user_group'), 
    dataIndex: 'user_group_id', 
    key: 'user_group_id',
    customRender: ({ text }: { text: number }) => getUserGroupName(text)
  },
  { title: $t('user.field.username'), dataIndex: 'username', key: 'username' },
  { title: $t('user.field.nickname'), dataIndex: 'nickname', key: 'nickname' },
  { title: $t('user.field.email'), dataIndex: 'email', key: 'email' },
  { title: $t('user.field.mobile'), dataIndex: 'mobile', key: 'mobile' },
  { title: $t('user.field.avatar'), dataIndex: 'avatar', key: 'avatar' },
  { title: $t('user.field.level'), dataIndex: 'level', key: 'level' },
  { title: $t('user.field.gender'), dataIndex: 'gender', key: 'gender' },
  { title: $t('user.field.birthday'), dataIndex: 'birthday', key: 'birthday' },
  { title: $t('user.field.balance'), dataIndex: 'balance', key: 'balance' },
  { title: $t('user.field.score'), dataIndex: 'score', key: 'score' },
  { title: $t('user.field.successions'), dataIndex: 'successions', key: 'successions' },
  { title: $t('user.field.max_successions'), dataIndex: 'max_successions', key: 'max_successions' },
  { title: $t('user.field.prev_time'), dataIndex: 'prev_time', key: 'prev_time' },
  { title: $t('user.field.login_time'), dataIndex: 'login_time', key: 'login_time' },
  { title: $t('user.field.login_ip'), dataIndex: 'login_ip', key: 'login_ip' },
  { title: $t('user.field.login_failure'), dataIndex: 'login_failure', key: 'login_failure' },
  { title: $t('user.field.join_ip'), dataIndex: 'join_ip', key: 'join_ip' },
  { title: $t('user.field.status'), dataIndex: 'status', key: 'status' },
  { title: $t('user.field.platform'), dataIndex: 'platform', key: 'platform' },
  { title: $t('user.field.created_at'), dataIndex: 'created_at', key: 'created_at' },
  { title: $t('user.field.updated_at'), dataIndex: 'updated_at', key: 'updated_at' },
  { title: $t('common.actions'), key: 'actions', fixed: 'right', align: "center" },
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

const fetchUserGroups = async () => {
  try {
    const response = await fetchUserGroupItems({
      page: 1,
      perPage: -1, // Get all items
      search: "",
    });
    userGroups.value = response.items;
    
    // Build hierarchical options
    userGroupOptions.value = buildUserGroupOptions(response.items);
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  }
};

// Helper function to build hierarchical user group options
const buildUserGroupOptions = (groups: any[], level = 0): { value: number; label: string }[] => {
  const options: { value: number; label: string }[] = [];
  
  groups.forEach(group => {
    const prefix = '　'.repeat(level); // Using full-width spaces for indentation
    options.push({
      value: group.id,
      label: `${prefix}${group.name}`
    });
    
    // Recursively add children if any
    if (group.children && group.children.length > 0) {
      options.push(...buildUserGroupOptions(group.children, level + 1));
    }
  });
  
  return options;
};

// Helper function to get user group name by ID
const getUserGroupName = (groupId: number): string => {
  const group = userGroups.value.find(g => g.id === groupId);
  return group ? group.name : `${$t('user.group.field.user_group')}(${groupId})`;
};

const openDialog = (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    Object.assign(currentItem, item);
    
    if (currentItem.prev_time) {
        item.prev_time = dayjs(currentItem.prev_time).tz(TIME_ZONE);
    }
            
    if (currentItem.login_time) {
        item.login_time = dayjs(currentItem.login_time).tz(TIME_ZONE);
    }
            
    if (currentItem.created_at) {
        item.created_at = dayjs(currentItem.created_at).tz(TIME_ZONE);
    }
            
    if (currentItem.updated_at) {
        item.updated_at = dayjs(currentItem.updated_at).tz(TIME_ZONE);
    }
            
  }
  fetchUserGroups(); // Load user groups when opening dialog
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
      user_group_id: 0,
      username: '',
      nickname: '',
      password: '',
      email: '',
      mobile: '',
      avatar: '',
      level: 0,
      gender: 'male',
      birthday: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD'),
      bio: '',
      balance: 0.0,
      score: 0,
      successions: 0,
      max_successions: 0,
      prev_time: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      login_time: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      login_ip: '',
      login_failure: 0,
      join_ip: '',
      verification: '',
      token: '',
      status: 'normal',
      platform: 'web',
      created_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      updated_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      
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
    await saveUser({
      user_group_id: currentItem.user_group_id,
      username: currentItem.username,
      nickname: currentItem.nickname,
      password: currentItem.password,
      email: currentItem.email,
      mobile: currentItem.mobile,
      avatar: currentItem.avatar,
      level: currentItem.level,
      gender: currentItem.gender,
      birthday: currentItem.birthday ? dayjs(currentItem.birthday).format('YYYY-MM-DD') : null,
      bio: currentItem.bio,
      balance: currentItem.balance,
      score: currentItem.score,
      successions: currentItem.successions,
      max_successions: currentItem.max_successions,
      prev_time: currentItem.prev_time ? dayjs(currentItem.prev_time).format('YYYY-MM-DD HH:mm:ss') : null,
      login_time: currentItem.login_time ? dayjs(currentItem.login_time).format('YYYY-MM-DD HH:mm:ss') : null,
      login_ip: currentItem.login_ip,
      login_failure: currentItem.login_failure,
      join_ip: currentItem.join_ip,
      verification: currentItem.verification,
      token: currentItem.token,
      status: currentItem.status,
      platform: currentItem.platform,
      created_at: currentItem.created_at ? dayjs(currentItem.created_at).format('YYYY-MM-DD HH:mm:ss') : null,
      updated_at: currentItem.updated_at ? dayjs(currentItem.updated_at).format('YYYY-MM-DD HH:mm:ss') : null,
      
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
    await saveUser({
      id: currentItem.id,
      user_group_id: currentItem.user_group_id,
      username: currentItem.username,
      nickname: currentItem.nickname,
      password: currentItem.password,
      email: currentItem.email,
      mobile: currentItem.mobile,
      avatar: currentItem.avatar,
      level: currentItem.level,
      gender: currentItem.gender,
      birthday: currentItem.birthday ? dayjs(currentItem.birthday).format('YYYY-MM-DD') : null,
      bio: currentItem.bio,
      balance: currentItem.balance,
      score: currentItem.score,
      successions: currentItem.successions,
      max_successions: currentItem.max_successions,
      prev_time: currentItem.prev_time ? dayjs(currentItem.prev_time).format('YYYY-MM-DD HH:mm:ss') : null,
      login_time: currentItem.login_time ? dayjs(currentItem.login_time).format('YYYY-MM-DD HH:mm:ss') : null,
      login_ip: currentItem.login_ip,
      login_failure: currentItem.login_failure,
      join_ip: currentItem.join_ip,
      verification: currentItem.verification,
      token: currentItem.token,
      status: currentItem.status,
      platform: currentItem.platform,
      created_at: currentItem.created_at ? dayjs(currentItem.created_at).format('YYYY-MM-DD HH:mm:ss') : null,
      updated_at: currentItem.updated_at ? dayjs(currentItem.updated_at).format('YYYY-MM-DD HH:mm:ss') : null,
      
    });
    fetchItems();
    closeDialog();
    message.success($t("common.update_success"));
  } catch (error) {
    console.error($t("common.update_item_failed"), error);
  }
};

const deleteItem = async (id: number) => {
  try {
    await deleteUser(id);
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
      await deleteUser(numericId);
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

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchUserItems({
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

onMounted(() => {
  fetchItems();
  fetchUserGroups(); // Load user groups on page initialization
});
</script>
