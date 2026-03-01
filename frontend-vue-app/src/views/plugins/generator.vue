<template>
  <a-card :title="$t('generator.code_generator')">
    <a-tabs v-model:value="mainActiveTab" class="mb-4" type="card">
      <a-tab-pane key="codeGenerator" :tab="$t('generator.code_generator')">
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
      </a-tab-pane>
      
      <a-tab-pane key="tableCreator" :tab="$t('generator.table_creator')">
        <!-- 表创建功能 -->
        <a-row class="mb-4">
          <a-col :span="24">
            <h4 class="text-left">{{ $t('generator.table_creator') }}</h4>
          </a-col>
        </a-row>

        <!-- 表基本信息 -->
        <a-card class="mb-4">
          <a-row :gutter="16" class="mb-4">
            <a-col :span="12">
              <a-form-item :label="$t('generator.table_name')" required>
                <a-input v-model:value="tableName" :placeholder="$t('generator.table_name')" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item :label="$t('generator.database_type')">
                <a-select v-model:value="databaseType" :options="databaseTypes.map(db => ({ label: db.label, value: db.value }))" />
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item :label="$t('generator.table_comment')">
                <a-textarea v-model:value="tableComment" :placeholder="$t('generator.table_comment')" :rows="2" />
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>

        <!-- 字段管理 -->
        <a-card class="mb-4">
          <template #title>
            <div class="flex justify-between items-center">
              <span>{{ $t('generator.field_management') }}</span>
              <div>
                <a-button type="primary" @click="addField" class="mr-2">{{ $t('generator.add_field') }}</a-button>
                <a-button @click="addMultipleFields">{{ $t('generator.add_multiple_fields') }}</a-button>
              </div>
            </div>
          </template>

          <!-- 字段列表 -->
          <a-table :data-source="tableFields" :pagination="false" class="mb-4">
            <a-table-column :title="$t('generator.field_name')" width="150px">
              <template #default="{ record }">
                <a-input v-model:value="record.name" :placeholder="$t('generator.field_name')" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.field_type')" width="120px">
              <template #default="{ record }">
                <a-select v-model:value="record.type" :options="fieldTypes.map(type => ({ label: type, value: type }))" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.field_length')" width="100px">
              <template #default="{ record }">
                <a-input v-model:value="record.length" :placeholder="$t('generator.field_length')" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.nullable')" width="100px">
              <template #default="{ record }">
                <a-checkbox v-model:checked="record.nullable" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.primary_key')" width="80px">
              <template #default="{ record }">
                <a-checkbox v-model:checked="record.primaryKey" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.auto_increment')" width="80px">
              <template #default="{ record }">
                <a-checkbox v-model:checked="record.autoIncrement" :disabled="!record.primaryKey" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.default_value')" width="120px">
              <template #default="{ record }">
                <a-input v-model:value="record.defaultValue" :placeholder="$t('generator.default_value')" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.field_comment')" width="150px">
              <template #default="{ record }">
                <a-input v-model:value="record.comment" :placeholder="$t('generator.field_comment')" />
              </template>
            </a-table-column>
            <a-table-column :title="$t('generator.operations')" width="120px">
              <template #default="{ record, index }">
                <a-space>
                  <a-button type="link" size="small" @click="moveFieldUp(index)" :disabled="index === 0">{{ $t('generator.move_up') }}</a-button>
                  <a-button type="link" size="small" @click="moveFieldDown(index)" :disabled="index === tableFields.length - 1">{{ $t('generator.move_down') }}</a-button>
                  <a-button type="link" size="small" danger @click="removeField(record.id)">{{ $t('generator.delete') }}</a-button>
                </a-space>
              </template>
            </a-table-column>
          </a-table>
        </a-card>

        <!-- 操作按钮 -->
        <a-row class="mb-4">
          <a-col :span="24">
            <a-space wrap>
              <a-button type="primary" @click="generateSQL" :loading="sqlLoading">{{ $t('generator.generate_sql') }}</a-button>
              <a-button type="primary" @click="createTableRemote" :loading="createTableLoading">{{ $t('generator.create_table_remote') }}</a-button>
              <a-button @click="clearForm">{{ $t('generator.clear_form') }}</a-button>
            </a-space>
          </a-col>
        </a-row>

        <!-- 生成的SQL -->
        <a-card v-if="generatedSQL">
          <template #title>
            <div class="flex justify-between items-center">
              <span>{{ $t('generator.generated_sql') }}</span>
              <a-button type="primary" @click="copySQL">{{ $t('generator.copy_sql') }}</a-button>
            </div>
          </template>
          <CodeBlock :code="generatedSQL" language="sql" height="300px" />
        </a-card>
      </a-tab-pane>
    </a-tabs>
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

