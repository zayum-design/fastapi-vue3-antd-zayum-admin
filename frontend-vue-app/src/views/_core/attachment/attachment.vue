<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['attachment.add','all']" type="code">
              <a-button
                type="primary"
                @click="openDialog(currentItem, 'add')"
              >
                <FileAddOutlined />
                {{ $t("common.add_item") }}
              </a-button>
            </AccessControl>
              <AccessControl :codes="['attachment.add','all']" type="code">
                <a-button
                  type="primary"
                  @click="openUploadDialog"
                >
                  <UploadOutlined />
                  {{ $t("common.upload") }}
                </a-button>
              </AccessControl>
              <AccessControl :codes="['attachment.delete','all']" type="code">
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
              <template v-if="column.key === 'thumb'">
                <div class="flex justify-center">
                  <img 
                    :src="getThumbnailUrl(record)" 
                    :alt="record.file_name || 'file'"
                    class="w-12 object-contain rounded border cursor-pointer hover:opacity-80"
                    @error="handleImageError"
                    @click="openAttachment(record)"
                  />
                </div>
              </template>
              <template v-if="column.key === 'file_size'">
                {{ formatFileSize(record.file_size) }}
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
                  <AccessControl :codes="['attachment.edit','all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
<AccessControl
                    :codes="['attachment.delete','all']"
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
        
        <a-form-item :label="$t('attachment.field.id')" v-if="mode !== 'add'">
        <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.category')" >
        <a-select
            v-model:value="currentItem.cat_id"
            :disabled="mode === 'view'"
            :placeholder="$t('common.select_placeholder')"
        >
            <a-select-option :value="0">{{ $t('common.no_category') }}</a-select-option>
            <a-select-option 
                v-for="category in hierarchicalCategories" 
                :key="category.id" 
                :value="category.id"
            >
                {{ category.displayName }}
            </a-select-option>
        </a-select>
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.admin_id')" name="admin_id" :rules="formRules.admin_id">
        <a-input v-model:value="currentItem.admin_id" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.user_id')" name="user_id" :rules="formRules.user_id">
        <a-input v-model:value="currentItem.user_id" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.att_type')" >
        <a-select
            v-model:value="currentItem.att_type"
            :disabled="mode === 'view'"
        >
            <a-select-option value="image">{{ $t("common.image") }}</a-select-option>
