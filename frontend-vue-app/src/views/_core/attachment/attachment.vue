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
                    class="w-12 h-12 object-cover rounded border cursor-pointer hover:opacity-80"
                    @error="handleImageError"
                    @click="openAttachment(record)"
                  />
                </div>
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
import { useAppConfig } from "@/_core/hooks";
const { webURL } = useAppConfig(import.meta.env, import.meta.env.PROD);

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
  { title: $t('attachment.field.id'), dataIndex: 'id', key: 'id' },
{ title: $t('attachment.field.category'), dataIndex: 'cat_name', key: 'cat_name' },
{ title: $t('attachment.field.admin_id'), dataIndex: 'admin_id', key: 'admin_id' },
{ title: $t('attachment.field.user_id'), dataIndex: 'user_id', key: 'user_id' },
{ title: $t('attachment.field.att_type'), dataIndex: 'att_type', key: 'att_type' },
{ title: $t('attachment.field.thumb'), dataIndex: 'thumb', key: 'thumb' },
{ title: $t('attachment.field.path_file'), dataIndex: 'path_file', key: 'path_file' },
{ title: $t('attachment.field.file_name'), dataIndex: 'file_name', key: 'file_name' },
{ title: $t('attachment.field.file_size'), dataIndex: 'file_size', key: 'file_size' },
{ title: $t('attachment.field.created_at'), dataIndex: 'created_at', key: 'created_at' },
{ title: $t('attachment.field.updated_at'), dataIndex: 'updated_at', key: 'updated_at' },
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
  
  // 如果路径已经是完整 URL 或本地 assets 路径，直接返回
  if (path.startsWith(webURL) || path.startsWith("/src/assets/")) {
    return path;
  }
  
  // 如果路径以 /uploads/ 开头，转换为 API 路径
  if (path.startsWith("/uploads/")) {
    return webURL + "/api/common" + path;
  }
  
  // 否则，添加 webURL 前缀
  return webURL + path;
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

onMounted(() => {
  fetchItems();
  fetchCategories();
});
</script>
