<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['user_group.add', 'all']" type="code">
                <a-button
                  type="primary"
                  @click="openDialog(currentItem, 'add')"
                >
                  <FileAddOutlined />
                  {{ $t("common.add_item") }}
                </a-button>
              </AccessControl>
              <AccessControl :codes="['user_group.delete', 'all']" type="code">
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
                  <AccessControl
                    :codes="['user_group.edit', 'all']"
                    type="code"
                  >
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
                  <AccessControl
                    :codes="['user_group.delete', 'all']"
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
        <a-form-item :label="$t('user.group.field.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item
          :label="$t('user.group.field.pid')"
          name="pid"
          :rules="formRules.pid"
        >
          <a-select
            v-model:value="currentItem.pid"
            :disabled="mode === 'view'"
            :options="userGroupOptions"
            :placeholder="$t('user.group.field.pid')"
          />
        </a-form-item>

        <a-form-item
          :label="$t('user.group.field.name')"
          name="name"
          :rules="formRules.name"
        >
          <a-input
            v-model:value="currentItem.name"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('user.group.field.rules')"
          name="rules"
          :rules="formRules.rules"
        >
          <a-select
            v-model:value="currentItem.rules"
            mode="multiple"
            :disabled="mode === 'view'"
            :placeholder="$t('user.group.placeholder.rules')"
          >
            <a-select-option value="all">全部权限</a-select-option>
            <a-select-option value="read">读取权限</a-select-option>
            <a-select-option value="write">写入权限</a-select-option>
            <a-select-option value="delete">删除权限</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('user.group.field.access')"
          name="access"
          :rules="formRules.access"
        >
          <a-select
            v-model:value="currentItem.access"
            mode="multiple"
            :disabled="mode === 'view'"
            :placeholder="$t('user.group.placeholder.access')"
          >
            <a-select-option value="all">全部访问</a-select-option>
            <a-select-option value="public">公开访问</a-select-option>
            <a-select-option value="private">私有访问</a-select-option>
            <a-select-option value="protected">受保护访问</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('user.group.field.status')"
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
          :label="$t('user.group.field.created_at')"
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
          :label="$t('user.group.field.updated_at')"
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
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from "@/_core/access";
import {
  fetchUserGroupItems,
  saveUserGroup,
  deleteUserGroup,
} from "@/api/admin/user_group";
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

// Setup dayjs plugins
dayjs.extend(utc);
dayjs.extend(timezone);

const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || "Asia/Shanghai";
const form = ref<FormInstance | null>(null);
const userGroupOptions = ref<{ value: number; label: string }[]>([]);

// Helper function to convert array to object for backend
const convertArrayToObject = (value: any) => {
  if (Array.isArray(value)) {
    return { permissions: value };
  }
  return value;
};

interface UserGroup {
  id: number;
  pid: number;
  name: string;
  rules: string[];
  access: string[];
  status: string;
  created_at: string;
  updated_at: string;
}

const currentItem: UnwrapRef<UserGroup> = reactive({
  id: 0,
  pid: 0,
  name: "",
  rules: ["all"],
  access: ["all"],
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
const pagination = ref({ current: 1, pageSize: 10, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

// Validation rules
const formRules = reactive({
  pid: [
    { required: true, message: $t("user.group.rules.pid.required") },
  ],
  name: [
    { required: true, message: $t("user.group.rules.nickname.required") },
    { min: 2, message: $t("user.group.rules.nickname.min_length") },
    { max: 30, message: $t("user.group.rules.nickname.max_length") },
  ],
  rules: [{ required: true, message: $t("user.group.rules.rules.required") }],
  access: [{ required: true, message: $t("user.group.rules.access.required") }],
  status: [{ required: true, message: $t("user.group.rules.status.required") }],
  created_at: [
    { required: true, message: $t("user.group.rules.created_at.required") },
  ],
  updated_at: [
    { required: true, message: $t("user.group.rules.updated_at.required") },
  ],
});

const columns = computed(() => [
  { title: $t("user.group.field.id"), dataIndex: "id", key: "id" },
  { title: $t("user.group.field.pid"), dataIndex: "parent_name", key: "parent_name" },
  { title: $t("user.group.field.name"), dataIndex: "name", key: "name" },
  { 
    title: $t("user.group.field.rules"), 
    dataIndex: "rules", 
    key: "rules",
    customRender: ({ text }: { text: any }) => {
      if (typeof text === 'object' && text !== null && text.permissions) {
        return text.permissions.join(", ");
      }
      return Array.isArray(text) ? text.join(", ") : String(text || "");
    }
  },
  { 
    title: $t("user.group.field.access"), 
    dataIndex: "access", 
    key: "access",
    customRender: ({ text }: { text: any }) => {
      if (typeof text === 'object' && text !== null && text.permissions) {
        return text.permissions.join(", ");
      }
      return Array.isArray(text) ? text.join(", ") : String(text || "");
    }
  },
  { title: $t("user.group.field.status"), dataIndex: "status", key: "status" },
  {
    title: $t("user.group.field.created_at"),
    dataIndex: "created_at",
    key: "created_at",
  },
  {
    title: $t("user.group.field.updated_at"),
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

const fetchUserGroupOptions = async () => {
  try {
    const response = await fetchUserGroupItems({
      page: 1,
      perPage: -1, // Get all items
      search: "",
    });
    
    // Filter out current item when editing to avoid self-reference
    const filteredItems = mode.value === 'edit' 
      ? response.items.filter((item: any) => item.id !== currentItem.id)
      : response.items;
    
    userGroupOptions.value = [
      { value: 0, label: $t("user.group.root_group") },
      ...filteredItems.map((item: any) => ({
        value: item.id,
        label: item.name,
      })),
    ];
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  }
};

const openDialog = (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    // Handle rules and access data from backend
    const formattedItem = {
      ...item,
      rules: Array.isArray(item.rules) ? item.rules : 
             (typeof item.rules === 'object' && item.rules !== null && item.rules.permissions) ? 
             item.rules.permissions : ["all"],
      access: Array.isArray(item.access) ? item.access : 
              (typeof item.access === 'object' && item.access !== null && item.access.permissions) ? 
              item.access.permissions : ["all"]
    };
    
    Object.assign(currentItem, formattedItem);

    if (currentItem.created_at) {
      item.created_at = dayjs(currentItem.created_at).tz(TIME_ZONE);
    }

    if (currentItem.updated_at) {
      item.updated_at = dayjs(currentItem.updated_at).tz(TIME_ZONE);
    }
  }
  fetchUserGroupOptions();
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    pid: "0",
    name: "",
    rules: ["all"],
    access: ["all"],
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
    await saveUserGroup({
      pid: currentItem.pid,
      name: currentItem.name,
      rules: convertArrayToObject(currentItem.rules),
      access: convertArrayToObject(currentItem.access),
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
    await saveUserGroup({
      id: currentItem.id,
      pid: currentItem.pid,
      name: currentItem.name,
      rules: convertArrayToObject(currentItem.rules),
      access: convertArrayToObject(currentItem.access),
      status: currentItem.status,
      created_at: currentItem.created_at
        ? dayjs(currentItem.created_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
      updated_at: currentItem.updated_at
        ? dayjs(currentItem.updated_at).format("YYYY-MM-DD HH:mm:ss")
        : null,
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
    await deleteUserGroup(id);
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
      await deleteUserGroup(numericId);
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
    const response = await fetchUserGroupItems({
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
});
</script>