<a-select-option value="file">{{ $t("common.file") }}</a-select-option>
        </a-select>
        </a-form-item>
                
        <a-form-item :label="$t('attachment.field.thumb')" >
        <a-input v-model:value="currentItem.thumb" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.path_file')" name="path_file" :rules="formRules.path_file">
        <a-input v-model:value="currentItem.path_file" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.file_name')" >
        <a-input v-model:value="currentItem.file_name" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.file_size')" name="file_size" :rules="formRules.file_size">
        <a-input v-model:value="currentItem.file_size" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.mimetype')" >
        <a-input v-model:value="currentItem.mimetype" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.ext_param')" >
        <a-input v-model:value="currentItem.ext_param" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.storage')" name="storage" :rules="formRules.storage">
        <a-input v-model:value="currentItem.storage" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.sha1')" >
        <a-input v-model:value="currentItem.sha1" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.general_attachment_col')" >
        <a-input v-model:value="currentItem.general_attachment_col" :disabled="mode === 'view'" />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.created_at')" name="created_at">
        <a-date-picker
            v-model:value="currentItem.created_at"
            show-time
            :disabled="mode === 'view'"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
        />
        </a-form-item>
            
        <a-form-item :label="$t('attachment.field.updated_at')" name="updated_at">
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

    <!-- Upload Dialog -->
    <a-modal
      v-model:open="isUploadDialogVisible"
      :title="$t('common.upload')"
      @cancel="closeUploadDialog"
      :footer="null"
      :destroyOnClose="true"
      :maskClosable="false"
      width="800px"
    >
      <div class="upload-dialog-content">
        <!-- 文件上传区域 -->
        <a-upload-dragger
          name="file"
          :multiple="true"
          :show-upload-list="false"
          :before-upload="beforeUploadMultiple"
          @change="handleFileChange"
          class="upload-dragger"
        >
          <p class="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p class="ant-upload-text">
            {{ $t('attachment.upload.click_or_drag_multiple') }}
          </p>
          <p class="ant-upload-hint">
            {{ $t('attachment.upload.support_types_multiple') }}
          </p>
        </a-upload-dragger>
        
        <!-- 上传队列 -->
        <div v-if="uploadQueue.length > 0" class="mt-6">
          <h4 class="font-medium mb-3">{{ $t('attachment.upload.upload_queue') }} ({{ uploadQueue.length }})</h4>
          <div class="max-h-60 overflow-y-auto border rounded">
            <div 
              v-for="(item, index) in uploadQueue" 
              :key="item.id"
              class="p-3 border-b last:border-b-0 hover:bg-gray-50"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center flex-1 min-w-0">
                  <div class="mr-3">
                    <img 
                      v-if="item.file.type.startsWith('image/')" 
                      :src="getFilePreview(item.file)"
                      class="w-10 h-10 object-cover rounded border"
                      alt="preview"
                    />
                    <div 
                      v-else 
                      class="w-10 h-10 flex items-center justify-center bg-gray-100 rounded border"
                    >
                      <FileOutlined class="text-gray-500" />
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="font-medium truncate">{{ item.file.name }}</div>
                    <div class="text-sm text-gray-500">
                      {{ formatFileSize(item.file.size) }} • 
                      <span :class="{
                        'text-blue-500': item.status === 'pending',
                        'text-green-500': item.status === 'success',
                        'text-red-500': item.status === 'error',
                        'text-yellow-500': item.status === 'uploading'
                      }">
                        {{ getStatusText(item.status) }}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div class="ml-4 w-32">
                  <a-progress 
                    v-if="item.status === 'uploading' || item.status === 'success' || item.status === 'error'"
                    :percent="item.progress"
                    :status="item.status === 'error' ? 'exception' : (item.status === 'success' ? 'success' : 'active')"
                    size="small"
                  />
                  <span v-else class="text-gray-400 text-sm">{{ $t('attachment.upload.waiting') }}</span>
                </div>
                
                <div class="ml-4">
                  <a-button
                    v-if="item.status === 'pending' || item.status === 'error'"
                    size="small"
                    type="link"
                    danger
                    @click="removeFromQueue(index)"
                  >
                    <DeleteOutlined />
                  </a-button>
                  <a-button
                    v-if="item.status === 'error'"
                    size="small"
                    type="link"
                    @click="retryUpload(index)"
                  >
                    <RedoOutlined />
                  </a-button>
                </div>
              </div>
              
              <div v-if="item.error" class="mt-2 text-sm text-red-500">
                {{ item.error }}
              </div>
            </div>
          </div>
          
          <!-- 队列控制按钮 -->
          <div class="mt-4 flex justify-between items-center">
            <div>
              <span class="text-sm text-gray-600">
                {{ $t('attachment.upload.queue_summary', { 
                  total: uploadQueue.length, 
                  success: completedCount,
                  failed: failedCount,
                  pending: pendingCount
                }) }}
              </span>
            </div>
            <div class="space-x-2">
              <a-button
                v-if="!isUploadingQueue"
                type="primary"
                :disabled="pendingCount === 0"
                @click="startQueueUpload"
              >
                <UploadOutlined />
                {{ $t('attachment.upload.start_upload') }} ({{ pendingCount }})
              </a-button>
              <a-button
                v-else
                type="primary"
                danger
                @click="stopQueueUpload"
              >
                <PauseOutlined />
                {{ $t('attachment.upload.stop_upload') }}
              </a-button>
              <a-button
                @click="clearCompleted"
                :disabled="completedCount === 0 && failedCount === 0"
              >
                {{ $t('attachment.upload.clear_completed') }}
              </a-button>
              <a-button
                danger
                @click="clearQueue"
                :disabled="uploadQueue.length === 0"
              >
                {{ $t('attachment.upload.clear_all') }}
              </a-button>
            </div>
          </div>
        </div>
        
        <!-- 上传统计 -->
        <div v-if="uploadQueue.length > 0" class="mt-6">
          <a-progress 
            :percent="overallProgress" 
            :status="overallStatus"
            size="large"
          />
          <div class="mt-2 text-center text-sm text-gray-600">
            {{ $t('attachment.upload.overall_progress', { 
              percent: overallProgress,
              completed: completedCount,
              total: uploadQueue.length
            }) }}
          </div>
        </div>
        
        <div class="mt-6 flex justify-end">
          <a-button @click="closeUploadDialog" class="mr-2">
            {{ $t('common.cancel') }}
          </a-button>
          <a-button 
            type="primary" 
            @click="completeUpload"
            :disabled="completedCount === 0"
          >
            {{ $t('common.complete') }} ({{ completedCount }})
          </a-button>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from '@/_core/access';
