<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['plugin.add', 'all']" type="code">
                <a-button
                  type="primary"
                  success
                  @click="openDialog(currentItem, 'add')"
                >
                  <template #icon>
                    <FileAddOutlined />
                  </template>
                  {{ $t("plugin_store.common.add_item") }}
                </a-button>
              </AccessControl>
              <a-input-search
                v-model:value="search"
                :placeholder="$t('plugin_store.plugin.search')"
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
              <template v-if="column.key === 'enabled'">
                <a-switch
                  :checked="record.enabled === 1"
                  @change="(checked) => toggleEnable(record, checked)"
                  :disabled="record.installed === 0"
                />
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

                  <!-- Install/Uninstall Button -->
                  <AccessControl :codes="['plugin.install', 'all']" type="code">
                    <a-button
                      size="small"
                      type="primary"
                      :danger="record.installed"
                      @click="toggleInstall(record)"
                    >
                      {{
                        record.installed
                          ? $t("plugin_store.plugin.uninstall")
                          : $t("plugin_store.plugin.install")
                      }}
                    </a-button>
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
        <a-form-item :label="$t('plugin_store.plugin.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>
        <a-form-item
          :label="$t('plugin_store.plugin.title')"
          name="title"
          :rules="formRules.title"
        >
          <a-input
            v-model:value="currentItem.title"
            :disabled="mode === 'view'"
          />
        </a-form-item>
        <!-- Other form items here -->
      </a-form>
    </a-modal>

    <!-- Payment Dialog -->
    <a-modal
      v-model:open="isPaymentVisible"
      :title="$t('plugin_store.plugin.payment')"
      @cancel="closePaymentDialog"
      :confirm-loading="paymentLoading"
      @ok="handlePayment"
    >
      <p>{{ $t('plugin_store.plugin.price') }}: {{ currentItem.price }}</p>
      <a-radio-group v-model:value="paymentMethod">
        <a-radio value="alipay">{{ $t('plugin_store.plugin.alipay') }}</a-radio>
        <a-radio value="wechat">{{ $t('plugin_store.plugin.wechat') }}</a-radio>
      </a-radio-group>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef } from "vue";
import { AccessControl } from "@/_core/access";
import {
  fetchPluginStore,
  installPlugin,
  uninstallPlugin,
  enablePlugin,
  purchasePlugin,
} from "@/api/core/plugin_store";
import { $t } from "@/locales";
import { FileAddOutlined, EyeOutlined } from "@ant-design/icons-vue";
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
  title: "",
  author: "",
  uuid: "",
  description: "",
  version: "",
  downloads: 0,
  download_url: "",
  md5_hash: "",
  price: 0.0,
  paid: 0,
  installed: 0,
  enabled: 0,
  setting_menu: "",
  created_at: moment().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
  updated_at: moment().tz(TIME_ZONE).format("YYYY-MM-DD HH:mm:ss"),
  status: "normal",
});

const isDialogVisible = ref(false);
const isPaymentVisible = ref(false);
const confirmLoading = ref(false);
const paymentLoading = ref(false);
const paymentMethod = ref("alipay");

const dialogTitle = computed(() => {
  switch (mode.value) {
    case "view":
      return $t("plugin_store.plugin.view_item");
    case "add":
      return $t("plugin_store.plugin.add_item");
    case "edit":
      return $t("plugin_store.plugin.edit_item");
    default:
      return "";
  }
});

const mode = ref<"add" | "edit" | "view">("add");

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

