<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl
                :codes="['user_balance_log.delete', 'all']"
                type="code"
              >
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
                    :codes="['user_balance_log.delete', 'all']"
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
        <a-form-item
          :label="$t('user.balance_log.field.id')"
          v-if="mode !== 'add'"
        >
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item
          :label="$t('user.balance_log.field.user_id')"
          name="user_id"
          :rules="formRules.user_id"
        >
          <a-input
            v-model:value="currentItem.user_id"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('user.balance_log.field.balance')"
          name="balance"
          :rules="formRules.balance"
        >
          <a-input
            v-model:value="currentItem.balance"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('user.balance_log.field.before')"
          name="before"
          :rules="formRules.before"
        >
          <a-input
            v-model:value="currentItem.before"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('user.balance_log.field.after')"
          name="after"
          :rules="formRules.after"
        >
          <a-input
            v-model:value="currentItem.after"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.memo')">
          <a-input
            v-model:value="currentItem.memo"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('user.balance_log.field.created_at')"
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
          :label="$t('user.balance_log.field.updated_at')"
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
  fetchUserBalanceLogItems,
  saveUserBalanceLog,
  deleteUserBalanceLog,
} from "@/api/admin/user_balance_log";
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

interface UserBalanceLog {
  id: number;
  user_id: number;
  balance: any;
  before: any;
  after: any;
  memo: string | null;
  created_at: string;
  updated_at: string;
}

const currentItem: UnwrapRef<UserBalanceLog> = reactive({
  id: 0,
  user_id: 0,
  balance: 0.0,
  before: 0.0,
  after: 0.0,
  memo: "",
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
  user_id: [
    { required: true, message: $t("user.balance_log.rules.user_id.required") },
    {
      validator: (_: any, value: number) => {
        if (isNaN(value))
          return Promise.reject(
            $t("user.balance_log.rules.user_id.must_be_number")
          );
        return Promise.resolve();
      },
    },
  ],
  balance: [
    { required: true, message: $t("user.balance_log.rules.balance.required") },
  ],
  before: [
    { required: true, message: $t("user.balance_log.rules.before.required") },
  ],
  after: [
    { required: true, message: $t("user.balance_log.rules.after.required") },
  ],
  created_at: [
    {
      required: true,
      message: $t("user.balance_log.rules.created_at.required"),
    },
  ],
  updated_at: [
    {
      required: true,
      message: $t("user.balance_log.rules.updated_at.required"),
    },
  ],
});

const columns = computed(() => [
  { title: $t("user.balance_log.field.id"), dataIndex: "id", key: "id" },
  {
    title: $t("user.balance_log.field.user_id"),
    dataIndex: "user_id",
    key: "user_id",
  },
  {
    title: $t("user.balance_log.field.balance"),
    dataIndex: "balance",
    key: "balance",
  },
  {
    title: $t("user.balance_log.field.before"),
    dataIndex: "before",
    key: "before",
  },
  {
    title: $t("user.balance_log.field.after"),
    dataIndex: "after",
    key: "after",
  },
  { title: $t("user.balance_log.field.memo"), dataIndex: "memo", key: "memo" },
  {
    title: $t("user.balance_log.field.created_at"),
    dataIndex: "created_at",
    key: "created_at",
  },
  {
    title: $t("user.balance_log.field.updated_at"),
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

const openDialog = (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    Object.assign(currentItem, item);

    if (currentItem.created_at) {
      item.created_at = dayjs(currentItem.created_at).tz(TIME_ZONE);
    }

    if (currentItem.updated_at) {
      item.updated_at = dayjs(currentItem.updated_at).tz(TIME_ZONE);
    }
  }
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    user_id: 0,
    balance: 0.0,
    before: 0.0,
    after: 0.0,
    memo: "",
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
    await saveUserBalanceLog({
      user_id: currentItem.user_id,
      balance: currentItem.balance,
      before: currentItem.before,
      after: currentItem.after,
      memo: currentItem.memo,
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
    await saveUserBalanceLog({
      id: currentItem.id,
      user_id: currentItem.user_id,
      balance: currentItem.balance,
      before: currentItem.before,
      after: currentItem.after,
      memo: currentItem.memo,
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
    await deleteUserBalanceLog(id);
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
      await deleteUserBalanceLog(numericId);
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
    const response = await fetchUserBalanceLogItems({
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
