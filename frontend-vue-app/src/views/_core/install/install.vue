<script setup lang="ts">
import { ref, nextTick } from "vue";

import {
  message,
  type FormInstance,
  type SelectProps,
  type CheckboxOptionType,
} from "ant-design-vue";

import { useRouter } from "vue-router";
import {
  testDatabaseConnection,
  completeInstallation,
  importDatabase,
  restart,
} from "@/api/admin/install";

const router = useRouter();

// 当前步骤
const currentStep = ref(0);

// 数据库类型选项
const databaseTypes: SelectProps["options"] = [
  { value: "mysql", label: "MySQL" },
  { value: "postgresql", label: "PostgreSQL" },
  { value: "sqlite", label: "SQLite" },
  { value: "sqlserver", label: "SQL Server" },
];

// 步骤配置
const steps = [
  { title: "数据库配置", description: "配置数据库连接信息" },
  { title: "导入数据", description: "导入系统初始数据" },
  { title: "系统设置", description: "设置管理员账号和系统信息" },
  { title: "完成安装", description: "安装完成，准备使用系统" },
];

// 表单数据
const dbForm = ref({
  type: "mysql",
  host: "localhost",
  port: 3306,
  username: "root",
  password: "password",
  database: "fastapi-vue3-antd-zayum-admin-1.2",
  prefix: "zayum_",
});

const configForm = ref({
  username: "admin",
  password: "Njh88888888",
  email: "13800000000@qq.com",
  mobile: "13800000000",
  nickname: "系统管理员",
  siteName: "Zayum Admin",
  siteUrl: window.location.origin,
  timezone: "Asia/Shanghai",
});

// 导入选项
interface CheckboxOptionTypeWithChecked extends CheckboxOptionType {
  checked?: boolean;
}

const importOptions = ref<CheckboxOptionTypeWithChecked[]>([
  {
    label: "系统核心表结构（必选）",
    value: "core",
    disabled: true,
    checked: true,
  },
  { label: "示例数据（可选）", value: "sample", checked: false },
]);

const importValue = ref(["core"]);

// 测试数据库连接
const testingConnection = ref(false);
const testConnection = async () => {
  try {
    testingConnection.value = true;
    // Only send required fields to backend
    const { host, port, username, password, database } = dbForm.value;
    await testDatabaseConnection({ host, port, username, password, database });
    currentStep.value = 1;
    message.success("数据库连接成功");
  } catch (error) {
    message.error("数据库连接失败");
  } finally {
    testingConnection.value = false;
  }
};

// 导入数据库
const importingDatabase = ref(false);
const importCompleted = ref(false);
const importProgress = ref("0/0");
const importLogs = ref<string[]>([]);

const importData = async (currentTable?: string | null) => {
  try {
    importingDatabase.value = true;

    if (!currentTable) {
      importLogs.value = [];
      importLogs.value.push("开始导入数据...");
    } else {
      importLogs.value.push(`表 ${currentTable} 开始导入`);
    }
    const response = await importDatabase(
      { current_table: currentTable || null },
      []
    );
    if (response.next_table) {
      importLogs.value.push(`✅ 表 ${currentTable} 导入成功`);
      await new Promise((resolve) => setTimeout(resolve, 100));
      importProgress.value = response.progress ?? "0/0";
      await importData(response.next_table);
    } else {
      importLogs.value.push("✅ 所有数据导入完成");
      importCompleted.value = true;
      importProgress.value = response.progress ?? "0/0";
    }
    
  } catch (error: any) {
    const errorMsg =
      error.response?.data?.msg || error.message || "导入过程中发生未知错误";
    importLogs.value.push(`导入失败: ${errorMsg}`);
    message.error(errorMsg);
  } finally {
    importingDatabase.value = false;
  }
};

// 完成安装
const completingInstall = ref(false);
    const completeInstall = async () => {
      try {
        // 构建符合后端要求的完整数据
        await completeInstallation(configForm.value);
        message.success("系统安装成功");
        currentStep.value = 3;
        completingInstall.value = false;
        restart()
      } catch (error) {
        console.error("安装失败", error);
        message.error("安装失败，请检查日志");
      } finally {
        completingInstall.value = false;
      }
    };

