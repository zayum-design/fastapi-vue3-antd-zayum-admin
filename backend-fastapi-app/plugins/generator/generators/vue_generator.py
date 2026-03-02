"""
Vue代码生成器
生成Vue前端代码
"""

from sqlalchemy import Table


class VueGenerator:
    """Vue代码生成器类"""
    
    def generate(self, table: Table, fields: str = 'all', operations: str = 'create,read,update,delete') -> str:
        """生成Vue代码"""
        class_name = "".join(word.capitalize() for word in table.name.split("_"))
        
        # 构建Vue代码
        vue_code = f'''<!-- {class_name} 管理页面 -->
<template>
  <div class="{table.name}-management">
    <a-card :title="$t('{table.name}.title')" :bordered="false">
      <!-- 搜索和操作区域 -->
      <div class="table-toolbar">
        <a-space>
          <a-input-search
            v-model:value="searchText"
            :placeholder="$t('common.search')"
            style="width: 300px"
            @search="handleSearch"
          />
          <a-button type="primary" @click="handleAdd">
            <template #icon><plus-outlined /></template>
            {{ $t('common.add') }}
          </a-button>
        </a-space>
      </div>

      <!-- 数据表格 -->
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :pagination="pagination"
        :loading="loading"
        @change="handleTableChange"
      >
        <template #bodyCell="{{ column, record }}">
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)">
                {{ $t('common.edit') }}
              </a-button>
              <a-button type="link" size="small" danger @click="handleDelete(record)">
                {{ $t('common.delete') }}
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑模态框 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :confirm-loading="confirmLoading"
      @ok="handleModalOk"
      @cancel="handleModalCancel"
    >
      <a-form
        ref="formRef"
        :model="formState"
        :rules="rules"
        :label-col="{{ span: 6 }}"
        :wrapper-col="{{ span: 16 }}"
      >
        <!-- 表单字段将根据表结构动态生成 -->
        {self._generate_form_fields(table)}
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import {{ ref, reactive, onMounted }} from 'vue'
import {{ message }} from 'ant-design-vue'
import {{ useI18n }} from 'vue-i18n'
import {{ PlusOutlined }} from '@ant-design/icons-vue'

const {{ t }} = useI18n()

// 响应式数据
const searchText = ref('')
const loading = ref(false)
const modalVisible = ref(false)
const confirmLoading = ref(false)
const formRef = ref()
const dataSource = ref([])
const formState = reactive({{}})

// 分页配置
const pagination = reactive({{
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => t('common.total', {{ total }})
}})

// 表格列配置
const columns = {self._generate_table_columns(table)}

// 表单验证规则
const rules = {self._generate_form_rules(table)}

// 计算模态框标题
const modalTitle = computed(() => {{
  return formState.id ? t('common.edit') : t('common.add')
}})

// 生命周期
onMounted(() => {{
  fetchData()
}})

// 方法
const fetchData = async () => {{
  loading.value = true
  try {{
    // 调用API获取数据
    const response = await api{table.name}.getList({{
      page: pagination.current,
      per_page: pagination.pageSize,
      search: searchText.value
    }})
    dataSource.value = response.data.items
    pagination.total = response.data.total
  }} catch (error) {{
    message.error(t('common.fetchFailed'))
  }} finally {{
    loading.value = false
  }}
}}

const handleSearch = () => {{
  pagination.current = 1
  fetchData()
}}

const handleAdd = () => {{
  Object.keys(formState).forEach(key => delete formState[key])
  modalVisible.value = true
}}

const handleEdit = (record: any) => {{
  Object.assign(formState, record)
  modalVisible.value = true
}}

const handleDelete = async (record: any) => {{
  const confirmed = await confirmDelete()
  if (!confirmed) return
  
  try {{
    await api{table.name}.delete(record.id)
    message.success(t('common.deleteSuccess'))
    fetchData()
  }} catch (error) {{
    message.error(t('common.deleteFailed'))
  }}
}}

const handleModalOk = async () => {{
  try {{
    await formRef.value.validate()
    confirmLoading.value = true
    
    if (formState.id) {{
      await api{table.name}.update(formState.id, formState)
      message.success(t('common.updateSuccess'))
    }} else {{
      await api{table.name}.create(formState)
      message.success(t('common.createSuccess'))
    }}
    
    modalVisible.value = false
    fetchData()
  }} catch (error) {{
    console.error('Form validation failed:', error)
  }} finally {{
    confirmLoading.value = false
  }}
}}

const handleModalCancel = () => {{
  modalVisible.value = false
  formRef.value?.resetFields()
}}

const handleTableChange = (pag: any) => {{
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchData()
}}

const confirmDelete = (): Promise<boolean> => {{
  return new Promise((resolve) => {{
    Modal.confirm({{
      title: t('common.confirmDelete'),
      okText: t('common.ok'),
      cancelText: t('common.cancel'),
      onOk: () => resolve(true),
      onCancel: () => resolve(false)
    }})
  }})
}}
</script>

<style scoped>
.{table.name}-management {{
  padding: 24px;
}}

.table-toolbar {{
  margin-bottom: 16px;
}}
</style>
'''
        return vue_code
    
    def _generate_form_fields(self, table: Table) -> str:
        """生成表单字段"""
        form_fields = ""
        for col in table.columns:
            if col.name.lower() in ["id", "created_at", "updated_at"]:
                continue
            form_fields += f'''
        <a-form-item :label="$t('{table.name}.{col.name}')" name="{col.name}">
          <a-input v-model:value="formState.{col.name}" />
        </a-form-item>'''
        return form_fields
    
    def _generate_table_columns(self, table: Table) -> str:
        """生成表格列配置"""
        columns = []
        for col in table.columns:
            if col.name.lower() in ["created_at", "updated_at"]:
                continue
            columns.append(f'''
    {{
      title: t('{table.name}.{col.name}'),
      dataIndex: '{col.name}',
      key: '{col.name}',
    }}''')
        
        columns.append('''
    {
      title: t('common.action'),
      key: 'action',
      width: 150,
    }''')
        
        return f"[{','.join(columns)}\n  ]"
    
    def _generate_form_rules(self, table: Table) -> str:
        """生成表单验证规则"""
        rules = {}
        for col in table.columns:
            if col.name.lower() in ["id", "created_at", "updated_at"] or col.nullable:
                continue
            rules[col.name] = f'[{{ required: true, message: t(\'{table.name}.{col.name}Required\') }}]'
        
        return str(rules).replace("'", "")
