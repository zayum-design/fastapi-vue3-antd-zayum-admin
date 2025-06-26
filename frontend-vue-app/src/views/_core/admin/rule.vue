<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['admin.rule.add', 'all']" type="code">
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
              <AccessControl :codes="['admin.rule.delete', 'all']" type="code">
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
              <template v-if="column.key === 'meta'">
                {{ formatMeta(record.meta) }}
              </template>
              <template v-if="column.key === 'permission'">
                {{ formatPermission(record.permission) }}
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
                  <AccessControl
                    :codes="['admin.rule.edit', 'all']"
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
                    :codes="['admin.rule.delete', 'all']"
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
      :width="800"
    >
      <a-form
        :model="currentItem"
        :label-col="labelCol"
        :wrapper-col="wrapperCol"
        ref="form"
        :rules="formRules"
      >
        <a-form-item :label="$t('admin.rule.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.rule_type')"
          :rules="formRules.rule_type"
        >
          <a-select
            v-model:value="currentItem.rule_type"
            :disabled="mode === 'view'"
          >
            <a-select-option value="menu">{{
              $t("admin.rule.menu")
            }}</a-select-option>
            <a-select-option value="action">{{
              $t("admin.rule.action")
            }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.parent_id')"
          name="parent_id"
          :rules="formRules.parent_id"
        >
          <a-input
            v-model:value="currentItem.parent_id"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.name')"
          name="name"
          :rules="formRules.name"
        >
          <a-input
            v-model:value="currentItem.name"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.path')"
          name="path"
          :rules="formRules.path"
        >
          <a-input
            v-model:value="currentItem.path"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.component')"
          name="component"
          :rules="formRules.component"
        >
          <a-input
            v-model:value="currentItem.component"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.redirect')"
          name="redirect"
          :rules="formRules.redirect"
        >
          <a-input
            v-model:value="currentItem.redirect"
            :disabled="mode === 'view'"
          />
        </a-form-item>
        <a-form-item
          :label="$t('admin.rule.meta')"
          name="meta"
          :rules="formRules.meta"
        >
          <div
            v-for="(item, index) in metaItems"
            :key="index"
            class="meta-item"
          >
            <a-input
              v-model:value="item.key"
              placeholder="Key"
              :disabled="mode === 'view'"
            />
            <a-input
              v-model:value="item.value"
              placeholder="Value"
              :disabled="mode === 'view'"
            />
            <a-button
              type="link"
              @click="removeMetaItem(index)"
              :disabled="mode === 'view'"
            >
              <CloseOutlined />
            </a-button>
          </div>
          <a-button
            type="dashed"
            @click="addMetaItem"
            :disabled="mode === 'view'"
          >
            {{ $t("common.add") }}
          </a-button>
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.permission')"
          name="permission"
          :rules="formRules.permission"
        >
          <a-checkbox-group v-model:value="permissionItems">
            <a-space>
              <a-checkbox value="add">{{ $t("common.add") }}</a-checkbox>
              <a-checkbox value="edit">{{ $t("common.edit") }}</a-checkbox>
              <a-checkbox value="delete">{{ $t("common.delete") }}</a-checkbox>
              <a-checkbox value="view">{{ $t("common.view") }}</a-checkbox>
            </a-space>
          </a-checkbox-group>
          <div
            v-for="(item, index) in otherPermissionItems"
            :key="index"
            class="permission-item"
          >
            <a-space>
              <a-input
                v-model:value="item.value"
                placeholder="Other Permission"
                :disabled="mode === 'view'" />

              <a-button
                type="link"
                @click="removeOtherPermissionItem(index)"
                :disabled="mode === 'view'"
              >
                <CloseOutlined /> </a-button
            ></a-space>
          </div>
          <a-space>
            <a-button
              type="dashed"
              @click="addOtherPermissionItem"
              :disabled="mode === 'view'"
            >
              {{ $t("common.add") }}
            </a-button></a-space
          >
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.menu_display_type')"
          :rules="formRules.menu_display_type"
        >
          <a-select
            v-model:value="currentItem.menu_display_type"
            :disabled="mode === 'view'"
          >
            <a-select-option value="ajax">{{
              $t("admin.rule.ajax")
            }}</a-select-option>
            <a-select-option value="addtabs">{{
              $t("admin.rule.addtabs")
            }}</a-select-option>
            <a-select-option value="blank">{{
              $t("admin.rule.blank")
            }}</a-select-option>
            <a-select-option value="dialog">{{
              $t("admin.rule.dialog")
            }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.model_name')"
          name="model_name"
          :rules="formRules.model_name"
        >
          <a-input
            v-model:value="currentItem.model_name"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.weigh')"
          name="weigh"
          :rules="formRules.weigh"
        >
          <a-input
            v-model:value="currentItem.weigh"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.rule.status')" :rules="formRules.status">
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
            <a-select-option value="deleted">{{
              $t("common.deleted")
            }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef, h } from "vue";
import { AccessControl } from "@/_core/access";
import {
  fetchAdminRuleItems,
  saveAdminRule,
  deleteAdminRule,
} from "@/api/core/admin_rule";
import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  CloseOutlined,
} from "@ant-design/icons-vue";
import { message, type FormInstance } from "ant-design-vue";
const form = ref<FormInstance | null>(null);

interface AdminRule {
  id: number;
  rule_type: string;
  parent_id: number | null;
  name: string;
  path: string;
  component: string | null;
  redirect: string | null;
  meta: any | null;
  permission: any | null;
  menu_display_type: string | null;
  model_name: string;
  weigh: number;
  status: string;
}

const currentItem: UnwrapRef<AdminRule> = reactive({
  id: 0,
  rule_type: "menu",
  parent_id: 0,
  name: "",
  path: "",
  component: "",
  redirect: "",
  meta: null,
  permission: null,
  menu_display_type: "ajax",
  model_name: "",
  weigh: 0,
  status: "normal",
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
const pagination = ref({ current: 1, pageSize: 1000, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

// Validation rules
const formRules = reactive({
  rule_type: [{ required: true, message: $t("common.field_required") }],

  name: [{ required: true, message: $t("common.field_required") }],

  path: [{ required: true, message: $t("common.field_required") }],

  component: [{ required: true, message: $t("common.field_required") }],

  model_name: [{ required: true, message: $t("common.field_required") }],

  weigh: [{ required: true, message: $t("common.field_required") }],

  status: [{ required: true, message: $t("common.field_required") }],
});

const columns = computed(() => [
  { key: "tree", align: "center" },

  { title: $t("admin.rule.id"), dataIndex: "id", align: "center", key: "id" },

  {
    title: $t("admin.rule.rule_type"),
    dataIndex: "rule_type",
    key: "rule_type",
  },

  {
    title: $t("admin.rule.parent_id"),
    dataIndex: "parent_id",
    key: "parent_id",
    width: 90,
  },

  { title: $t("admin.rule.name"), dataIndex: "name", key: "name" },

  { title: $t("admin.rule.path"), dataIndex: "path", key: "path" },

  // { title: $t('admin.rule.component'), dataIndex: 'component', key: 'component' },

  // { title: $t("admin.rule.redirect"), dataIndex: "redirect", key: "redirect" },

  // {
  //   title: $t("admin.rule.meta"),
  //   dataIndex: "meta",
  //   key: "meta",
  //   customRender: ({ text }: { text: any }) => formatMeta(text),
  // },

  {
    title: $t("admin.rule.permission"),
    dataIndex: "permission",
    key: "permission",
    customRender: ({ text }: { text: any }) => formatPermission(text),
  },

  {
    title: $t("admin.rule.menu_display_type"),
    dataIndex: "menu_display_type",
    key: "menu_display_type",
  },

  {
    title: $t("admin.rule.model_name"),
    dataIndex: "model_name",
    key: "model_name",
  },

  { title: $t("admin.rule.weigh"), dataIndex: "weigh", key: "weigh" },

  { title: $t("admin.rule.status"), dataIndex: "status", key: "status" },

  {
    title: $t("common.actions"),
    key: "actions",
    fixed: "right",
    align: "center",
  },
]);

// 格式化 meta 显示
const formatMeta = (meta: any) => {
  if (!meta) return "-";
  return Object.entries(meta)
    .map(([key, value]) => `${key}: ${value}`)
    .join(", ");
};

// 格式化 permission 显示
const formatPermission = (permission: any) => {
  if (!permission) return "-";
  return Object.keys(permission).join(", ");
};

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

    // 初始化 metaItems
    if (currentItem.meta) {
      try {
        metaItems.value = Object.keys(currentItem.meta).map((key) => ({
          key,
          value: currentItem.meta[key],
        }));
      } catch (e) {
        console.error("Failed to parse meta:", e);
        metaItems.value = [];
      }
    } else {
      metaItems.value = [];
    }

    // 初始化 permissionItems 和 otherPermissionItems
    if (currentItem.permission) {
      try {
        permissionItems.value = Object.keys(currentItem.permission).filter(
          (p) => ["add", "edit", "delete", "view"].includes(p)
        );
        otherPermissionItems.value = Object.keys(currentItem.permission)
          .filter((p) => !["add", "edit", "delete", "view"].includes(p))
          .map((p) => ({ value: p }));
      } catch (e) {
        console.error("Failed to parse permission:", e);
        permissionItems.value = [];
        otherPermissionItems.value = [];
      }
    } else {
      permissionItems.value = [];
      otherPermissionItems.value = [];
    }
  }
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    rule_type: "menu",
    parent_id: 0,
    name: "",
    path: "",
    component: "",
    redirect: "",
    meta: { title: "", icon: "" }, // 默认添加 title 和 icon
    permission: null,
    menu_display_type: "ajax",
    model_name: "",
    weigh: 0,
    status: "normal",
  });
  metaItems.value = [
    { key: "title", value: "" },
    { key: "icon", value: "" },
    { key: "menuVisibleWithForbidden", value: "false" },
  ]; // 默认添加 title 和 icon
  permissionItems.value = [];
  otherPermissionItems.value = [];
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const onSubmit = async () => {
  confirmLoading.value = true;
  try {
    // 将 metaItems 转换为字典对象
    const meta = metaItems.value.reduce((acc, item) => {
      if (item.key && item.value) {
        acc[item.key] = item.value;
      }
      return acc;
    }, {} as Record<string, string>);
    currentItem.meta = meta;

    // 将 permissionItems 和 otherPermissionItems 合并为字典对象
    const permission = [
      ...permissionItems.value,
      ...otherPermissionItems.value.map((item) => item.value),
    ].reduce((acc, p) => {
      acc[p] = true; // 或者根据需要设置其他值
      return acc;
    }, {} as Record<string, boolean>);
    currentItem.permission = permission;

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
    await saveAdminRule({
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
      weigh: currentItem.weigh,
      status: currentItem.status,
    });
    message.success($t("common.save_success"));
  } catch (error) {
    console.error($t("common.save_item_failed"), error);
  }
};

const updateItem = async () => {
  try {
    await saveAdminRule({
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
      weigh: currentItem.weigh,
      status: currentItem.status,
    });
    message.success($t("common.update_success"));
  } catch (error) {
    console.error($t("common.update_item_failed"), error);
  }
};

const deleteItem = async (id: number) => {
  try {
    await deleteAdminRule(id);
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
      await deleteAdminRule(numericId);
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
function addPrefixForTree(treeData: any[], level = 0) {
  return treeData.map((node, index) => {
    const isLast = index === treeData.length - 1;
    let prefix = "";
    if (level > 0) {
      const space = "&nbsp;&nbsp;&nbsp;&nbsp;".repeat(level - 1);
      prefix = space + (isLast ? "└ " : "├ ");
    }
    // 给 name 加上前缀
    node.name = prefix + node.name;
    // 如果有 children，则递归处理
    if (node.children && node.children.length > 0) {
      node.children = addPrefixForTree(node.children, level + 1);
    }
    return node;
  });
}

// 然后直接在 fetchItems 中：

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchAdminRuleItems({
      page: pagination.value.current,
      perPage: pagination.value.pageSize,
      search: search.value,
    });
    // items.value = response.items;
    items.value = addPrefixForTree(response.items);
    pagination.value.total = response.total;
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  } finally {
    loading.value = false;
  }
};

const metaItems = ref<{ key: string; value: string }[]>([]);
const addMetaItem = () => {
  metaItems.value.push({ key: "", value: "" });
};
const removeMetaItem = (index: number) => {
  metaItems.value.splice(index, 1);
};

const permissionItems = ref<string[]>([]);
const otherPermissionItems = ref<{ value: string }[]>([]);
const addOtherPermissionItem = () => {
  otherPermissionItems.value.push({ value: "" });
};
const removeOtherPermissionItem = (index: number) => {
  otherPermissionItems.value.splice(index, 1);
};

onMounted(() => {
  fetchItems();
});
</script>

<style scoped>
.meta-item,
.permission-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.meta-item .ant-input,
.permission-item .ant-input {
  margin-right: 8px;
}
</style>
