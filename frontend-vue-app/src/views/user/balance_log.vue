<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <a-input-search v-model:value="search" :placeholder="$t('common.search')" @search="fetchItems"
                enter-button class="w-1/3" />
            </a-space>
          </a-card-header>

          <a-divider />

          <a-table :columns="columns" :dataSource="items" :loading="loading" :rowKey="rowKey" :pagination="pagination"
            @change="onTableChange" :scroll="{ x: true }">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'actions'">
                <a-space>
                  <a-button size="small" type="primary" @click="openDialog(record)">
                    <EyeOutlined />
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>

    <!-- View Dialog -->
    <a-modal v-model:open="isDialogVisible" :title="$t('common.view_item')" @cancel="closeDialog" :footer="null"
      :destroyOnClose="true" :maskClosable="false">
      <a-form :model="currentItem" :label-col="labelCol" :wrapper-col="wrapperCol">
        <a-form-item :label="$t('user.balance_log.field.id')">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.balance')">
          <a-input v-model:value="currentItem.balance" :disabled="true" />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.before')">
          <a-input v-model:value="currentItem.before" :disabled="true" />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.after')">
          <a-input v-model:value="currentItem.after" :disabled="true" />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.memo')">
          <a-input v-model:value="currentItem.memo" :disabled="true" />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.created_at')">
          <a-input v-model:value="currentItem.created_at" :disabled="true" />
        </a-form-item>

        <a-form-item :label="$t('user.balance_log.field.updated_at')">
          <a-input v-model:value="currentItem.updated_at" :disabled="true" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import {
  fetchUserBalanceLogItems,
} from "@/api/user/balance_log";
import { $t } from "@/locales";
import {
  EyeOutlined,
} from "@ant-design/icons-vue";

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
  created_at: "",
  updated_at: "",
});

const isDialogVisible = ref(false);

const loading = ref(false);
const rowKey = ref("id");
const items = ref([]);
const pagination = ref({ current: 1, pageSize: 10, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

const columns = computed(() => [
  {
    title: $t("user.balance_log.field.id"),
    dataIndex: "id",
    key: "id",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("user.balance_log.field.balance"),
    dataIndex: "balance",
    key: "balance",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("user.balance_log.field.before"),
    dataIndex: "before",
    key: "before",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("user.balance_log.field.after"),
    dataIndex: "after",
    key: "after",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("user.balance_log.field.memo"),
    dataIndex: "memo",
    key: "memo",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },
  {
    title: $t("user.balance_log.field.created_at"),
    dataIndex: "created_at",
    key: "created_at",
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

const openDialog = (item: any) => {
  Object.assign(currentItem, item);
  isDialogVisible.value = true;
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchUserBalanceLogItems({
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

onMounted(() => {
  fetchItems();
});
</script>
