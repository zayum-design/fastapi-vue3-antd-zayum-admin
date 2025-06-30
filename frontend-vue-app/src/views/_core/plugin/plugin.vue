<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['plugin.add','all']" type="code">
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
              <AccessControl :codes="['plugin.delete','all']" type="code">
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
                  <AccessControl :codes="['plugin.edit','all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
                  <AccessControl
                    :codes="['plugin.delete','all']"
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
        
        <a-form-item :label="$t('plugin.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.title')" name="title" :rules="formRules.title">
          <a-input v-model:value="currentItem.title" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.author')" name="author" :rules="formRules.author">
          <a-input v-model:value="currentItem.author" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.uuid')" name="uuid" :rules="formRules.uuid">
          <a-input v-model:value="currentItem.uuid" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.description')" name="description" :rules="formRules.description">
          <a-input v-model:value="currentItem.description" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.version')" name="version" :rules="formRules.version">
          <a-input v-model:value="currentItem.version" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.downloads')" name="downloads" :rules="formRules.downloads">
          <a-input v-model:value="currentItem.downloads" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.download_url')" name="download_url" :rules="formRules.download_url">
          <a-input v-model:value="currentItem.download_url" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.md5_hash')" name="md5_hash" :rules="formRules.md5_hash">
          <a-input v-model:value="currentItem.md5_hash" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.price')" name="price" :rules="formRules.price">
          <a-input v-model:value="currentItem.price" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.paid')" name="paid" :rules="formRules.paid">
          <a-input v-model:value="currentItem.paid" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.installed')" name="installed" :rules="formRules.installed">
          <a-input v-model:value="currentItem.installed" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.enabled')" name="enabled" :rules="formRules.enabled">
          <a-input v-model:value="currentItem.enabled" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.setting_menu')" name="setting_menu" :rules="formRules.setting_menu">
          <a-input v-model:value="currentItem.setting_menu" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.created_at')" name="created_at">
          <a-date-picker
            v-model:value="currentItem.created_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.updated_at')" name="updated_at">
          <a-date-picker
            v-model:value="currentItem.updated_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
          />
        </a-form-item>
            
        <a-form-item :label="$t('plugin.status')" :rules="formRules.status">
          <a-select
            v-model:value="currentItem.status"
            :disabled="mode === 'view'"
          >
            <a-select-option value="normal">{{ $t("common.normal") }}</a-select-option>
<a-select-option value="hidden">{{ $t("common.hidden") }}</a-select-option>
          </a-select>
        </a-form-item>
                
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from '@/_core/access';
import {
  fetchPluginItems,
  savePlugin,
  deletePlugin,
} from "@/api/admin/plugin";
import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
} from "@ant-design/icons-vue";
import { message, type FormInstance } from "ant-design-vue";
import moment from "moment-timezone";

const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || "Asia/Shanghai";
const form = ref<FormInstance | null>(null);

interface Plugin {
  id: number;
  title: string;
  author: string;
  uuid: string;
  description: string;
  version: string;
  downloads: number;
  download_url: string;
  md5_hash: string;
  price: any;
  paid: number;
  installed: number;
  enabled: number;
  setting_menu: string;
  created_at: string | null;
  updated_at: string | null;
  status: string;
  
}

const currentItem: UnwrapRef<Plugin> = reactive({
  id: 0,
      title: '',
      author: '',
      uuid: '',
      description: '',
      version: '',
      downloads: 0,
      download_url: '',
      md5_hash: '',
      price: 0.0,
      paid: 0,
      installed: 0,
      enabled: 0,
      setting_menu: '',
      created_at: moment().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      updated_at: moment().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      status: 'normal',
      
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
  
      title: [
        { required: true, message: $t('common.field_required') },
      ],
                
      author: [
        { required: true, message: $t('common.field_required') },
      ],
                
      uuid: [
        { required: true, message: $t('common.field_required') },
      ],
                
      description: [
        { required: true, message: $t('common.field_required') },
      ],
                
      version: [
        { required: true, message: $t('common.field_required') },
      ],
                
      downloads: [
        { required: true, message: $t('common.field_required') },
      ],
                
      download_url: [
        { required: true, message: $t('common.field_required') },
      ],
                
      md5_hash: [
        { required: true, message: $t('common.field_required') },
      ],
                
      price: [
        { required: true, message: $t('common.field_required') },
      ],
                
      paid: [
        { required: true, message: $t('common.field_required') },
      ],
                
      installed: [
        { required: true, message: $t('common.field_required') },
      ],
                
      enabled: [
        { required: true, message: $t('common.field_required') },
      ],
                
      setting_menu: [
        { required: true, message: $t('common.field_required') },
      ],
                
      status: [
        { required: true, message: $t('common.field_required') },
      ],
                
});

