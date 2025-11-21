<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['admin.group.add', 'all']" type="code">
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
              <AccessControl :codes="['admin.group.delete', 'all']" type="code">
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
                    :codes="['admin.group.edit', 'all']"
                    type="code"
                  >
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined />
                    </a-button>
                  </AccessControl>
                  <AccessControl
                    :codes="['admin.group.delete', 'all']"
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
        <a-form-item :label="$t('admin.group.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item
          :label="$t('admin.group.pid')"
          name="pid"
          :rules="formRules.pid"
        >
          <a-select
            v-model:value="currentItem.pid"
            :disabled="mode === 'view'"
            placeholder="请选择父级分组"
          >
            <a-select-option :value="0">根分组</a-select-option>
            <a-select-option
              v-for="group in allGroups"
              :key="group.id"
              :value="group.id"
              :disabled="group.id === currentItem.id"
            >
              {{ group.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.group.name')"
          name="name"
          :rules="formRules.name"
        >
          <a-input
            v-model:value="currentItem.name"
            :disabled="mode === 'view'"
          />
        </a-form-item>
        <a-form-item
          :label="$t('admin.group.rules')"
          name="rules"
          :rules="formRules.rules"
        >
          <a-checkbox
            v-model:checked="isAllRulesSelected"
            @change="handleAllRulesChange"
            :disabled="mode === 'view'"
          >
            {{ $t("common.select_all") }}
          </a-checkbox>

          <a-tree
            :checkedKeys="treeCheckedKeys"
            checkable
            :tree-data="treeData"
            :disabled="mode === 'view'"
            @check="onTreeCheck"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.group.access')"
          name="access"
          :rules="formRules.access"
        >
          <a-select
            v-model:value="currentItem.access"
            mode="multiple"
            :disabled="mode === 'view'"
            placeholder="请选择权限"
          >
            <a-select-option
              v-for="permission in flattenedPermissions"
              :key="permission"
              :value="permission"
            >
              {{ permission }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item :label="$t('admin.group.created_at')" name="created_at">
          <a-date-picker
            v-model:value="currentItem.created_at"
            show-time
            :disabled="mode === 'view'"
            :format="dateTimeFormat"
            :value-format="dateTimeFormat"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.group.updated_at')" name="updated_at">
          <a-date-picker
            v-model:value="currentItem.updated_at"
            show-time
            :disabled="mode === 'view'"
            :format="dateTimeFormat"
            :value-format="dateTimeFormat"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.group.status')"
          :rules="formRules.status"
        >
          <a-select
            v-model:value="currentItem.status"
            :disabled="mode === 'view'"
          >
            <a-select-option value="normal">
              {{ $t("common.normal") }}
            </a-select-option>
            <a-select-option value="hidden">
              {{ $t("common.hidden") }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from "@/_core/access";
import {
  fetchAdminGroupItems,
  saveAdminGroup,
  deleteAdminGroup,
} from "@/api/admin/admin_group";
import { fetchAdminRuleItems } from "@/api/admin/admin_rule";

import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
} from "@ant-design/icons-vue";
import { message, type FormInstance, type TreeProps } from "ant-design-vue";
import moment, { type Moment } from "moment-timezone";

const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || "Asia/Shanghai";
const form = ref<FormInstance | null>(null);

// 日期时间格式常量
const dateTimeFormat = "YYYY-MM-DD HH:mm:ss";
const dateFormat = "YYYY-MM-DD";
const timeFormat = "HH:mm:ss";

interface AdminGroup {
  id: number;
  pid: number;
  name: string;
  rules: (number | string)[];
  access: string[];
  created_at: string;
  updated_at: string;
  status: string;
}

const currentItem = reactive<AdminGroup>({
  id: 0,
  pid: 0,
  name: "",
  rules: [],
  access: [],
  created_at: moment().tz(TIME_ZONE).format(dateTimeFormat),
  updated_at: moment().tz(TIME_ZONE).format(dateTimeFormat),
  status: "normal",
});

const isDialogVisible = ref(false);
const confirmLoading = ref(false);
const mode = ref<"add" | "edit" | "view">("add");

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

const items = ref<AdminGroupItem[]>([]);
const allGroups = ref<AdminGroupItem[]>([]); // 所有管理员组用于映射父级名称
const pagination = ref({ current: 1, pageSize: 10, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

const formRules = reactive({
  pid: [{ required: true, message: $t("admin_group.id.field_required") }],
  name: [
    { required: true, message: $t("admin_group.nickname.field_required") },
    { min: 2, message: $t("admin_group.nickname.min_length") },
    { max: 30, message: $t("admin_group.nickname.max_length") },
  ],
  rules: [{ required: true, message: $t("admin_group.rules.field_required") }],
  access: [
    { required: true, message: $t("admin_group.access.field_required") },
  ],
  status: [
    { required: true, message: $t("admin_group.status.field_required") },
  ],
  created_at: [
    { required: true, message: $t("admin_group.created_at.field_required") },
  ],
  updated_at: [
    { required: true, message: $t("admin_group.updated_at.field_required") },
  ],
});

const columns = computed(() => [
  { 
    title: $t("admin.group.id"), 
    dataIndex: "id", 
    key: "id",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("admin.group.pid"),
    dataIndex: "pid",
    key: "pid",
    customRender: ({ text }: { text: number }) => getParentName(text),
  },
  { 
    title: $t("admin.group.name"), 
    dataIndex: "name", 
    key: "name",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("admin.group.rules"),
    dataIndex: "rules",
    key: "rules",
    customRender: ({ text }: { text: (number | string)[] }) => text.join(", "),
  },
  {
    title: $t("admin.group.access"),
    dataIndex: "access",
    key: "access",
    customRender: ({ text }: { text: string[] }) => text.join(", "),
  },
  {
    title: $t("admin.group.created_at"),
    dataIndex: "created_at",
    key: "created_at",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("admin.group.updated_at"),
    dataIndex: "updated_at",
    key: "updated_at",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  { 
    title: $t("admin.group.status"), 
    dataIndex: "status", 
    key: "status",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
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

const orderby = ref('');

const onTableChange = (pag: any, filters: any, sorter: any) => {
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

const openDialog = async (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    // 处理日期时间，确保格式正确
    const formatDateTime = (dateString: string) => {
      if (!dateString) return moment().tz(TIME_ZONE).format(dateTimeFormat);
      const m = moment(dateString, dateTimeFormat);
      return m.isValid()
        ? m.tz(TIME_ZONE).format(dateTimeFormat)
        : moment().tz(TIME_ZONE).format(dateTimeFormat);
    };

    Object.assign(currentItem, {
      id: item.id,
      pid: item.pid,
      name: item.name,
      rules: item.rules || [],
      access: item.access || [],
      created_at: formatDateTime(item.created_at),
      updated_at: formatDateTime(item.updated_at),
      status: item.status || "normal",
    });

    if (Array.isArray(item.rules) && item.rules.includes("all")) {
      isAllRulesSelected.value = true;
      currentItem.rules = ["all"];
      currentItem.access = ["all"];
    } else {
      isAllRulesSelected.value = false;
    }
  }

  isDialogVisible.value = true;
  await fetchAllGroups(); // 确保获取所有管理员组数据
  await fetchAdminRule();
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    pid: 0,
    name: "",
    rules: [],
    access: [],
    created_at: moment().tz(TIME_ZONE).format(dateTimeFormat),
    updated_at: moment().tz(TIME_ZONE).format(dateTimeFormat),
    status: "normal",
  });
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const onSubmit = async () => {
  confirmLoading.value = true;
  try {
    await form.value?.validate();

    if (isAllRulesSelected.value) {
      currentItem.rules = ["all"];
      currentItem.access = ["all"];
    }

    if (mode.value === "add") {
      await saveItem();
    } else if (mode.value === "edit") {
      await updateItem();
    }
  } catch (error) {
    console.error($t("common.form_validation_failed"), error);
  } finally {
    confirmLoading.value = false;
    fetchItems();
  }
};

// 全选相关逻辑
const isAllRulesSelected = ref(false);

interface TreeNode {
  title: string;
  key: string | number;
  children?: TreeNode[];
  isLeaf?: boolean;
}

const treeData = ref<TreeNode[]>([]);
const flattenedPermissions = ref<string[]>([]);

const treeCheckedKeys = computed(() => {
  if (isAllRulesSelected.value) {
    return getAllTreeKeys(treeData.value);
  } else {
    return currentItem.rules;
  }
});

const handleAllRulesChange = (e: any) => {
  const checked = e.target.checked;
  isAllRulesSelected.value = checked;
  if (checked) {
    currentItem.access = ["all"];
  } else {
    currentItem.rules = [];
    currentItem.access = [];
  }
};

function getAllTreeKeys(nodes: TreeNode[] | undefined): (string | number)[] {
  if (!nodes) return [];
  const keys: (string | number)[] = [];
  nodes.forEach((node) => {
    keys.push(node.key);
    if (node.children) {
      keys.push(...getAllTreeKeys(node.children));
    }
  });
  return keys;
}

const onTreeCheck = (checkedKeys: any, { checkedNodes }: any) => {
  if (!isAllRulesSelected.value) {
    currentItem.rules = checkedKeys.filter(
      (key: any) => typeof key === "number"
    );
    currentItem.access = checkedNodes
      .filter((node: any) => node.isLeaf)
      .map((node: any) => node.key);
  }
};

const saveItem = async () => {
  try {
    await saveAdminGroup({
      pid: currentItem.pid,
      name: currentItem.name,
      rules: currentItem.rules,
      access: currentItem.access,
      created_at: currentItem.created_at,
      updated_at: currentItem.updated_at,
      status: currentItem.status,
    });
    closeDialog();
    message.success($t("common.save_success"));
    resetCurrentItem();
  } catch (error) {
    console.error($t("common.save_item_failed"), error);
  }
};

const updateItem = async () => {
  try {
    await saveAdminGroup({
      id: currentItem.id,
      pid: currentItem.pid,
      name: currentItem.name,
      rules: currentItem.rules,
      access: currentItem.access,
      created_at: currentItem.created_at,
      updated_at: currentItem.updated_at,
      status: currentItem.status,
    });
    closeDialog();
    message.success($t("common.update_success"));
  } catch (error) {
    console.error($t("common.update_item_failed"), error);
  }
};

const deleteItem = async (id: number) => {
  try {
    await deleteAdminGroup(id);
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
      await deleteAdminGroup(numericId);
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

// 获取所有管理员组用于映射父级名称
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

// 根据父级ID获取父级名称
const getParentName = (pid: number): string => {
  if (pid === 0) {
    return "根分组";
  }
  const parentGroup = allGroups.value.find((group) => group.id === pid);
  return parentGroup ? parentGroup.name : `未知分组(${pid})`;
};

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchAdminGroupItems({
      page: pagination.value.current,
      perPage: pagination.value.pageSize,
      search: search.value,
      orderby: orderby.value,
    });
    // 确保返回的 rules / access 都是数组
    items.value = response.items.map((item: any) => ({
      ...item,
      rules: item.rules || [],
      access: item.access || [],
    }));

    pagination.value.total = response.total;
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  } finally {
    loading.value = false;
  }
};

// ========================== 拉取菜单规则 (Tree) ==========================
interface TreeNode {
  title: string;
  key: string | number;
  children?: TreeNode[];
  isLeaf?: boolean;
}

const fetchAdminRule = async () => {
  loading.value = true;
  try {
    const response = await fetchAdminRuleItems({
      page: 1,
      perPage: -1,
      search: "",
    });
    treeData.value = transformItemsToTreeData(response.items) || [];
    flattenedPermissions.value = flattenPermissions(response.items);
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
    treeData.value = [];
  } finally {
    loading.value = false;
  }
};

const transformItemsToTreeData = (items: any[] = []): TreeNode[] => {
  return (items || []).map((item): TreeNode => {
    const children: TreeNode[] = item.children
      ? transformItemsToTreeData(item.children)
      : [];
    // 若有 permission，就把它们当作子节点
    if (item.permission && Object.keys(item.permission).length > 0) {
      const permissionChildren = Object.keys(item.permission).map((key) => ({
        title: key,
        key: `${item.name}.${key}`,
        isLeaf: true,
      }));
      children.push(...permissionChildren);
    }
    return {
      title: item.name,
      key: item.id,
      children: children.length > 0 ? children : undefined,
    };
  });
};

const flattenPermissions = (items: any[]): string[] => {
  const permissions: string[] = [];
  items.forEach((item) => {
    if (item.permission && Object.keys(item.permission).length > 0) {
      Object.keys(item.permission).forEach((key) => {
        permissions.push(`${item.name}.${key}`);
      });
    }
    if (item.children) {
      permissions.push(...flattenPermissions(item.children));
    }
  });
  return permissions;
};

onMounted(() => {
  fetchItems();
  fetchAllGroups(); // 获取所有管理员组用于映射父级名称
});
</script>