// Table creation types
interface TableField {
  id: number;
  name: string;
  type: string;
  length: string;
  nullable: boolean;
  primaryKey: boolean;
  autoIncrement: boolean;
  defaultValue: string;
  comment: string;
}

interface DatabaseType {
  label: string;
  value: string;
  fieldTypes: string[];
}


// Responsive data
const mainActiveTab = ref("codeGenerator");
const tables = ref<{ label: string; value: string }[]>([]);
const selectedTable = ref<string | null>(null);
const selectedFields = ref<string[]>([]);
const operationPermissions = ref<string[]>(["create", "read", "update", "delete"]);
const generatedCode = ref<GeneratedCodeResponse | null>(null); // Use the interface
const loading = ref(false);
const activeTabKey = ref("modelCode");

// Table creation data
const tableName = ref("");
const tableComment = ref("");
const databaseType = ref("mysql");
const tableFields = ref<TableField[]>([
  {
    id: 1,
    name: "id",
    type: "int",
    length: "11",
    nullable: false,
    primaryKey: true,
    autoIncrement: true,
    defaultValue: "",
    comment: "主键ID"
  }
]);
const nextFieldId = ref(2);
const generatedSQL = ref("");
const sqlLoading = ref(false);
const createTableLoading = ref(false);

// Database types
const databaseTypes = ref<DatabaseType[]>([
  {
    label: "MySQL",
    value: "mysql",
    fieldTypes: ["int", "varchar", "text", "datetime", "timestamp", "decimal", "float", "double", "boolean", "json"]
  },
  {
    label: "PostgreSQL",
    value: "postgresql",
    fieldTypes: ["integer", "varchar", "text", "timestamp", "numeric", "real", "double precision", "boolean", "json", "uuid"]
  },
  {
    label: "SQLite",
    value: "sqlite",
    fieldTypes: ["INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"]
  }
]);

