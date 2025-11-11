<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['user_rule.add','all']" type="code">
              <a-button
                type="primary"
                @click="openDialog(currentItem, 'add')"
              >
                <FileAddOutlined />
                {{ $t("common.add_item") }}
              </a-button>
            </AccessControl>
              <AccessControl :codes="['user_rule.delete','all']" type="code">
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
                  <AccessControl :codes="['user_rule.edit','all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
<AccessControl
                    :codes="['user_rule.delete','all']"
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
        
        <a-form-item :label="$t('user.rule.field.id')" v-if="mode !== 'add'">
        <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.rule_type')" name="rule_type" :rules="formRules.rule_type">
        <a-select
            v-model:value="currentItem.rule_type"
            :disabled="mode === 'view'"
        >
            <a-select-option value="menu">{{ $t("common.menu") }}</a-select-option>
<a-select-option value="action">{{ $t("common.action") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('user.rule.field.parent_id')" name="parent_id" :rules="formRules.parent_id">
        <a-input v-model:value="currentItem.parent_id" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.name')" name="name" :rules="formRules.name">
        <a-input v-model:value="currentItem.name" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.path')" name="path" :rules="formRules.path">
        <a-input v-model:value="currentItem.path" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.component')" >
        <a-input v-model:value="currentItem.component" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.redirect')" >
        <a-input v-model:value="currentItem.redirect" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.meta')" >
        <a-input v-model:value="currentItem.meta" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.permission')" >
        <a-input v-model:value="currentItem.permission" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.menu_display_type')" >
        <a-select
            v-model:value="currentItem.menu_display_type"
            :disabled="mode === 'view'"
        >
            <a-select-option value="ajax">{{ $t("common.ajax") }}</a-select-option>
<a-select-option value="addtabs">{{ $t("common.addtabs") }}</a-select-option>
<a-select-option value="blank">{{ $t("common.blank") }}</a-select-option>
<a-select-option value="dialog">{{ $t("common.dialog") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('user.rule.field.model_name')" name="model_name" :rules="formRules.model_name">
        <a-input v-model:value="currentItem.model_name" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.deleted_at')" name="deleted_at">
        <a-date-picker
            v-model:value="currentItem.deleted_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.weigh')" name="weigh" :rules="formRules.weigh">
        <a-input v-model:value="currentItem.weigh" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.status')" name="status" :rules="formRules.status">
        <a-select
            v-model:value="currentItem.status"
            :disabled="mode === 'view'"
        >
            <a-select-option value="normal">{{ $t("common.normal") }}</a-select-option>
<a-select-option value="hidden">{{ $t("common.hidden") }}</a-select-option>
<a-select-option value="deleted">{{ $t("common.deleted") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('user.rule.field.created_at')" name="created_at">
        <a-date-picker
            v-model:value="currentItem.created_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            
        <a-form-item :label="$t('user.rule.field.updated_at')" name="updated_at">
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
  fetchUserRuleItems,
  saveUserRule,
  deleteUserRule,
} from "@/api/admin/user_rule";
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

interface UserRule {
  id: number;
  rule_type: string;
  parent_id: number;
  name: string;
  path: string;
  component: string | null;
  redirect: string | null;
  meta: any | null;
  permission: any | null;
  menu_display_type: string | null;
  model_name: string;
  deleted_at: string | null;
  weigh: number;
  status: string;
  created_at: string;
  updated_at: string;
  
}

const currentItem: UnwrapRef<UserRule> = reactive({
  id: 0,
      rule_type: 'menu',
      parent_id: 0,
      name: '',
      path: '',
      component: '',
      redirect: '',
      meta: '',
      permission: '',
      menu_display_type: 'addtabs',
      model_name: '',
      deleted_at: null,
      weigh: 0,
      status: 'normal',
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
const formRules = reactive({
    rule_type: [
    { required: true, message: $t('user.rule.rules.rule_type.required') }
  ],
  parent_id: [
    { required: true, message: $t('user.rule.rules.parent_id.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('user.rule.rules.parent_id.must_be_number'));
    return Promise.resolve();
    }}
  ],
  name: [
    { required: true, message: $t('user.rule.rules.nickname.required') },
    { min: 2, message: $t('user.rule.rules.nickname.min_length') },
    { max: 30, message: $t('user.rule.rules.nickname.max_length') }
  ],
  path: [
    { required: true, message: $t('user.rule.rules.path.required') },
    { max: 255, message: $t('user.rule.rules.path.max_length') }
  ],
  model_name: [
    { required: true, message: $t('user.rule.rules.nickname.required') },
    { min: 2, message: $t('user.rule.rules.nickname.min_length') },
    { max: 30, message: $t('user.rule.rules.nickname.max_length') }
  ],
  weigh: [
    { required: true, message: $t('user.rule.rules.weigh.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('user.rule.rules.weigh.must_be_number'));
    return Promise.resolve();
    }}
  ],
  status: [
    { required: true, message: $t('user.rule.rules.status.required') }
  ],
  created_at: [
    { required: true, message: $t('user.rule.rules.created_at.required') }
  ],
  updated_at: [
    { required: true, message: $t('user.rule.rules.updated_at.required') }
  ],

});

const columns = computed(() => [
  { title: $t('user.rule.field.id'), dataIndex: 'id', key: 'id' },
{ title: $t('user.rule.field.rule_type'), dataIndex: 'rule_type', key: 'rule_type' },
{ title: $t('user.rule.field.parent_id'), dataIndex: 'parent_id', key: 'parent_id' },
{ title: $t('user.rule.field.name'), dataIndex: 'name', key: 'name' },
{ title: $t('user.rule.field.path'), dataIndex: 'path', key: 'path' },
{ title: $t('user.rule.field.component'), dataIndex: 'component', key: 'component' },
{ title: $t('user.rule.field.redirect'), dataIndex: 'redirect', key: 'redirect' },
{ title: $t('user.rule.field.meta'), dataIndex: 'meta', key: 'meta' },
{ title: $t('user.rule.field.permission'), dataIndex: 'permission', key: 'permission' },
{ title: $t('user.rule.field.menu_display_type'), dataIndex: 'menu_display_type', key: 'menu_display_type' },
{ title: $t('user.rule.field.model_name'), dataIndex: 'model_name', key: 'model_name' },
{ title: $t('user.rule.field.deleted_at'), dataIndex: 'deleted_at', key: 'deleted_at' },
{ title: $t('user.rule.field.weigh'), dataIndex: 'weigh', key: 'weigh' },
{ title: $t('user.rule.field.status'), dataIndex: 'status', key: 'status' },
{ title: $t('user.rule.field.created_at'), dataIndex: 'created_at', key: 'created_at' },
{ title: $t('user.rule.field.updated_at'), dataIndex: 'updated_at', key: 'updated_at' },
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

const openDialog = (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    Object.assign(currentItem, item);
    
    if (currentItem.deleted_at) {
        item.deleted_at = dayjs(currentItem.deleted_at).tz(TIME_ZONE);
    }
            
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
      rule_type: 'menu',
      parent_id: 0,
      name: '',
      path: '',
      component: '',
      redirect: '',
      meta: '',
      permission: '',
      menu_display_type: 'addtabs',
      model_name: '',
      deleted_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      weigh: 0,
      status: 'normal',
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
    await saveUserRule({
      rule_type: currentItem.rule_type,
      parent_id: currentItem.parent_id,
      name: currentItem.name,
      path: currentItem.path,
      component: currentItem.component,
      redirect: currentItem.redirect,
      meta: currentItem.meta,
      permission: currentItem.permission,
      menu_display_type: currentItem.menu_display_type,
      model_name: currentItem.model_name,
      deleted_at: currentItem.deleted_at ? dayjs(currentItem.deleted_at).format('YYYY-MM-DD HH:mm:ss') : null,
      weigh: currentItem.weigh,
      status: currentItem.status,
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
    await saveUserRule({
      id: currentItem.id,
      rule_type: currentItem.rule_type,
      parent_id: currentItem.parent_id,
      name: currentItem.name,
      path: currentItem.path,
      component: currentItem.component,
      redirect: currentItem.redirect,
      meta: currentItem.meta,
      permission: currentItem.permission,
      menu_display_type: currentItem.menu_display_type,
      model_name: currentItem.model_name,
      deleted_at: currentItem.deleted_at ? dayjs(currentItem.deleted_at).format('YYYY-MM-DD HH:mm:ss') : null,
      weigh: currentItem.weigh,
      status: currentItem.status,
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
    await deleteUserRule(id);
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
      await deleteUserRule(numericId);
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
    const response = await fetchUserRuleItems({
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