const columns = computed(() => [
  
      { title: $t('plugin.id'), dataIndex: 'id', key: 'id' },
            
      { title: $t('plugin.title'), dataIndex: 'title', key: 'title' },
            
      { title: $t('plugin.author'), dataIndex: 'author', key: 'author' },
            
      { title: $t('plugin.uuid'), dataIndex: 'uuid', key: 'uuid' },
            
      { title: $t('plugin.description'), dataIndex: 'description', key: 'description' },
            
      { title: $t('plugin.version'), dataIndex: 'version', key: 'version' },
            
      { title: $t('plugin.downloads'), dataIndex: 'downloads', key: 'downloads' },
            
      { title: $t('plugin.download_url'), dataIndex: 'download_url', key: 'download_url' },
            
      { title: $t('plugin.md5_hash'), dataIndex: 'md5_hash', key: 'md5_hash' },
            
      { title: $t('plugin.price'), dataIndex: 'price', key: 'price' },
            
      { title: $t('plugin.paid'), dataIndex: 'paid', key: 'paid' },
            
      { title: $t('plugin.installed'), dataIndex: 'installed', key: 'installed' },
            
      { title: $t('plugin.enabled'), dataIndex: 'enabled', key: 'enabled' },
            
      { title: $t('plugin.setting_menu'), dataIndex: 'setting_menu', key: 'setting_menu' },
            
      { title: $t('plugin.created_at'), dataIndex: 'created_at', key: 'created_at' },
            
      { title: $t('plugin.updated_at'), dataIndex: 'updated_at', key: 'updated_at' },
            
      { title: $t('plugin.status'), dataIndex: 'status', key: 'status' },
            
      { title: $t('common.actions'), key: 'actions',fixed: 'right',align:"center" },
            
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
      currentItem.created_at = moment(currentItem.created_at).tz(TIME_ZONE);
    }
            
    if (currentItem.updated_at) {
      currentItem.updated_at = moment(currentItem.updated_at).tz(TIME_ZONE);
    }
            
  }
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
      title: '',
      author: '',
      uuid: '',
      description: '',
      version: '',
      downloads: 0,
      download_url: '',
      md5_hash: '',
      price: 0.0,
      paid: 0,
      installed: 0,
      enabled: 0,
      setting_menu: '',
      created_at: null,
      updated_at: null,
      status: 'normal',
      
  });
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const onSubmit = async () => {
  confirmLoading.value = true;
  try {
    // Validate the form before submission
    await form.value?.validate();
    if (mode.value === "add") {
      await saveItem();
      resetCurrentItem();
    } else if (mode.value === "edit") {
      await updateItem();
    }
    closeDialog();
  } catch (error) {
    // Handle validation errors
    console.error($t("common.form_validation_failed"), error);
  } finally {
    confirmLoading.value = false;
    fetchItems();
  }
};

const saveItem = async () => {
  try {
    await savePlugin({
      title: currentItem.title,
      author: currentItem.author,
      uuid: currentItem.uuid,
      description: currentItem.description,
      version: currentItem.version,
      downloads: currentItem.downloads,
      download_url: currentItem.download_url,
      md5_hash: currentItem.md5_hash,
      price: currentItem.price,
      paid: currentItem.paid,
      installed: currentItem.installed,
      enabled: currentItem.enabled,
      setting_menu: currentItem.setting_menu,
      created_at: currentItem.created_at ? moment(currentItem.created_at).format('YYYY-MM-DD HH:mm:ss') : null,
      updated_at: currentItem.updated_at ? moment(currentItem.updated_at).format('YYYY-MM-DD HH:mm:ss') : null,
      status: currentItem.status,
      
    });
    message.success($t("common.save_success"));
  } catch (error) {
    console.error($t("common.save_item_failed"), error);
  }
};

const updateItem = async () => {
  try {
    await savePlugin({
      id: currentItem.id,
      title: currentItem.title,
      author: currentItem.author,
      uuid: currentItem.uuid,
      description: currentItem.description,
      version: currentItem.version,
      downloads: currentItem.downloads,
      download_url: currentItem.download_url,
      md5_hash: currentItem.md5_hash,
      price: currentItem.price,
      paid: currentItem.paid,
      installed: currentItem.installed,
      enabled: currentItem.enabled,
      setting_menu: currentItem.setting_menu,
      created_at: currentItem.created_at ? moment(currentItem.created_at).format('YYYY-MM-DD HH:mm:ss') : null,
      updated_at: currentItem.updated_at ? moment(currentItem.updated_at).format('YYYY-MM-DD HH:mm:ss') : null,
      status: currentItem.status,
      
    });
    message.success($t("common.update_success"));
  } catch (error) {
    console.error($t("common.update_item_failed"), error);
  }
};

const deleteItem = async (id: number) => {
  try {
    await deletePlugin(id);
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
      await deletePlugin(numericId);
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
    const response = await fetchPluginItems({
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
