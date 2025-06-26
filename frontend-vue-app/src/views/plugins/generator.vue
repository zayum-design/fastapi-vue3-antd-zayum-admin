<template>
  <a-card :title="$t('generator.code_generator')">
    <!-- 选择数据表标题 -->
    <a-row class="mb-4">
      <a-col :span="24">
        <h4 class="text-left">{{ $t("generator.select_database_table") }}</h4>
      </a-col>
    </a-row>

    <a-row class="mb-4">
      <a-col :span="18">
        <!-- 选择数据表 -->
        <a-select
          v-model:value="selectedTable"
          :options="tables"
          :placeholder="$t('generator.select_a_table')"
          class="w-full"
          @change="handleTableChange"
        />
      </a-col>
    </a-row>

    <!-- 选择字段标题 -->
    <a-row class="mb-4" v-if="generatedCode && generatedCode.field_info && generatedCode.field_info.length > 0">
      <a-col :span="4">
        <h4 class="text-left">{{ $t("generator.select_fields") }}</h4>
      </a-col>
    </a-row>

    <!-- 选择字段 -->
    <a-row class="mb-4" v-if="generatedCode && generatedCode.field_info && generatedCode.field_info.length > 0">
      <a-checkbox-group
        v-model:value="selectedFields"
        class="w-full"
        @change="handleFieldChange"
      >
        <a-col
          v-for="field in generatedCode.field_info"
          :key="field.name"
          :span="6"
          class="p-1"
        >
          <a-checkbox :value="field.name">
            {{ field.name }} ({{ field.type }})
          </a-checkbox>
        </a-col>
      </a-checkbox-group>
    </a-row>

    <!-- 权限操作标题 -->
    <a-row class="mb-4" v-if="generatedCode">
      <a-col :span="24">
        <h4 class="text-left">
          {{ $t("generator.select_operations_permissions") }}
        </h4>
      </a-col>
    </a-row>

    <!-- 增删改查权限 -->
    <a-row class="mb-4" v-if="generatedCode">
      <a-checkbox-group
        v-model:value="operationPermissions"
        class="w-full"
        @change="handlePermissionChange"
      >
        <a-col
          v-for="operation in ['create', 'read', 'update', 'delete']"
          :key="operation"
          :span="6"
          class="p-1"
        >
          <a-checkbox :value="operation">
            {{ $t(capitalize(operation)) }}
          </a-checkbox>
        </a-col>
      </a-checkbox-group>
    </a-row>

    <!-- 生成代码按钮 -->
    <a-row class="mb-4" v-if="generatedCode">
      <a-col :span="24">
        <a-space wrap>
          <a-button type="primary" @click="updateSelectedFields" :loading="loading">
            {{ $t("generator.generate_code") }}
          </a-button>
          <a-button type="primary" @click="downloadCode" :loading="loading">
            {{ $t("generator.code_download") }}
          </a-button>
        </a-space>
      </a-col>
    </a-row>

    <!-- 生成的代码标题 -->
    <a-row class="mb-4" v-if="showGeneratedCode">
      <a-col :span="24">
        <h4 class="text-left">{{ $t("generator.generated_code") }}</h4>
      </a-col>
    </a-row>

    <!-- 代码展示区域 -->
    <a-card v-if="showGeneratedCode">
      <a-tabs v-model:value="activeTabKey" class="mb-4" type="card">
        <a-tab-pane key="modelCode" :tab="$t('generator.model_code')">
          <CodeBlock :code="modelCode" language="python" height="500px" />
        </a-tab-pane>
        <a-tab-pane key="crudCode" :tab="$t('generator.crud_code')">
          <CodeBlock :code="crudCode" language="python" height="500px" />
        </a-tab-pane>
        <a-tab-pane key="schemasCode" :tab="$t('generator.schemas_code')">
          <CodeBlock :code="schemasCode" language="python" height="500px" />
        </a-tab-pane>
        <a-tab-pane key="apiCode" :tab="$t('generator.api_code')">
          <CodeBlock :code="apiCode" language="python" height="500px" />
        </a-tab-pane>
        <a-tab-pane key="vueCode" :tab="$t('generator.vue_code')">
          <CodeBlock :code="vueCode" language="vue" height="500px" />
        </a-tab-pane>
        <a-tab-pane key="vueI18nJsonCode" :tab="$t('generator.vue_i18n_json')">
          <CodeBlock :code="vueI18nJsonCode" language="json" height="500px" />
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { requestClient } from "@/api/request";
import CodeBlock from "@/_core/ui/components/CodeBlock.vue";
import { $t } from "@/locales";
import JSZip from "jszip";
import { saveAs } from "file-saver";

// Define a type for field_info if not already defined elsewhere
interface FieldInfo {
  name: string;
  type: string;
  // Add other properties if they exist
}

interface GeneratedCodeResponse {
  model_code?: string;
  crud_code?: string;
  schemas_code?: string;
  api_code?: string;
  vue_code?: string;
  vue_i18n_json?: string;
  field_info?: FieldInfo[]; // Add this line
  // Add other properties from the response
}