// Field types based on selected database
const fieldTypes = computed(() => {
  const db = databaseTypes.value.find(db => db.value === databaseType.value);
  return db ? db.fieldTypes : [];
});

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
      `${import.meta.env.VITE_GLOB_API_URL}/plugins/generator/tables`
    );
    tables.value = response.map(table => ({ label: table, value: table }));
  } catch (error) {
    console.error("获取表名列表失败:==="+`${import.meta.env.VITE_GLOB_API_URL}/plugins/generator/tables`, error);
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
      `${import.meta.env.VITE_GLOB_API_URL}/plugins/generator/code/${selectedTable.value}`,
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
    
    // 根据 sys_admin_group 结构创建文件结构
    // 1. 创建服务目录
    const serviceDir = tableName;
    
    // 2. 创建子目录结构
    zip.file(`${serviceDir}/models/${tableName}.py`, modelCode.value);
    zip.file(`${serviceDir}/crud/${tableName}.py`, crudCode.value);
    zip.file(`${serviceDir}/schemas/${tableName}.py`, schemasCode.value);
    
    // 3. API 文件命名：移除 sys_ 前缀（如果存在）
    const apiFileName = tableName.replace(/^sys_/, "");
    zip.file(`${serviceDir}/api/${apiFileName}.py`, apiCode.value);
    
    // 4. Vue 相关文件
    zip.file(`vue/${tableName}.vue`, vueCode.value);
    zip.file(`vue_i18n/${tableName}.json`, vueI18nJsonCode.value);

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

// Table creation methods
const addField = () => {
  tableFields.value.push({
    id: nextFieldId.value,
    name: "",
    type: fieldTypes.value[0] || "varchar",
    length: "",
    nullable: true,
    primaryKey: false,
    autoIncrement: false,
    defaultValue: "",
    comment: ""
  });
  nextFieldId.value++;
};

const removeField = (id: number) => {
  const index = tableFields.value.findIndex(field => field.id === id);
  if (index !== -1) {
    tableFields.value.splice(index, 1);
  }
};

const moveFieldUp = (index: number) => {
  if (index > 0) {
    const field = tableFields.value[index];
    tableFields.value.splice(index, 1);
    tableFields.value.splice(index - 1, 0, field);
  }
};

const moveFieldDown = (index: number) => {
  if (index < tableFields.value.length - 1) {
    const field = tableFields.value[index];
    tableFields.value.splice(index, 1);
    tableFields.value.splice(index + 1, 0, field);
  }
};

const addMultipleFields = () => {
  const fieldNames = prompt("请输入要添加的字段名称，用逗号分隔（例如：name,age,email）：");
  if (fieldNames) {
    const names = fieldNames.split(',').map(name => name.trim()).filter(name => name);
    names.forEach(name => {
      tableFields.value.push({
        id: nextFieldId.value,
        name: name,
        type: fieldTypes.value[0] || "varchar",
        length: "",
        nullable: true,
        primaryKey: false,
        autoIncrement: false,
        defaultValue: "",
        comment: ""
      });
      nextFieldId.value++;
    });
  }
};

const generateSQL = () => {
  if (!tableName.value.trim()) {
    alert("请输入表名称");
    return;
  }

  sqlLoading.value = true;
  
  try {
    let sql = "";
    
    // 根据数据库类型生成不同的SQL
    switch (databaseType.value) {
      case "mysql":
        sql = generateMySQLSQL();
        break;
      case "postgresql":
        sql = generatePostgreSQLSQL();
        break;
      case "sqlite":
        sql = generateSQLiteSQL();
        break;
      default:
        sql = generateMySQLSQL();
    }
    
    generatedSQL.value = sql;
  } catch (error) {
    console.error("生成SQL失败:", error);
    generatedSQL.value = "生成SQL时发生错误：" + error;
  } finally {
    sqlLoading.value = false;
  }
};

const generateMySQLSQL = () => {
  let sql = `CREATE TABLE \`${tableName.value}\` (\n`;
  
  const fieldDefinitions = tableFields.value.map(field => {
    let definition = `  \`${field.name}\` ${field.type.toUpperCase()}`;
    
    // 添加长度（如果适用）
    if (field.length && (field.type === 'varchar' || field.type === 'decimal' || field.type === 'float' || field.type === 'double')) {
      definition += `(${field.length})`;
    }
    
    // 添加NOT NULL
    if (!field.nullable) {
      definition += " NOT NULL";
    }
    
    // 添加自增
    if (field.autoIncrement) {
      definition += " AUTO_INCREMENT";
    }
    
    // 添加默认值
    if (field.defaultValue) {
      if (field.type === 'varchar' || field.type === 'text' || field.type === 'datetime' || field.type === 'timestamp') {
        definition += ` DEFAULT '${field.defaultValue}'`;
      } else {
        definition += ` DEFAULT ${field.defaultValue}`;
      }
    }
    
    // 添加注释
    if (field.comment) {
      definition += ` COMMENT '${field.comment}'`;
    }
    
    return definition;
  });
  
  sql += fieldDefinitions.join(",\n");
  
  // 添加主键
  const primaryKeys = tableFields.value.filter(field => field.primaryKey);
  if (primaryKeys.length > 0) {
    sql += `,\n  PRIMARY KEY (\`${primaryKeys.map(pk => pk.name).join('`, `')}\`)`;
  }
  
  sql += "\n)";
  
  // 添加表注释
  if (tableComment.value) {
    sql += ` COMMENT='${tableComment.value}'`;
  }
  
  sql += ";\n";
  
  return sql;
};

const generatePostgreSQLSQL = () => {
  let sql = `CREATE TABLE "${tableName.value}" (\n`;
  
  const fieldDefinitions = tableFields.value.map(field => {
    let definition = `  "${field.name}" ${field.type}`;
    
    // 添加长度（如果适用）
    if (field.length && (field.type === 'varchar' || field.type === 'numeric')) {
      definition += `(${field.length})`;
    }
    
    // 添加NOT NULL
    if (!field.nullable) {
      definition += " NOT NULL";
    }
    
    // 添加自增（PostgreSQL使用SERIAL）
    if (field.autoIncrement && field.type === 'integer') {
      definition = `  "${field.name}" SERIAL`;
      if (!field.nullable) {
        definition += " NOT NULL";
      }
    }
    
    // 添加默认值
    if (field.defaultValue) {
      if (field.type === 'varchar' || field.type === 'text' || field.type === 'timestamp') {
        definition += ` DEFAULT '${field.defaultValue}'`;
      } else {
        definition += ` DEFAULT ${field.defaultValue}`;
      }
    }
    
    // 添加注释（PostgreSQL使用单独的COMMENT语句）
    
    return definition;
  });
  
  sql += fieldDefinitions.join(",\n");
  
  // 添加主键
  const primaryKeys = tableFields.value.filter(field => field.primaryKey);
  if (primaryKeys.length > 0) {
    sql += `,\n  PRIMARY KEY ("${primaryKeys.map(pk => pk.name).join('", "')}")`;
  }
  
  sql += "\n);\n";
  
  // 添加表注释
  if (tableComment.value) {
    sql += `COMMENT ON TABLE "${tableName.value}" IS '${tableComment.value}';\n`;
  }
  
  // 添加字段注释
  tableFields.value.forEach(field => {
    if (field.comment) {
      sql += `COMMENT ON COLUMN "${tableName.value}"."${field.name}" IS '${field.comment}';\n`;
    }
  });
  
  return sql;
};

const generateSQLiteSQL = () => {
  let sql = `CREATE TABLE "${tableName.value}" (\n`;
  
  const fieldDefinitions = tableFields.value.map(field => {
    let definition = `  "${field.name}" ${field.type}`;
    
    // 添加NOT NULL
    if (!field.nullable) {
      definition += " NOT NULL";
    }
    
    // 添加主键（SQLite的主键定义方式不同）
    if (field.primaryKey) {
      definition += " PRIMARY KEY";
    }
    
    // 添加自增（SQLite使用AUTOINCREMENT）
    if (field.autoIncrement && field.primaryKey) {
      definition += " AUTOINCREMENT";
    }
    
    // 添加默认值
    if (field.defaultValue) {
      if (field.type === 'TEXT') {
        definition += ` DEFAULT '${field.defaultValue}'`;
      } else {
        definition += ` DEFAULT ${field.defaultValue}`;
      }
    }
    
    return definition;
  });
  
  sql += fieldDefinitions.join(",\n");
  
  sql += "\n);\n";
  
  // SQLite不支持表注释，但我们可以添加注释作为SQL注释
  if (tableComment.value) {
    sql = `-- ${tableComment.value}\n${sql}`;
  }
  
  return sql;
};

const copySQL = () => {
  if (!generatedSQL.value) return;
  
  navigator.clipboard.writeText(generatedSQL.value)
    .then(() => {
      alert("SQL已复制到剪贴板");
    })
    .catch(err => {
      console.error("复制失败:", err);
      alert("复制失败，请手动复制");
    });
};

const createTableRemote = async () => {
  if (!tableName.value.trim()) {
    alert($t('generator.table_name') + " " + $t('generator.is_required'));
    return;
  }

  // 验证字段
  for (const field of tableFields.value) {
    if (!field.name.trim()) {
      alert($t('generator.field_name') + " " + $t('generator.is_required'));
      return;
    }
  }

  createTableLoading.value = true;
  
  try {
    const requestData = {
      table_name: tableName.value,
      database_type: databaseType.value,
      table_comment: tableComment.value,
      fields: tableFields.value.map(field => ({
        name: field.name,
        type: field.type,
        length: field.length || undefined,
        nullable: field.nullable,
        primaryKey: field.primaryKey,
        autoIncrement: field.autoIncrement,
        defaultValue: field.defaultValue || undefined,
        comment: field.comment || undefined
      }))
    };

    // 直接调用API，不检查response.code
    await requestClient.post(
      `${import.meta.env.VITE_GLOB_API_URL}/plugins/generator/create-table`,
      requestData
    );
    
    // 如果API调用成功（没有抛出异常），则显示成功消息
    alert($t('generator.create_table_success') + ": " + tableName.value);
    
    // 刷新表列表
    await fetchTables();
    
  } catch (error: any) {
    console.error("远程创建表失败:", error);
    
    // 调试信息
    console.log("错误对象:", error);
    console.log("错误响应:", error.response);
    console.log("错误数据:", error.response?.data);
    
    let errorMessage = "未知错误";
    
    if (error.response?.status === 400) {
      if (error.response?.data?.detail?.includes("已存在")) {
        errorMessage = $t('generator.table_already_exists') + ": " + tableName.value;
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.response?.data?.msg) {
        errorMessage = error.response.data.msg;
      } else if (error.response?.data?.errors) {
        errorMessage = Array.isArray(error.response.data.errors) 
          ? error.response.data.errors.join(", ")
          : String(error.response.data.errors);
      }
    } else if (error.response?.data?.msg) {
      errorMessage = error.response.data.msg;
    } else if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    alert($t('generator.create_table_failed') + ": " + errorMessage);
  } finally {
    createTableLoading.value = false;
  }
};

const clearForm = () => {
  tableName.value = "";
  tableComment.value = "";
  tableFields.value = [
    {
      id: 1,
      name: "id",
      type: "int",
      length: "11",
      nullable: false,
      primaryKey: true,
      autoIncrement: true,
      defaultValue: "",
      comment: "主键ID"
    }
  ];
  nextFieldId.value = 2;
  generatedSQL.value = "";
};

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

.flex {
  display: flex;
}
.justify-between {
  justify-content: space-between;
}
.items-center {
  align-items: center;
}
.mr-2 {
  margin-right: 0.5rem;
}

/* 表格样式 */
:deep(.ant-table-thead > tr > th) {
  background-color: #fafafa;
  font-weight: 600;
}

:deep(.ant-table-tbody > tr > td) {
  padding: 8px;
}

/* 表单样式 */
:deep(.ant-form-item) {
  margin-bottom: 0;
}

:deep(.ant-form-item-label) {
  font-weight: 500;
}
</style>