// 表单验证规则
const dbRules = {
  type: [{ required: true, message: "请选择数据库类型" }],
  host: [{ required: true, message: "请输入数据库主机" }],
  port: [{ required: true, message: "请输入数据库端口" }],
  username: [{ required: true, message: "请输入数据库用户名" }],
  database: [{ required: true, message: "请输入数据库名称" }],
};

const configRules = {
  username: [{ required: true, message: "请输入管理员用户名" }],
  password: [{ required: true, message: "请输入管理员密码" }],
  email: [
    { required: true, message: "请输入邮箱" },
    { type: 'email', message: '请输入有效的邮箱地址' }
  ],
  mobile: [
    { required: true, message: "请输入手机号" },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码' }
  ],
  nickname: [{ required: true, message: "请输入昵称" }],
  confirmPassword: [
    { required: true, message: "请确认密码" },
    {
      validator: (_rule: any, value: string) => {
        if (value !== configForm.value.password) {
          return Promise.reject("两次输入的密码不一致");
        }
        return Promise.resolve();
      },
    },
  ],
  siteName: [{ required: true, message: "请输入站点名称" }],
  siteUrl: [{ required: true, message: "请输入站点URL" }],
};

// 表单引用
const dbFormRef = ref<FormInstance>();
const configFormRef = ref<FormInstance>();
</script>