import {
  fetchAttachmentItems,
  saveAttachment,
  deleteAttachment,
} from "@/api/admin/attachment";
import { fetchAttachmentCategoryItems } from "@/api/admin/attachment_category";
import { uploadApi } from "@/api/admin/upload";
import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  UploadOutlined,
  InboxOutlined,
  FileOutlined,
  PauseOutlined,
  RedoOutlined,
} from "@ant-design/icons-vue";
import { message, type FormInstance } from "ant-design-vue";

import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone';
import utc from 'dayjs/plugin/utc';
import { useAppConfig } from "@/_core/hooks";
const { attachmentURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

// Setup dayjs plugins
dayjs.extend(utc);
dayjs.extend(timezone);

const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || "Asia/Shanghai";
const form = ref<FormInstance | null>(null);

interface Attachment {
  id: number;
  cat_id: number | null;
  admin_id: number;
  user_id: number;
  att_type: string | null;
  thumb: string | null;
  path_file: string;
  file_name: string | null;
  file_size: number;
  mimetype: string | null;
  ext_param: string | null;
  storage: string;
  sha1: string | null;
  general_attachment_col: string | null;
  created_at: string;
  updated_at: string;
  
}

interface Category {
  id: number;
  name: string;
  pid: number;
  status: string;
  created_at: string;
  updated_at: string;
}

const currentItem: UnwrapRef<Attachment> = reactive({
  id: 0,
      cat_id: 0,
      admin_id: 0,
      user_id: 0,
      att_type: 'image',
      thumb: '',
      path_file: '',
      file_name: '',
      file_size: 0,
      mimetype: '',
      ext_param: '',
      storage: '',
      sha1: '',
      general_attachment_col: '',
      created_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      updated_at: dayjs().tz(TIME_ZONE).format('YYYY-MM-DD HH:mm:ss'),
      
});

const isDialogVisible = ref(false);
const confirmLoading = ref(false);
const isUploadDialogVisible = ref(false);
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
const categories = ref<Category[]>([]);

// 计算层级分类
const hierarchicalCategories = computed(() => {
  const buildHierarchy = (items: Category[], parentId: number = 0, level: number = 0): any[] => {
    const result: any[] = [];
    const children = items.filter(item => item.pid === parentId);
    
    children.forEach(child => {
      const displayName = '　'.repeat(level * 2) + child.name;
      result.push({
        ...child,
        displayName,
        level
      });
      
      // 递归处理子分类
      const grandchildren = buildHierarchy(items, child.id, level + 1);
      result.push(...grandchildren);
    });
    
    return result;
  };
  
  return buildHierarchy(categories.value);
});

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

// Validation rules
const formRules = reactive({
    admin_id: [
    { required: true, message: $t('attachment.rules.admin_id.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('attachment.rules.admin_id.must_be_number'));
    return Promise.resolve();
    }}
  ],
  user_id: [
    { required: true, message: $t('attachment.rules.user_id.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('attachment.rules.user_id.must_be_number'));
    return Promise.resolve();
    }}
  ],
  path_file: [
    { required: true, message: $t('attachment.rules.path_file.required') },
    { max: 255, message: $t('attachment.rules.path_file.max_length') }
  ],
  file_size: [
    { required: true, message: $t('attachment.rules.file_size.required') },
    { validator: (_: any, value: number) => {
    if (isNaN(value)) return Promise.reject($t('attachment.rules.file_size.must_be_number'));
    return Promise.resolve();
    }}
  ],
  storage: [
    { required: true, message: $t('attachment.rules.storage.required') },
    { max: 255, message: $t('attachment.rules.storage.max_length') }
  ],
  created_at: [
    { required: true, message: $t('attachment.rules.created_at.required') }
  ],
  updated_at: [
    { required: true, message: $t('attachment.rules.updated_at.required') }
  ],

});

const columns = computed(() => [
  { 
    title: $t('attachment.field.id'), 
    dataIndex: 'id', 
    key: 'id',
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  { title: $t('attachment.field.category'), dataIndex: 'cat_name', key: 'cat_name' },
  { title: $t('attachment.field.admin_id'), dataIndex: 'admin_id', key: 'admin_id' },
  { title: $t('attachment.field.user_id'), dataIndex: 'user_id', key: 'user_id' },
  { title: $t('attachment.field.att_type'), dataIndex: 'att_type', key: 'att_type' },
  { title: $t('attachment.field.thumb'), dataIndex: 'thumb', key: 'thumb' },
  // { title: $t('attachment.field.path_file'), dataIndex: 'path_file', key: 'path_file' },
  { title: $t('attachment.field.file_name'), dataIndex: 'file_name', key: 'file_name' },
  { title: $t('attachment.field.file_size'), dataIndex: 'file_size', key: 'file_size' },
  { 
    title: $t('attachment.field.created_at'), 
    dataIndex: 'created_at', 
    key: 'created_at',
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  { 
    title: $t('attachment.field.updated_at'), 
    dataIndex: 'updated_at', 
    key: 'updated_at',
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  { title: $t('common.actions'), key: 'actions', fixed: 'right', align: "center" },

]);

const onSelectChange = (selectedRowIds: Key[]) => {
  state.selectedRowIds = selectedRowIds;
};

const orderby = ref('');

const onTableChange = (pag: any, filters: any, sorter: any) => {
  console.log("onTableChange", pag, filters, sorter);
  pagination.value.current = pag.current;
  pagination.value.pageSize = pag.pageSize;
  
  // Handle sorting
  if (sorter && sorter.field) {
    const field = sorter.field;
    const order = sorter.order;
    if (order) {
      const direction = order === 'ascend' ? 'asc' : 'desc';
      orderby.value = `${field}_${direction}`;
    } else {
      orderby.value = '';
    }
  } else {
    orderby.value = '';
  }
  
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
      cat_id: 0,
      admin_id: 0,
      user_id: 0,
      att_type: 'image',
      thumb: '',
      path_file: '',
      file_name: '',
      file_size: 0,
      mimetype: '',
      ext_param: '',
      storage: '',
      sha1: '',
      general_attachment_col: '',
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
    await saveAttachment({
      cat_id: currentItem.cat_id,
      admin_id: currentItem.admin_id,
      user_id: currentItem.user_id,
      att_type: currentItem.att_type,
      thumb: currentItem.thumb,
      path_file: currentItem.path_file,
      file_name: currentItem.file_name,
      file_size: currentItem.file_size,
      mimetype: currentItem.mimetype,
      ext_param: currentItem.ext_param,
      storage: currentItem.storage,
      sha1: currentItem.sha1,
      general_attachment_col: currentItem.general_attachment_col,
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
    await saveAttachment({
      id: currentItem.id,
      cat_id: currentItem.cat_id,
      admin_id: currentItem.admin_id,
      user_id: currentItem.user_id,
      att_type: currentItem.att_type,
      thumb: currentItem.thumb,
      path_file: currentItem.path_file,
      file_name: currentItem.file_name,
      file_size: currentItem.file_size,
      mimetype: currentItem.mimetype,
      ext_param: currentItem.ext_param,
      storage: currentItem.storage,
      sha1: currentItem.sha1,
      general_attachment_col: currentItem.general_attachment_col,
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
    await deleteAttachment(id);
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
      await deleteAttachment(numericId);
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
    const response = await fetchAttachmentItems({
      page: pagination.value.current,
      perPage: pagination.value.pageSize,
      search: search.value,
      orderby: orderby.value,
    });
    items.value = response.items;
    pagination.value.total = response.total;
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  } finally {
    loading.value = false;
  }
};

// 获取分类数据
const fetchCategories = async () => {
  try {
    const response = await fetchAttachmentCategoryItems({
      page: 1,
      perPage: -1, // 获取所有分类
    });
    categories.value = response.items;
  } catch (error) {
    console.error("获取分类数据失败", error);
  }
};

// 获取缩略图URL
const getThumbnailUrl = (record: any) => {
  // 如果是图片类型，显示实际的图片地址
  if (record.att_type === 'image' && record.path_file) {
    return getAttachmentUrl(record.path_file);
  }
  
  // 如果是文件类型，根据文件扩展名显示对应的文件类型图标
  if (record.att_type === 'file' && record.file_name) {
    const extension = getFileExtension(record.file_name);
    return getFileTypeIcon(extension);
  }
  
  // 默认显示通用文件图标
  return '/src/assets/flie-type/file.png';
};

// 获取文件扩展名
const getFileExtension = (filename: string) => {
  const parts = filename.split('.');
  return parts.length > 1 ? parts[parts.length - 1].toLowerCase() : '';
};

// 根据文件扩展名获取对应的文件类型图标
const getFileTypeIcon = (extension: string) => {
  const iconMap: Record<string, string> = {
    'pdf': '/src/assets/flie-type/file-type-pdf.png',
    'doc': '/src/assets/flie-type/file-type-doc.png',
    'docx': '/src/assets/flie-type/file-type-docx.png',
    'xls': '/src/assets/flie-type/file-type-xls.png',
    'xlsx': '/src/assets/flie-type/file-type-xlsx.png',
    'ppt': '/src/assets/flie-type/file-type-ppt.png',
    'pptx': '/src/assets/flie-type/file-type-pptx.png',
    'txt': '/src/assets/flie-type/file-type-txt.png',
    'zip': '/src/assets/flie-type/file-type-zip.png',
    'rar': '/src/assets/flie-type/file-type-rar.png',
  };
  
  return iconMap[extension] || '/src/assets/flie-type/file.png';
};

// 获取附件完整URL
const getAttachmentUrl = (path: string): string => {
  // 如果路径为空或无效，返回空字符串
  if (!path || path.trim() === "") {
    return '';
  }
  
  // 如果路径已经是完整 URL（http/https）或本地 assets 路径，直接返回
  if (path.startsWith("http://") || path.startsWith("https://") || path.startsWith("/src/assets/")) {
    return path;
  }
  
  // 如果路径以 /uploads/ 开头，使用附件域名配置
  if (path.startsWith("/uploads/")) {
    return attachmentURL + path;
  }
  
  // 否则，添加附件域名前缀
  return attachmentURL + (path.startsWith("/") ? path : "/" + path);
};

// 在新窗口打开附件
const openAttachment = (record: any) => {
  if (record.att_type === 'image' && record.path_file) {
    const url = getAttachmentUrl(record.path_file);
    if (url) {
      window.open(url, '_blank');
    }
  } else if (record.att_type === 'file' && record.path_file) {
    const url = getAttachmentUrl(record.path_file);
    if (url) {
      window.open(url, '_blank');
    }
  }
};

// 图片加载错误处理
const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement;
  // 如果图片加载失败，显示图片错误图标
  img.src = '/src/assets/image-error.png';
};

// 格式化文件大小为MB
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 MB';
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(2)} MB`;
};

// 上传相关变量
const uploading = ref(false);
const uploadPercent = ref(0);
const uploadStatus = ref<'active' | 'success' | 'exception' | 'normal'>('active');
const uploadedFile = ref<File | null>(null);
const uploadResponseData = ref<any>(null);

// 队列上传相关变量
interface UploadQueueItem {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'success' | 'error';
  progress: number;
  error?: string;
  response?: any;
}

const uploadQueue = ref<UploadQueueItem[]>([]);
const isUploadingQueue = ref(false);
const currentUploadIndex = ref(-1);

// 计算属性
const completedCount = computed(() => {
  return uploadQueue.value.filter(item => item.status === 'success').length;
});

const failedCount = computed(() => {
  return uploadQueue.value.filter(item => item.status === 'error').length;
});

const pendingCount = computed(() => {
  return uploadQueue.value.filter(item => item.status === 'pending').length;
});

const overallProgress = computed(() => {
  if (uploadQueue.value.length === 0) return 0;
  const totalProgress = uploadQueue.value.reduce((sum, item) => sum + item.progress, 0);
  return Math.round(totalProgress / uploadQueue.value.length);
});

const overallStatus = computed(() => {
  if (failedCount.value > 0) return 'exception';
  if (completedCount.value === uploadQueue.value.length) return 'success';
  return 'active';
});

// 打开上传对话框
const openUploadDialog = () => {
  isUploadDialogVisible.value = true;
  resetUploadState();
};

// 关闭上传对话框
const closeUploadDialog = () => {
  isUploadDialogVisible.value = false;
  resetUploadState();
};

// 重置上传状态
const resetUploadState = () => {
  uploading.value = false;
  uploadPercent.value = 0;
  uploadStatus.value = 'active';
  uploadedFile.value = null;
  uploadResponseData.value = null;
  uploadQueue.value = [];
  isUploadingQueue.value = false;
  currentUploadIndex.value = -1;
};

// 上传前验证
const beforeUpload = (file: File) => {
  const isAllowedType = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain', 'text/csv'
  ].includes(file.type);
  
  const isLt10M = file.size / 1024 / 1024 < 10;
  
  if (!isAllowedType) {
    message.error($t('attachment.upload.unsupported_file_type'));
    return false;
  }
  
  if (!isLt10M) {
    message.error($t('attachment.upload.file_too_large'));
    return false;
  }
  
  return true;
};

// 处理上传
const handleUpload = async (options: any) => {
  const { file, onSuccess, onError, onProgress } = options;
  
  try {
    uploading.value = true;
    uploadPercent.value = 0;
    uploadStatus.value = 'active';
    uploadedFile.value = file;
    
    // 模拟上传进度
    const interval = setInterval(() => {
      if (uploadPercent.value < 90) {
        uploadPercent.value += 10;
        onProgress?.({ percent: uploadPercent.value });
      }
    }, 200);
    
    // 实际调用上传API
    const response = await uploadApi(file, 'images');
    
    clearInterval(interval);
    uploadPercent.value = 100;
    uploadStatus.value = 'success';
    onProgress?.({ percent: 100 });
    
    // 保存上传响应数据
    uploadResponseData.value = response;
    
    // 延迟一点时间显示成功状态
    setTimeout(() => {
      onSuccess?.(response);
      message.success($t('common.upload_success'));
      uploading.value = false;
    }, 500);
    
  } catch (error: any) {
    uploading.value = false;
    uploadPercent.value = 0;
    uploadStatus.value = 'exception';
    uploadedFile.value = null;
    onError?.(error);
    message.error(error.message || $t('common.upload_failed'));
  }
};

// ========== 队列上传相关方法 ==========

// 多文件上传前验证
const beforeUploadMultiple = (file: File) => {
  const isAllowedType = [
    'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
    'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain', 'text/csv'
  ].includes(file.type);
  
  const isLt10M = file.size / 1024 / 1024 < 10;
  
  if (!isAllowedType) {
    message.error($t('attachment.upload.unsupported_file_type'));
    return false;
  }
  
  if (!isLt10M) {
    message.error($t('attachment.upload.file_too_large'));
    return false;
  }
  
  return true;
};

// 处理文件选择变化
const handleFileChange = (info: any) => {
  const { fileList } = info;
  
  // 过滤掉已经上传完成的文件
  const newFiles = fileList.filter((file: any) => file.status === 'done' || file.status === 'uploading');
  
  // 将新文件添加到队列
  newFiles.forEach((file: any) => {
    if (file.originFileObj && !uploadQueue.value.some(item => item.file === file.originFileObj)) {
      const queueItem: UploadQueueItem = {
        id: Date.now() + '-' + Math.random().toString(36).substr(2, 9),
        file: file.originFileObj,
        status: 'pending',
        progress: 0
      };
      uploadQueue.value.push(queueItem);
    }
  });
};

// 获取文件预览URL
const getFilePreview = (file: File): string => {
  if (file.type.startsWith('image/')) {
    return URL.createObjectURL(file);
  }
  return '';
};

// 获取状态文本
const getStatusText = (status: string): string => {
  switch (status) {
    case 'pending': return $t('attachment.upload.status.pending');
    case 'uploading': return $t('attachment.upload.status.uploading');
    case 'success': return $t('attachment.upload.status.success');
    case 'error': return $t('attachment.upload.status.error');
    default: return status;
  }
};

// 从队列中移除文件
const removeFromQueue = (index: number) => {
  if (index >= 0 && index < uploadQueue.value.length) {
    const item = uploadQueue.value[index];
    // 如果正在上传，先停止
    if (item.status === 'uploading') {
      stopQueueUpload();
    }
    uploadQueue.value.splice(index, 1);
  }
};

// 重试上传
const retryUpload = (index: number) => {
  if (index >= 0 && index < uploadQueue.value.length) {
    const item = uploadQueue.value[index];
    item.status = 'pending';
    item.progress = 0;
    item.error = undefined;
    
    // 如果队列没有在上传，开始上传
    if (!isUploadingQueue.value) {
      startQueueUpload();
    }
  }
};

// 开始队列上传
const startQueueUpload = async () => {
  if (uploadQueue.value.length === 0 || pendingCount.value === 0) {
    return;
  }
  
  isUploadingQueue.value = true;
  currentUploadIndex.value = -1;
  
  // 开始上传第一个待上传的文件
  await uploadNextFile();
};

// 停止队列上传
const stopQueueUpload = () => {
  isUploadingQueue.value = false;
  if (currentUploadIndex.value >= 0 && currentUploadIndex.value < uploadQueue.value.length) {
    const currentItem = uploadQueue.value[currentUploadIndex.value];
    if (currentItem.status === 'uploading') {
      currentItem.status = 'pending';
      currentItem.progress = 0;
    }
  }
  currentUploadIndex.value = -1;
};

// 上传下一个文件
const uploadNextFile = async () => {
  if (!isUploadingQueue.value) {
    return;
  }
  
  // 查找下一个待上传的文件
  const nextIndex = uploadQueue.value.findIndex((item, index) => 
    item.status === 'pending' && index > currentUploadIndex.value
  );
  
  if (nextIndex === -1) {
    // 没有更多待上传的文件
    isUploadingQueue.value = false;
    currentUploadIndex.value = -1;
    return;
  }
  
  currentUploadIndex.value = nextIndex;
  const queueItem = uploadQueue.value[nextIndex];
  
  try {
    // 更新状态为上传中
    queueItem.status = 'uploading';
    queueItem.progress = 0;
    
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (queueItem.status === 'uploading' && queueItem.progress < 90) {
        queueItem.progress += 10;
      }
    }, 200);
    
    // 实际调用上传API
    const response = await uploadApi(queueItem.file, 'images');
    
    clearInterval(progressInterval);
    queueItem.progress = 100;
    queueItem.status = 'success';
    queueItem.response = response;
    
    // 延迟一点时间，然后上传下一个文件
    setTimeout(() => {
      if (isUploadingQueue.value) {
        uploadNextFile();
      }
    }, 500);
    
  } catch (error: any) {
    queueItem.status = 'error';
    queueItem.progress = 0;
    queueItem.error = error.message || $t('common.upload_failed');
    
    // 停止上传队列
    stopQueueUpload();
    
    message.error($t('common.upload_failed') + ': ' + queueItem.file.name);
  }
};

// 清除已完成的项目
const clearCompleted = () => {
  uploadQueue.value = uploadQueue.value.filter(item => 
    item.status !== 'success' && item.status !== 'error'
  );
};

// 清除整个队列
const clearQueue = () => {
  stopQueueUpload();
  uploadQueue.value = [];
};

// 完成队列上传
const completeQueueUpload = async () => {
  if (completedCount.value === 0) {
    message.warning($t('attachment.upload.no_completed_files'));
    return;
  }
  
  // 关闭对话框
  closeUploadDialog();
  
  // 刷新页面数据
  fetchItems();
  
  message.success($t('common.upload_success_multiple', { count: completedCount.value }));
};

// 修改completeUpload以支持队列
const completeUpload = () => {
  if (uploadQueue.value.length > 0) {
    completeQueueUpload();
  } else {
    // 保持原有的单文件上传逻辑
    if (!uploadedFile.value || !uploadResponseData.value) {
      message.warning($t('attachment.upload.please_upload_first'));
      return;
    }
    
    closeUploadDialog();
    fetchItems();
    message.success($t('common.upload_success'));
  }
};

onMounted(() => {
  fetchItems();
  fetchCategories();
});
</script>
