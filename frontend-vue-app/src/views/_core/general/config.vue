<template>
  <div>
    <!-- Main Layout -->
    <a-row justify="center">
      <a-col :span="24">
        <!-- Add Button -->

        <div class="mt-6">
          <!-- Generated Code Card -->
          <a-card v-if="showGeneratedCode">
            <a-card-header class="flex items-center justify-between mb-6">
              <a-button type="primary" @click="openAddDialog">
                <template #icon>
                  <FileAddOutlined />
                </template>
                {{ $t("general.config.add") }}
              </a-button>
            </a-card-header>
            <a-divider />
            <!-- Configuration Group Tabs -->
            <a-tabs v-model:value="activeTab" tab-position="left">
              <a-tab-pane
                v-for="group in CONFIG_GROUPS"
                :key="group"
                :tab="$t('general.config.' + group)"
              >
                <!-- Group Content -->
                <a-row
                  v-for="item in groupedItems[group]"
                  :key="item.id"
                  class="mb-4"
                >
                  <a-col :span="24">
                    <a-space wrap>
                      <label class="form-label">
                        {{ $t("general.config." + formatText(item.title)) }} (
                        configs.{{ group }}.{{ item.name }}
                        )
                      </label>
                      <a-button
                        type="link"
                        size="small"
                        shape="circle"
                        :icon="h(CopyOutlined)"
                        @click="
                          copyToClipboard(
                            `configs.${group}.${item.name}`,
                            item.id
                          )
                        "
                      >
                        <span :class="{ 'text-success': copied[item.id] }">
                          {{
                            copied[item.id]
                              ? $t("general.config.copy_success")
                              : ""
                          }}
                        </span>
                      </a-button>
                      <a-popconfirm
                        :title="
                          $t('general.config.are_you_sure_delete_this_one')
                        "
                        :ok-text="$t('common.yes')"
                        :cancel-text="$t('common.no')"
                        @confirm="confirmDelete(item)"
                      >
                        <a-button
                          type="link"
                          size="small"
                          danger
                          :icon="h(DeleteOutlined)"
                        />
                      </a-popconfirm>
                    </a-space>
                  </a-col>

                  <!-- Key-Value Form for JSON Arrays -->
                  <a-col v-if="isKeyValueForm(item)" :span="24">
                    <div
                      v-for="(row, index) in keyValueData[item.id]"
                      :key="index"
                      class="p-2"
                    >
                      <a-space wrap>
                        <a-input
                          v-model:value="row.key"
                          :placeholder="`${$t('general.config.key')} #${
                            index + 1
                          }`"
                        />
                        <a-input
                          v-model:value="row.value"
                          :placeholder="`${$t('general.config.value')} #${
                            index + 1
                          }`"
                        />
                        <a-popconfirm
                          :title="
                            $t('general.config.are_you_sure_delete_this_one')
                          "
                          :ok-text="$t('common.yes')"
                          :cancel-text="$t('common.no')"
                          @confirm="deleteKeyValueRow(item.id, index)"
                        >
                          <a-button
                            type="link"
                            size="small"
                            danger
                            :icon="h(DeleteOutlined)"
                          />
                        </a-popconfirm>
                        <a-button
                          type="link"
                          :icon="h(DragOutlined)"
                          size="small"
                          @mousedown="onDragStart(index)"
                        />
                      </a-space>
                    </div>
                    <a-space wrap class="mt-4">
                      <a-button type="primary" @click="addKeyValueRow(item.id)">
                        <a-icon type="plus" /> {{ $t("general.config.add") }}
                      </a-button>
                    </a-space>
                  </a-col>

                  <!-- Regular Input Fields Based on Type -->
                  <a-col v-else :span="12" class="p-2">
                    <template v-if="item.type === 'text'">
                      <a-textarea
                        v-model:value="item.value"
                        :placeholder="item.title"
                        rows="4"
                      />
                    </template>
                    <template v-else-if="item.type === 'select'">
                      <a-select
                        v-model:value="item.value"
                        :placeholder="$t(item.title)"
                      >
                        <a-select-option
                          v-for="(option, index) in parseContent(item.content)"
                          :key="index"
                          :value="option"
                        >
                          {{ option }}
                        </a-select-option>
                      </a-select>
                    </template>
                    <template v-else>
                      <a-input
                        v-model:value="item.value"
                        :placeholder="item.title"
                      />
                    </template>
                  </a-col>
                </a-row>
              </a-tab-pane>
            </a-tabs>

            <!-- Save Button -->
            <a-card-actions>
              <a-flex justify="center" align="center">
                <div class="mt-6">
                  <a-button
                    :loading="loading"
                    type="primary"
                    block
                    @click="submitForm"
                  >
                    {{ $t("general.config.save") }}
                  </a-button>
                </div>
              </a-flex>
            </a-card-actions>
          </a-card>
        </div>
      </a-col>
    </a-row>
    <!-- Add Configuration Dialog -->
    <a-modal
      v-model:visible="showAddDialog"
      :title="$t('general.config.add_configuration')"
      @cancel="closeDialog"
      @ok="handleFormSubmit"
    >
      <a-form :model="form" ref="formRef" layout="vertical">
        <a-form-item
          :label="$t('general.config.configuration_group')"
          name="group"
        >
          <a-select v-model="form.group">
            <a-select-option
              v-for="option in groupOptions"
              :key="option.value"
              :value="option.value"
            >
              {{ option.text }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-row gutter="16">
          <a-col span="12">
            <a-form-item
              :label="$t('general.config.variable_name')"
              name="name"
            >
              <a-input v-model="form.name" />
            </a-form-item>
          </a-col>
          <a-col span="12">
            <a-form-item
              :label="$t('general.config.variable_title')"
              name="title"
            >
              <a-input v-model="form.title" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row gutter="16">
          <a-col span="12">
            <a-form-item
              :label="$t('general.config.variable_description')"
              name="tip"
            >
              <a-input v-model="form.tip" />
            </a-form-item>
          </a-col>
          <a-col span="12">
            <a-form-item :label="$t('general.config.type')" name="type">
              <a-select v-model="form.type" @change="handleTypeChange">
                <a-select-option
                  v-for="option in typeOptions"
                  :key="option.value"
                  :value="option.value"
                >
                  {{ option.text }}
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item
          :label="$t('general.config.visibility_condition')"
          name="visible"
        >
          <a-input v-model="form.visible" />
        </a-form-item>
        <a-form-item :label="$t('general.config.variable_value')" name="value">
          <a-textarea v-model="form.value" rows="3" />
        </a-form-item>
        <a-form-item
          v-if="showSelectPage"
          :label="$t('general.config.related_table')"
          name="selectPageTable"
        >
          <a-select v-model="form.selectPageTable">
            <a-select-option
              v-for="table in selectPageTables"
              :key="table.value"
              :value="table.value"
            >
              {{ table.text }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <div v-if="form.type === 'array'">
          <a-button type="dashed" icon="plus" @click="addArrayOption">
            {{ $t("general.config.add") }}
          </a-button>
          <a-list bordered>
            <a-list-item
              v-for="(option, index) in form.arrayOptions"
              :key="index"
            >
              <a-row gutter="16">
                <a-col span="10">
                  <a-input
                    v-model="option.key"
                    :placeholder="$t('general.config.array_key')"
                  />
                </a-col>
                <a-col span="10">
                  <a-input
                    v-model="option.value"
                    :placeholder="$t('general.config.array_value')"
                  />
                </a-col>
                <a-col span="4" class="flex justify-center items-center">
                  <a-button
                    type="link"
                    icon="delete"
                    @click="removeArrayOption(index)"
                  />
                </a-col>
              </a-row>
            </a-list-item>
          </a-list>
        </div>
        <a-form-item :label="$t('general.config.data')" name="content">
          <a-textarea v-model="form.content" rows="3" />
        </a-form-item>
        <a-form-item :label="$t('general.config.validation_rules')" name="rule">
          <a-select
            mode="multiple"
            v-model="form.rule"
            :placeholder="$t('general.config.select_validation_rules')"
            class="w-full"
          >
            <a-select-option
              v-for="rule in validationRules"
              :key="rule.value"
              :value="rule.value"
            >
              {{ rule.label }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item
          :label="$t('general.config.extended_properties')"
          name="extend"
        >
          <a-input v-model="form.extend" />
        </a-form-item>
        <a-form-item :label="$t('general.config.settings')" name="setting">
          <a-input v-model="form.setting" />
        </a-form-item>
        <a-alert
          v-if="formErrors.length"
          type="error"
          :message="$t('general.config.form_errors')"
          :description="$t('general.config.check_the_errors')"
          show-icon
        />
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h, reactive, type CSSProperties } from "vue";
import {
  createGeneralConfig,
  deleteGeneralConfig,
  fetchGeneralConfig,
  saveGeneralConfig,
} from "@/api/admin/general";
import {
  FileAddOutlined,
  DeleteOutlined,
  DragOutlined,
  CopyOutlined,
} from "@ant-design/icons-vue";

import moment from "moment-timezone";
import { message } from "ant-design-vue";
import { $t } from "@/locales";

// Component props and events
const props = defineProps({ modelValue: Boolean });
const emit = defineEmits(["update:modelValue", "formSubmitted"]);

// Reactive data
const showSuccess = ref(false);
const showError = ref(false);
const errorMessages = ref<string[]>([]);
const loading = ref(false);
const showAddDialog = ref(false);
const showGeneratedCode = ref(true);
const activeTab = ref("basic");
const CONFIG_GROUPS = ["basic", "dictionary", "email", "user"];
const items = ref<any[]>([]);
const copied = ref<Record<number, boolean>>({});
const selectPageTables = ref<Array<{ text: string; value: string }>>([
  { text: $t("config.table_1"), value: "table1" },
  { text: $t("config.table_2"), value: "table2" },
]);
const keyValueData = ref<Record<number, { key: string; value: string }[]>>({});
const formErrors = ref<string[]>([]);

function formatText(text: string): string {
  return text.toLowerCase().replace(/\s+/g, "_");
}

// Form model
const form = reactive({
  group: "basic",
  name: "",
  title: "",
  tip: "",
  type: "string",
  visible: "",
  value: "",
  selectPageTable: "",
  arrayOptions: [] as Array<{ key: string; value: string }>,
  content: "",
  rule: [] as string[],
  extend: "",
  setting: "",
});

const groupOptions = [
  { text: $t("config.basic"), value: "basic" },
  { text: $t("config.dictionary"), value: "dictionary" },
  { text: $t("config.email"), value: "email" },
  { text: $t("config.user"), value: "user" },
];

const typeOptions = [
  { text: $t("config.string"), value: "string" },
  { text: $t("config.password"), value: "password" },
  { text: $t("config.text"), value: "text" },
  { text: $t("config.editor"), value: "editor" },
  { text: $t("config.number"), value: "number" },
  { text: $t("config.date"), value: "date" },
  { text: $t("config.time"), value: "time" },
  { text: $t("config.datetime"), value: "datetime" },
  { text: $t("config.datetime_range"), value: "datetime_range" },
  { text: $t("config.dropdown_list"), value: "select" },
  { text: $t("config.dropdown_list_multiple"), value: "selects" },
  { text: $t("config.image"), value: "image" },
  { text: $t("config.images_multiple"), value: "images" },
  { text: $t("config.file"), value: "file" },
  { text: $t("config.files_multiple"), value: "files" },
  { text: $t("config.switch"), value: "switch" },
  { text: $t("config.checkbox"), value: "checkbox" },
  { text: $t("config.radio_button"), value: "radio" },
  { text: $t("config.related_table"), value: "selectpage" },
  { text: $t("config.related_table_multiple_select"), value: "selectpages" },
  { text: $t("config.array"), value: "array" },
  { text: $t("config.custom"), value: "custom" },
];

const validationRules = [
  { label: $t("config.required"), value: "required" },
  { label: $t("config.digits"), value: "digits" },
  { label: $t("config.letters"), value: "letters" },
  { label: $t("config.date"), value: "date" },
  { label: $t("config.time"), value: "time" },
  { label: $t("config.email"), value: "email" },
  { label: $t("config.url"), value: "url" },
  { label: $t("config.qq"), value: "qq" },
  { label: $t("config.id_card"), value: "IDcard" },
  { label: $t("config.tel"), value: "tel" },
  { label: $t("config.mobile"), value: "mobile" },
  { label: $t("config.zipcode"), value: "zipcode" },
  { label: $t("config.chinese"), value: "chinese" },
  { label: $t("config.username"), value: "username" },
  { label: $t("config.password"), value: "password" },
];

const showSelectPage = computed(
  () => form.type === "selectpage" || form.type === "selectpages"
);

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit("update:modelValue", val),
});

const groupedItems = computed(() => {
  return CONFIG_GROUPS.reduce((acc, group) => {
    acc[group] = items.value.filter((item) => item.group === group);
    return acc;
  }, {} as Record<string, any[]>);
});

// Parsing item values into key-value pairs
function parseItemValueToKeyValue(item: any) {
  let parsed: any = {};
  try {
    parsed = JSON.parse(item.value);
  } catch {
    parsed = {};
  }
  const kvArray = Object.keys(parsed).map((k) => ({
    key: k,
    value: parsed[k],
  }));
  keyValueData.value[item.id] = kvArray;
}

// Fetch configuration items
async function fetchItems() {
  try {
    const res = await fetchGeneralConfig();
    console.log($t("config.config_request_return"), res);
    items.value = res.items;
    items.value.forEach((item) => {
      if (isKeyValueForm(item)) {
        parseItemValueToKeyValue(item);
      }
    });
  } catch (error) {
    handleError(error);
  }
}

// Handle form submission
async function handleFormSubmit() {
  try {
    const payload = {
      group: form.group,
      name: form.name,
      title: form.title,
      tip: form.tip,
      type: form.type,
      visible: form.visible,
      value: form.value,
      selectPageTable: form.selectPageTable,
      arrayOptions: form.arrayOptions, // Array of { key, value }
      content: form.content,
      rule: form.rule.join(","),
      extend: form.extend,
      setting: form.setting,
      created_at: moment().tz("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss"),
      updated_at: moment().tz("Asia/Shanghai").format("YYYY-MM-DD HH:mm:ss"),
    };
    console.log($t("config.submit_form_data"), payload);
    await createGeneralConfig(payload);
    emit("formSubmitted");
    message.success($t("config.save_successful"));
  } catch (error: any) {
    console.error($t("config.error_on_submit"), error);
    handleError(error);
  } finally {
    fetchItems();
    closeDialog();
  }
}

// Copy text to clipboard
function copyToClipboard(text: string, id: number) {
  navigator.clipboard
    .writeText(text)
    .then(() => {
      copied.value[id] = true;
      setTimeout(() => {
        copied.value[id] = false;
      }, 1000);
    })
    .catch(() => {});
}

// Parse content
function parseContent(content: string) {
  try {
    return JSON.parse(content);
  } catch {
    return [];
  }
}

const addArrayOption = () => {
  form.arrayOptions.push({ key: "", value: "" });
};

const removeArrayOption = (index: number) => {
  form.arrayOptions.splice(index, 1);
};

// Confirm deletion operation
async function confirmDelete(item: any) {
  try {
    await deleteGeneralConfig(item.id);
    await fetchItems();
    showSuccess.value = true;
  } catch (error) {
    handleError(error);
  }
}

// Add key-value pair row
function addKeyValueRow(id: number) {
  if (!keyValueData.value[id]) {
    keyValueData.value[id] = [];
  }
  keyValueData.value[id].push({ key: "", value: "" });
}

// Open add configuration dialog
function openAddDialog() {
  showAddDialog.value = true;
}

// Delete specified key-value row
function deleteKeyValueRow(itemId: number, index: number) {
  if (keyValueData.value[itemId]) {
    keyValueData.value[itemId].splice(index, 1);
  }
}

let dragIndex = ref<number | null>(null);
// Handle drag event
function onDragStart(index: number) {
  dragIndex.value = index;
}

// Handle type change
async function handleTypeChange(newType: string) {
  if (newType === "selectpage" || newType === "selectpages") {
    // Fetch selectPageTables based on type
  }
}

// Close dialog
function closeDialog() {
  dialog.value = false;
}

// Error handling
function handleError(error: any) {
  errorMessages.value = error.message
    ? [error.message]
    : [$t("config.unknown_error_occurred")];
  showError.value = true;
}

/** Submit save */
async function submitForm() {
  loading.value = true;
  // Build payload
  const payload: Record<string, string> = {};
  items.value.forEach((item) => {
    // If it's a JSON parsable item
    if (isKeyValueForm(item)) {
      const arrayData = keyValueData.value[item.id] || [];
      arrayData.forEach((kv, idx) => {
        payload[`row[${item.name}][${idx}][key]`] = kv.key;
        payload[`row[${item.name}][${idx}][value]`] = kv.value;
      });
    } else {
      // Otherwise, it's plain text
      payload[`row[${item.name}]`] = item.value;
    }
  });

  try {
    await saveGeneralConfig(payload);
    loading.value = false;
  } catch (error: any) {
    console.error($t("config.error_on_submit"), error);
    handleError(error);
  }
}

// Fetch configuration items on component mount
onMounted(() => {
  fetchItems();
});

// Check if the form uses key-value pairs
function isKeyValueForm(item: any) {
  if (item.type === "array") return true;
  try {
    const parsed = JSON.parse(item.value);
    return typeof parsed === "object" && parsed !== null;
  } catch {
    return false;
  }
}

const boxStyle: CSSProperties = {
  width: "100%",
  height: "120px",
  borderRadius: "6px",
  border: "1px solid #40a9ff",
};
</script>