<template>
  <div class="w-full">
    <div class="text-center mb-10">
      <h1 class="text-3xl font-semibold text-gray-800">Zayum Admin 安装向导</h1>
      <p class="text-sm text-gray-500">轻松完成系统安装与配置</p>
    </div>

    <a-steps :current="currentStep" :items="steps" size="" class="w-full" />

    <div class="space-y-8">
      <!-- 第一步：数据库配置 -->
      <div v-if="currentStep === 0" class="space-y-6 w-full">
        <h2 class="text-2xl font-semibold text-gray-800">数据库配置</h2>
        <p class="text-sm text-gray-500">
          请填写您的数据库连接信息，系统将测试连接是否可用
        </p>

        <a-form
          ref="dbFormRef"
          :model="dbForm"
          :rules="dbRules"
          layout="vertical"
          class="max-w-3xl mx-auto"
        >
          <a-form-item label="数据库类型" name="type">
            <a-select v-model:value="dbForm.type" :options="databaseTypes" />
          </a-form-item>

          <a-form-item label="数据库主机" name="host">
            <a-input
              v-model:value="dbForm.host"
              placeholder="例如: localhost 或 127.0.0.1"
            />
          </a-form-item>

          <a-form-item label="数据库端口" name="port">
            <a-input-number v-model:value="dbForm.port" class="w-full" />
          </a-form-item>

          <a-form-item label="数据库用户名" name="username">
            <a-input
              v-model:value="dbForm.username"
              placeholder="数据库登录用户名"
            />
          </a-form-item>

          <a-form-item label="数据库密码" name="password">
            <a-input-password
              v-model:value="dbForm.password"
              placeholder="数据库登录密码"
            />
          </a-form-item>

          <a-form-item label="数据库名称" name="database">
            <a-input
              v-model:value="dbForm.database"
              placeholder="要使用的数据库名称"
            />
          </a-form-item>

          <a-form-item label="数据表前缀" name="prefix">
            <a-input v-model:value="dbForm.prefix" placeholder="数据表前缀" />
          </a-form-item>

          <div class="flex justify-end gap-4 mt-8">
            <a-button
              type="primary"
              size="large"
              :loading="testingConnection"
              @click="dbFormRef?.validate().then(() => testConnection())"
            >
              测试连接并下一步
            </a-button>
          </div>
        </a-form>
      </div>

      <!-- 第二步：导入数据 -->
      <div v-if="currentStep === 1" class="space-y-6">
        <h2 class="text-2xl font-semibold text-gray-800">导入数据</h2>
        <p class="text-sm text-gray-500">
          选择需要导入的数据类型，系统将初始化数据库
        </p>

        <div class="max-w-3xl mx-auto my-6">
          <a-card title="导入选项" size="small">
            <a-checkbox-group
              :options="importOptions"
              v-model:value="importValue"
              class="space-y-4"
            >
              <a-checkbox
                v-for="option in importOptions"
                :key="option.value"
                v-model:checked="option.checked"
                :disabled="option.disabled"
                class="flex items-center"
              >
                <span
                  :class="{ 'text-gray-700 font-medium': option.disabled }"
                  >{{ option.label }}</span
                >
              </a-checkbox>
            </a-checkbox-group>

            <div class="p-4 bg-gray-100 rounded-md mt-4">
              <h4 class="text-gray-800 font-medium mb-3">导入说明：</h4>
              <ul class="list-disc pl-5 space-y-2">
                <li><strong>系统核心表结构</strong> - 必须导入</li>
                <li><strong>示例数据</strong> - 可选导入</li>
              </ul>
            </div>
          </a-card>
          <a-card
            v-if="importingDatabase || importLogs.length > 0"
            title="导入进度"
            size="small"
            :style="{ marginTop: '16px' }"
          >
            
            
            <div class="border rounded-md p-4 bg-gray-50 h-64 overflow-y-auto">
              <div v-for="(log, index) in importLogs" :key="index" class="py-1">
                {{ log }}
              </div>
            </div>
            
            <a-alert
              v-if="importCompleted"
              type="success"
              show-icon
              message="数据导入已完成"
              description="所有数据已成功导入，请点击下一步继续"
              :style="{ marginTop: '16px' }"
            />
          </a-card>
          <div class="flex justify-end gap-4 mt-8">
            <a-button @click="currentStep = 0" size="large">上一步</a-button>
            <a-button
              type="primary"
              size="large"
              :loading="importingDatabase"
              @click="importCompleted ? (currentStep = 2) : importData()"
            >
              {{ importCompleted ? "下一步" : "导入数据" }}
            </a-button>
          </div>
        </div>
      </div>

      <!-- 第三步：系统设置 -->
      <div v-if="currentStep === 2" class="space-y-6">
        <h2 class="text-2xl font-semibold text-gray-800">系统设置</h2>
        <p class="text-sm text-gray-500">请设置管理员账号、系统名称等信息</p>

        <a-form
          ref="configFormRef"
          :model="configForm"
          :rules="configRules"
          layout="vertical"
          class="max-w-3xl mx-auto"
        >
          <a-form-item label="管理员用户名" name="username">
            <a-input
              v-model:value="configForm.username"
              placeholder="管理员用户名"
            />
          </a-form-item>

          <a-form-item label="管理员密码" name="password">
            <a-input-password
              v-model:value="configForm.password"
              placeholder="管理员密码"
            />
          </a-form-item>

          <a-form-item label="邮箱" name="email">
            <a-input
              v-model:value="configForm.email"
              placeholder="管理员邮箱"
              type="email"
            />
          </a-form-item>

          <a-form-item label="手机号" name="mobile">
            <a-input
              v-model:value="configForm.mobile"
              placeholder="管理员手机号"
              maxlength="11"
            />
          </a-form-item>

          <a-form-item label="昵称" name="nickname">
            <a-input
              v-model:value="configForm.nickname"
              placeholder="管理员昵称"
            />
          </a-form-item>
 
          <a-form-item label="站点名称" name="siteName">
            <a-input
              v-model:value="configForm.siteName"
              placeholder="站点名称"
            />
          </a-form-item>

          <a-form-item label="站点 URL" name="siteUrl">
            <a-input v-model:value="configForm.siteUrl" placeholder="站点URL" />
          </a-form-item>

          <a-form-item label="时区" name="timezone">
            <a-select v-model:value="configForm.timezone" class="w-full">
              <a-select-option value="Asia/Shanghai">上海</a-select-option>
              <a-select-option value="UTC">UTC</a-select-option>
              <a-select-option value="America/New_York">纽约</a-select-option>
              <!-- 更多时区 -->
            </a-select>
          </a-form-item>

          <div class="flex justify-end gap-4 mt-8">
            <a-button @click="currentStep = 1" size="large">上一步</a-button>
            <a-button
              type="primary"
              size="large"
              :loading="completingInstall"
              @click="completeInstall"
            >
              完成安装
            </a-button>
          </div>
        </a-form>
      </div>

      <!-- 第四步：完成安装 -->
      <div v-if="currentStep === 3" class="text-center">
        <h2 class="text-2xl font-semibold text-gray-800">安装完成</h2>
        <p class="text-sm text-gray-500">系统已成功安装！</p>
        <a-button type="primary" size="large" @click="router.push('/login')">
          登录系统
        </a-button>
      </div>
    </div>
  </div>
</template>