const columns = computed(() => [
  { title: $t("plugin_store.plugin.id"), dataIndex: "id", key: "id" },
  { title: $t("plugin_store.plugin.title"), dataIndex: "title", key: "title" },
  { title: $t("plugin_store.plugin.author"), dataIndex: "author", key: "author" },
  { title: $t("plugin_store.plugin.uuid"), dataIndex: "uuid", key: "uuid" },
  {
    title: $t("plugin_store.plugin.description"),
    dataIndex: "description",
    key: "description",
  },
  { title: $t("plugin_store.plugin.version"), dataIndex: "version", key: "version" },
  { title: $t("plugin_store.plugin.downloads"), dataIndex: "downloads", key: "downloads" },
  {
    title: $t("plugin_store.plugin.download_url"),
    dataIndex: "download_url",
    key: "download_url",
  },
  { title: $t("plugin_store.plugin.md5_hash"), dataIndex: "md5_hash", key: "md5_hash" },
  { title: $t("plugin_store.plugin.price"), dataIndex: "price", key: "price" },
  { title: $t("plugin_store.plugin.paid"), dataIndex: "paid", key: "paid" },
  {
    title: $t("plugin_store.plugin.installed"),
    dataIndex: "installed",
    key: "installed",
    customRender: ({ text }: { text: number }) =>
      text === 1
        ? $t("plugin_store.plugin.installed")
        : $t("plugin_store.plugin.not_installed"),
  },
  {
    title: $t("plugin_store.plugin.enabled"),
    dataIndex: "enabled",
    key: "enabled",
    customRender: ({ text }: { text: number }) =>
      text === 1
        ? $t("plugin_store.plugin.enabled")
        : $t("plugin_store.plugin.disabled"),
  },
  {
    title: $t("plugin_store.plugin.setting_menu"),
    dataIndex: "setting_menu",
    key: "setting_menu",
  },
  {
    title: $t("plugin_store.plugin.created_at"),
    dataIndex: "created_at",
    key: "created_at",
  },
  {
    title: $t("plugin_store.plugin.updated_at"),
    dataIndex: "updated_at",
    key: "updated_at",
  },
  { title: $t("plugin_store.plugin.status"), dataIndex: "status", key: "status" },
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
  }
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    title: "",
    author: "",
    uuid: "",
    description: "",
    version: "",
    downloads: 0,
    download_url: "",
    md5_hash: "",
    price: 0.0,
    paid: 0,
    installed: 0,
    enabled: 0,
    setting_menu: "",
    created_at: null,
    updated_at: null,
    status: "normal",
  });
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const closePaymentDialog = () => {
  isPaymentVisible.value = false;
};

const handlePayment = async () => {
  paymentLoading.value = true;
  try {
    await purchasePlugin(currentItem.id);
    message.success($t("plugin_store.plugin.payment_success"));
    closePaymentDialog();
    fetchItems();
  } catch (error) {
    console.error($t("plugin_store.plugin.payment_failed"), error);
  } finally {
    paymentLoading.value = false;
  }
};

const onSubmit = async () => {
  confirmLoading.value = true;
  try {
    await form.value?.validate();
    if (mode.value === "add") {
      await saveItem();
      resetCurrentItem();
    } else if (mode.value === "edit") {
      await updateItem();
    }
    closeDialog();
  } catch (error) {
    console.error($t("plugin_store.plugin.form_validation_failed"), error);
  } finally {
    confirmLoading.value = false;
    fetchItems();
  }
};

const saveItem = async () => {
  try {
    await installPlugin(currentItem);
    message.success($t("plugin_store.plugin.save_success"));
  } catch (error) {
    console.error($t("plugin_store.plugin.save_item_failed"), error);
  }
};

const updateItem = async () => {
  try {
    await installPlugin(currentItem);
    message.success($t("plugin_store.plugin.update_success"));
  } catch (error) {
    console.error($t("plugin_store.plugin.update_item_failed"), error);
  }
};

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchPluginStore({
      page: pagination.value.current,
      perPage: pagination.value.pageSize,
      search: search.value,
    });
    items.value = response.items;
    pagination.value.total = response.total;
  } catch (error) {
    console.error($t("plugin_store.plugin.fetch_items_error"), error);
  } finally {
    loading.value = false;
  }
};

const toggleEnable = async (record: Plugin, checked: boolean) => {
  try {
    const newStatus = checked ? 1 : 0;
    await enablePlugin(record.id, newStatus);
    record.enabled = newStatus; // 更新本地状态
    message.success(
      $t(
        checked
          ? "plugin_store.plugin.enabled"
          : "plugin_store.plugin.disabled"
      )
    );
    fetchItems();
  } catch (error) {
    console.error($t("plugin_store.plugin.toggle_enable_failed"), error);
  }
};

const toggleInstall = async (record: Plugin) => {
  try {
    if (record.installed === 1) {
      await uninstallPlugin(record.id);
      message.success($t("plugin_store.plugin.uninstall_success"));
    } else {
      if (record.paid === 0) {
        isPaymentVisible.value = true;
        currentItem.id = record.id;
        currentItem.price = record.price;
      } else {
        await installPlugin(record);
        message.success($t("plugin_store.plugin.install_success"));
      }
    }
    fetchItems();
  } catch (error) {
    console.error($t("plugin_store.plugin.toggle_install_failed"), error);
  }
};

onMounted(() => {
  fetchItems();
});
</script>