// Responsive data
const tables = ref<{ label: string; value: string }[]>([]);
const selectedTable = ref<string | null>(null);
const selectedFields = ref<string[]>([]);
const operationPermissions = ref<string[]>(["create", "read", "update", "delete"]);
const generatedCode = ref<GeneratedCodeResponse | null>(null); // Use the interface
const loading = ref(false);
const activeTabKey = ref("modelCode");

// Auxiliary functions
const capitalize = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

// Computed properties
const modelCode = computed(() => generatedCode.value?.model_code || "");
const crudCode = computed(() => generatedCode.value?.crud_code || "");
const schemasCode = computed(() => generatedCode.value?.schemas_code || "");
const apiCode = computed(() => generatedCode.value?.api_code || "");
const vueCode = computed(() => generatedCode.value?.vue_code || "");
const vueI18nJsonCode = computed(() => generatedCode.value?.vue_i18n_json || "");
const showGeneratedCode = computed(() => !!generatedCode.value);

// Methods
const fetchTables = async () => {
  try {
    const response = await requestClient.get<string[]>(
      `${import.meta.env.VITE_GLOB_URL}/plugins/generator/tables`
    );
    tables.value = response.map(table => ({ label: table, value: table }));
  } catch (error) {
    console.error("获取表名列表失败:", error);
  }
};

const updateSelectedFieldsAndCode = async (isInitialLoadForTable: boolean = false) => {
  if (!selectedTable.value) return;

  loading.value = true;
  try {
    const fieldsParam = (isInitialLoadForTable || selectedFields.value.length === 0)
      ? 'all'
      : selectedFields.value.join(",");

    const operationsParam = operationPermissions.value.length === 0
      ? "read,delete" // Default if none selected, adjust if needed
      : operationPermissions.value.join(",");

    const response = await requestClient.get<GeneratedCodeResponse>( // Use the interface
      `${import.meta.env.VITE_GLOB_URL}/plugins/generator/code/${selectedTable.value}`,
      {
        params: {
          fields: fieldsParam,
          operations: operationsParam,
        },
      }
    );

    generatedCode.value = response;

    // If it was an initial load and we got field_info, update selectedFields to reflect all
    if (isInitialLoadForTable && response?.field_info) {
      selectedFields.value = response.field_info.map(f => f.name);
    } else if (!response?.field_info && selectedFields.value.length > 0) {
      // If field_info is not returned (e.g., error or empty table), clear selectedFields
      selectedFields.value = [];
    }
    // If not initial load, selectedFields is already managed by user interaction

  } catch (error) {
    console.error("获取代码失败:", error);
    generatedCode.value = null; // Clear generated code on error
    selectedFields.value = []; // Clear selected fields on error
  } finally {
    loading.value = false;
  }
};


const downloadCode = async () => {
  if (!selectedTable.value) return;

  loading.value = true;
  try {
    // Ensure the latest code based on current selections is generated before zipping
    // Pass false, as this is not an "initial load for table" scenario,
    // but a regeneration based on current selectedFields.
    await updateSelectedFieldsAndCode(false);

    if (!generatedCode.value) {
        console.error("生成代码数据为空，无法下载。");
        // Optionally show a user message
        return;
    }
    
    const zip = new JSZip();
    const tableName = selectedTable.value; // selectedTable.value is guaranteed to be non-null here

    zip.file(`models/${tableName}.py`, modelCode.value);
    zip.file(`crud/${tableName}.py`, crudCode.value);
    zip.file(`schemas/${tableName}.py`, schemasCode.value);
    zip.file(`api/admin/${tableName.replace(/^sys_/, "")}.py`, apiCode.value);
    zip.file(`vue/${tableName}.vue`, vueCode.value);
    zip.file(`vue_i18n/${tableName}.json`, vueI18nJsonCode.value); // Consistent folder naming

    const content = await zip.generateAsync({ type: "blob" });
    saveAs(content, `${tableName}_code.zip`); // More descriptive zip name
  } catch (error) {
    console.error("下载代码失败:", error);
  } finally {
    loading.value = false;
  }
};

// Event handlers
const handleTableChange = async () => {
  if (selectedTable.value) {
    // Reset fields for the new table, so 'all' is fetched.
    selectedFields.value = [];
    // Fetch code for the new table, indicating it's an initial load for this table
    // This will populate generatedCode and also set selectedFields to all available fields.
    await updateSelectedFieldsAndCode(true);
  } else {
    // No table selected, clear everything
    generatedCode.value = null;
    selectedFields.value = [];
  }
};

const handleFieldChange = () => {
  // User manually changed field selection, re-fetch code based on new selection
  // Pass false, as it's not an initial load for the table.
  updateSelectedFieldsAndCode(false);
};

const handlePermissionChange = () => {
  // User changed permissions, re-fetch code
  // Pass false, as it's not an initial load for the table.
  updateSelectedFieldsAndCode(false);
};

// Renamed the original updateSelectedFields to avoid confusion for the button
const updateSelectedFields = () => {
    updateSelectedFieldsAndCode(false);
}


// Lifecycle
onMounted(() => {
  fetchTables();
});
</script>

<style scoped>
/* 自定义样式 */
.w-full {
  width: 100%;
}
.mb-4 {
  margin-bottom: 1rem;
}
.p-1 {
  padding: 0.25rem;
}
</style>