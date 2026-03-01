<template>
  <div class="language-manager">
    <a-card :title="$t('general.language_manager')" class="mb-4">
      <template #extra>
        <a-button type="primary" @click="showAddLanguageModal">
          <template #icon>
            <PlusOutlined />
          </template>
          {{ $t('common.add') }}
        </a-button>
      </template>

      <a-alert
        v-if="languages.length === 0"
        type="info"
        :message="$t('general.no_languages_found')"
        show-icon
        class="mb-4"
      />

      <a-table
        v-else
        :data-source="languages"
        :columns="columns"
        :pagination="false"
        row-key="code"
        class="mb-4"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'actions'">
            <a-space>
              <a-button
                type="link"
                size="small"
                @click="editLanguage(record)"
              >
                {{ $t('common.edit') }}
              </a-button>
              <a-button
                v-if="!record.isDefault"
                type="link"
                size="small"
                danger
                @click="deleteLanguage(record)"
              >
                {{ $t('common.delete') }}
              </a-button>
              <a-button
                type="link"
                size="small"
                @click="manageFiles(record)"
              >
                {{ $t('general.manage_files') }}
              </a-button>
            </a-space>
          </template>
          <template v-else-if="column.key === 'isDefault'">
            <a-tag v-if="record.code === defaultLanguage" color="blue">
              {{ $t('general.default') }}
            </a-tag>
            <a-button
              v-else
              type="link"
              size="small"
              @click="setAsDefault(record)"
            >
              {{ $t('general.set_as_default') }}
            </a-button>
          </template>
          <template v-else-if="column.key === 'fileCount'">
            {{ record.fileCount }}
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑语言模态框 -->
    <a-modal
      v-model:open="languageModalVisible"
      :title="modalTitle"
      @ok="handleLanguageModalOk"
      @cancel="handleLanguageModalCancel"
    >
      <a-form
        ref="languageFormRef"
        :model="languageForm"
        :rules="languageFormRules"
        layout="vertical"
      >
        <a-form-item
          :label="$t('general.language_code')"
          name="code"
        >
          <a-input
            v-model:value="languageForm.code"
            :placeholder="$t('general.language_code_placeholder')"
            :disabled="isEditing"
          />
        </a-form-item>
        <a-form-item
          :label="$t('general.language_name')"
          name="name"
        >
          <a-input
            v-model:value="languageForm.name"
            :placeholder="$t('general.language_name_placeholder')"
          />
        </a-form-item>
        <a-form-item
          :label="$t('general.language_native_name')"
          name="nativeName"
        >
          <a-input
            v-model:value="languageForm.nativeName"
            :placeholder="$t('general.language_native_name_placeholder')"
          />
        </a-form-item>
        <a-form-item
          :label="$t('general.copy_from')"
          name="copyFrom"
        >
          <a-select
            v-model:value="languageForm.copyFrom"
            :placeholder="$t('general.copy_from_placeholder')"
            allow-clear
          >
            <a-select-option
              v-for="lang in existingLanguages"
              :key="lang.code"
              :value="lang.code"
            >
              {{ lang.name }} ({{ lang.code }})
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 文件管理模态框 -->
    <a-modal
      v-model:open="fileManagerModalVisible"
      :title="fileManagerTitle"
      width="80%"
      @cancel="handleFileManagerCancel"
    >
      <a-card :title="$t('general.language_files')" class="mb-4">
        <template #extra>
          <a-button type="primary" @click="showAddFileModal">
            <template #icon>
              <PlusOutlined />
            </template>
            {{ $t('general.add_file') }}
          </a-button>
        </template>

        <a-table
          :data-source="currentLanguageFiles"
          :columns="fileColumns"
          :pagination="false"
          row-key="name"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button
                  type="link"
                  size="small"
                  @click="editFile(record)"
                >
                  {{ $t('common.edit') }}
                </a-button>
                <a-button
                  v-if="!record.isRequired"
                  type="link"
                  size="small"
                  danger
                  @click="deleteFile(record)"
                >
                  {{ $t('common.delete') }}
                </a-button>
              </a-space>
            </template>
            <template v-else-if="column.key === 'size'">
              {{ formatFileSize(record.size) }}
            </template>
          </template>
        </a-table>
      </a-card>

      <!-- 文件编辑器 -->
      <a-card v-if="currentFile" :title="currentFileName">
        <template #extra>
          <a-space>
            <a-button @click="saveFile">
              {{ $t('common.confirm') }}
            </a-button>
            <a-button @click="cancelEdit">
              {{ $t('common.cancel') }}
            </a-button>
          </a-space>
        </template>

        <div class="file-editor">
          <a-alert
            v-if="fileError"
            type="error"
            :message="fileError"
            show-icon
            class="mb-4"
          />

          <div class="editor-container">
            <CodeEditor
              v-model:code="fileContent"
              language="json"
            />
          </div>
        </div>
      </a-card>
    </a-modal>

    <!-- 添加文件模态框 -->
    <a-modal
      v-model:open="addFileModalVisible"
      :title="$t('general.add_file')"
      @ok="handleAddFileOk"
      @cancel="handleAddFileCancel"
    >
      <a-form
        ref="addFileFormRef"
        :model="addFileForm"
        :rules="addFileFormRules"
        layout="vertical"
      >
        <a-form-item
          :label="$t('general.file_name')"
          name="fileName"
        >
          <a-input
            v-model:value="addFileForm.fileName"
            :placeholder="$t('general.file_name_placeholder')"
            addon-after=".json"
          />
        </a-form-item>
        <a-form-item
          :label="$t('general.copy_from_file')"
          name="copyFromFile"
        >
          <a-select
            v-model:value="addFileForm.copyFromFile"
            :placeholder="$t('general.copy_from_file_placeholder')"
            allow-clear
          >
            <a-select-option
              v-for="file in templateFiles"
              :key="file"
              :value="file"
            >
              {{ file }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import CodeEditor from '@/_core/ui/components/CodeEditor.vue'
import { $t } from '@/locales'
import { preferences, updatePreferences } from '@/_core/preferences'

// 动态导入 JSON 文件
const modules = import.meta.glob('@/locales/langs/**/*.json', { eager: false })

interface Language {
  code: string
  name: string
  nativeName: string
  fileCount: number
  isDefault?: boolean
}

interface LanguageFile {
  name: string
  size: number
  isRequired: boolean
  content?: string
}

const defaultLanguage = computed(() => preferences.app.locale)

const languages = ref<Language[]>([
  {
    code: 'zh-CN',
    name: '简体中文',
    nativeName: '简体中文',
    fileCount: 15,
    isDefault: true
  },
  {
    code: 'en-US',
    name: 'English',
    nativeName: 'English',
    fileCount: 15,
    isDefault: false
  }
])

const columns = [
  {
    title: $t('general.language_code'),
    dataIndex: 'code',
    key: 'code'
  },
  {
    title: $t('general.language_name'),
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: $t('general.language_native_name'),
    dataIndex: 'nativeName',
    key: 'nativeName'
  },
  {
    title: $t('general.file_count'),
    key: 'fileCount',
    dataIndex: 'fileCount'
  },
  {
    title: $t('general.default_language'),
    key: 'isDefault'
  },
  {
    title: $t('common.action'),
    key: 'actions'
  }
]

const fileColumns = [
  {
    title: $t('general.file_name'),
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: $t('general.file_size'),
    key: 'size'
  },
  {
    title: $t('common.action'),
    key: 'actions'
  }
]

// 语言管理相关状态
const languageModalVisible = ref(false)
const isEditing = ref(false)
const languageFormRef = ref()
const languageForm = reactive({
  code: '',
  name: '',
  nativeName: '',
  copyFrom: ''
})

const languageFormRules = {
  code: [
    { required: true, message: $t('general.language_code_required') },
    { pattern: /^[a-z]{2}-[A-Z]{2}$/, message: $t('general.language_code_format') }
  ],
  name: [
    { required: true, message: $t('general.language_name_required') }
  ],
  nativeName: [
    { required: true, message: $t('general.language_native_name_required') }
  ]
}

// 文件管理相关状态
const fileManagerModalVisible = ref(false)
const currentLanguageCode = ref('')
const currentLanguageFiles = ref<LanguageFile[]>([])
const currentFile = ref<LanguageFile | null>(null)
const fileContent = ref('')
const fileError = ref('')
const addFileModalVisible = ref(false)
const addFileFormRef = ref()
const addFileForm = reactive({
  fileName: '',
  copyFromFile: ''
})

const addFileFormRules = {
  fileName: [
    { required: true, message: $t('general.file_name_required') },
    { pattern: /^[a-z_]+$/, message: $t('general.file_name_format') }
  ]
}

const editorOptions = {
  minimap: { enabled: true },
  scrollBeyondLastLine: false,
  wordWrap: 'on',
  formatOnPaste: true,
  formatOnType: true
}

const modalTitle = computed(() => {
  return isEditing.value ? $t('general.edit_language') : $t('general.add_language')
})

const fileManagerTitle = computed(() => {
  return `${$t('general.manage_files')} - ${currentLanguageCode.value}`
})

const currentFileName = computed(() => {
  return currentFile.value ? `${currentFile.value.name}.json` : ''
})

const existingLanguages = computed(() => {
  return languages.value.filter(lang => lang.code !== languageForm.code)
})

const templateFiles = computed(() => {
  // 从所有语言文件中提取唯一的文件名
  const fileNames = new Set<string>()
  
  for (const path of Object.keys(modules)) {
    const fileNameMatch = path.match(/\/([^/]+)\.json$/)
    if (fileNameMatch) {
      fileNames.add(fileNameMatch[1])
    }
  }
  
  // 如果没有找到文件，返回默认列表
  if (fileNames.size === 0) {
    return ['common', 'admin', 'user', 'dashboard', 'preferences', 'ui']
  }
  
  return Array.from(fileNames).sort()
})

onMounted(() => {
  loadLanguages()
})

async function loadLanguages() {
  try {
    // TODO: 从API加载语言列表
    console.log('Loading languages...')
  } catch (error) {
    console.error('Failed to load languages:', error)
    message.error($t('general.load_languages_failed'))
  }
}

function showAddLanguageModal() {
  isEditing.value = false
  Object.assign(languageForm, {
    code: '',
    name: '',
    nativeName: '',
    copyFrom: ''
  })
  languageModalVisible.value = true
}

function editLanguage(language: Language) {
  isEditing.value = true
  Object.assign(languageForm, {
    code: language.code,
    name: language.name,
    nativeName: language.nativeName,
    copyFrom: ''
  })
  languageModalVisible.value = true
}

async function handleLanguageModalOk() {
  try {
    await languageFormRef.value.validate()
    
    if (isEditing.value) {
      // 更新现有语言
      const index = languages.value.findIndex(l => l.code === languageForm.code)
      if (index !== -1) {
        languages.value[index] = {
          ...languages.value[index],
          name: languageForm.name,
          nativeName: languageForm.nativeName
        }
      }
      message.success($t('general.language_updated'))
    } else {
      // 添加新语言
      const newLanguage: Language = {
        code: languageForm.code,
        name: languageForm.name,
        nativeName: languageForm.nativeName,
        fileCount: 0
      }
      
      // TODO: 调用API创建语言目录和文件
      if (languageForm.copyFrom) {
        // 复制现有语言的文件
        // TODO: 实现复制逻辑
      }
      
      languages.value.push(newLanguage)
      message.success($t('general.language_added'))
    }
    
    languageModalVisible.value = false
  } catch (error) {
    console.error('Language form validation failed:', error)
  }
}

function handleLanguageModalCancel() {
  languageModalVisible.value = false
  languageFormRef.value?.resetFields()
}

function deleteLanguage(language: Language) {
  Modal.confirm({
    title: $t('general.confirm_delete_language'),
    content: $t('general.confirm_delete_language_content', { language: language.name }),
    okText: $t('common.confirm'),
    okType: 'danger',
    cancelText: $t('common.cancel'),
    async onOk() {
      try {
        // TODO: 调用API删除语言
        languages.value = languages.value.filter(l => l.code !== language.code)
        message.success($t('general.language_deleted'))
      } catch (error) {
        console.error('Failed to delete language:', error)
        message.error($t('general.delete_language_failed'))
      }
    }
  })
}

function setAsDefault(language: Language) {
  Modal.confirm({
    title: $t('general.confirm_set_default'),
    content: $t('general.confirm_set_default_content', { language: language.name }),
    okText: $t('common.confirm'),
    cancelText: $t('common.cancel'),
    async onOk() {
      try {
        // TODO: 调用API设置默认语言
        updatePreferences({
          app: {
            locale: language.code as any
          }
        })
        message.success($t('general.default_language_set'))
      } catch (error) {
        console.error('Failed to set default language:', error)
        message.error($t('general.set_default_failed'))
      }
    }
  })
}

function manageFiles(language: Language) {
  currentLanguageCode.value = language.code
  loadLanguageFiles(language.code)
  fileManagerModalVisible.value = true
}

async function loadLanguageFiles(languageCode: string) {
  try {
    // 查找该语言的所有文件
    const languageFiles: LanguageFile[] = []
    const requiredFiles = ['common', 'admin', 'user'] // 必需的文件
    
    for (const [path, importFn] of Object.entries(modules)) {
      if (path.includes(`/${languageCode}/`)) {
        const fileNameMatch = path.match(/\/([^/]+)\.json$/)
        if (fileNameMatch) {
          const fileName = fileNameMatch[1]
          const isRequired = requiredFiles.includes(fileName)
          
          try {
            // 加载文件以获取大小
            const module = await importFn() as any
            const content = module.default || module
            const contentStr = JSON.stringify(content)
            const size = new Blob([contentStr]).size
            
            languageFiles.push({
              name: fileName,
              size: size,
              isRequired: isRequired
            })
          } catch (error) {
            // 如果加载失败，使用默认大小
            languageFiles.push({
              name: fileName,
              size: 1024,
              isRequired: isRequired
            })
          }
        }
      }
    }
    
    // 如果没有找到文件，使用默认列表
    if (languageFiles.length === 0) {
      languageFiles.push(
        { name: 'common', size: 2048, isRequired: true },
        { name: 'admin', size: 4096, isRequired: true },
        { name: 'user', size: 1024, isRequired: true },
        { name: 'dashboard', size: 512, isRequired: false },
        { name: 'preferences', size: 1024, isRequired: false },
        { name: 'ui', size: 768, isRequired: false }
      )
    }
    
    currentLanguageFiles.value = languageFiles
  } catch (error) {
    console.error('Failed to load language files:', error)
    message.error($t('general.load_files_failed'))
  }
}

function showAddFileModal() {
  Object.assign(addFileForm, {
    fileName: '',
    copyFromFile: ''
  })
  addFileModalVisible.value = true
}

async function handleAddFileOk() {
  try {
    await addFileFormRef.value.validate()
    
    // TODO: 调用API创建文件
    const newFile: LanguageFile = {
      name: addFileForm.fileName,
      size: 0,
      isRequired: false
    }
    
    if (addFileForm.copyFromFile) {
      // TODO: 复制文件内容
    }
    
    currentLanguageFiles.value.push(newFile)
    addFileModalVisible.value = false
    message.success($t('general.file_added'))
  } catch (error) {
    console.error('Add file form validation failed:', error)
  }
}

function handleAddFileCancel() {
  addFileModalVisible.value = false
  addFileFormRef.value?.resetFields()
}

async function editFile(file: LanguageFile) {
  currentFile.value = file
  fileError.value = ''
  
  try {
    // 构建文件路径
    const filePath = `@/locales/langs/${currentLanguageCode.value}/${file.name}.json`
    
    // 查找对应的模块
    const moduleKey = Object.keys(modules).find(key => 
      key.includes(`/${currentLanguageCode.value}/${file.name}.json`)
    )
    
    if (moduleKey && modules[moduleKey]) {
      // 加载文件内容
      const module = await modules[moduleKey]() as any
      const content = module.default || module
      fileContent.value = JSON.stringify(content, null, 2)
    } else {
      // 如果文件不存在，创建空对象
      fileContent.value = JSON.stringify({}, null, 2)
      message.warning($t('general.file_not_found_creating_empty'))
    }
  } catch (error) {
    console.error('Failed to load file:', error)
    fileError.value = $t('general.load_file_failed')
    // 如果加载失败，创建空对象
    fileContent.value = JSON.stringify({}, null, 2)
  }
}

function deleteFile(file: LanguageFile) {
  Modal.confirm({
    title: $t('general.confirm_delete_file'),
    content: $t('general.confirm_delete_file_content', { file: file.name }),
    okText: $t('common.confirm'),
    okType: 'danger',
    cancelText: $t('common.cancel'),
    async onOk() {
      try {
        // TODO: 调用API删除文件
        currentLanguageFiles.value = currentLanguageFiles.value.filter(f => f.name !== file.name)
        if (currentFile.value?.name === file.name) {
          currentFile.value = null
        }
        message.success($t('general.file_deleted'))
      } catch (error) {
        console.error('Failed to delete file:', error)
        message.error($t('general.delete_file_failed'))
      }
    }
  })
}

async function saveFile() {
  try {
    // 验证JSON格式
    const parsedContent = JSON.parse(fileContent.value)
    
    if (!currentFile.value) {
      message.error($t('general.no_file_selected'))
      return
    }
    
    // TODO: 调用API保存文件
    // 目前先模拟保存成功
    console.log('Saving file:', {
      language: currentLanguageCode.value,
      file: currentFile.value.name,
      content: parsedContent
    })
    
    // 更新本地模块缓存
    const moduleKey = Object.keys(modules).find(key => 
      key.includes(`/${currentLanguageCode.value}/${currentFile.value.name}.json`)
    )
    
    if (moduleKey) {
      // 更新模块缓存
      modules[moduleKey] = async () => ({ default: parsedContent })
    }
    
    message.success($t('general.file_saved'))
    fileError.value = ''
    
    // 重新加载文件列表以更新文件大小
    await loadLanguageFiles(currentLanguageCode.value)
    
  } catch (error) {
    fileError.value = $t('general.invalid_json_format')
    console.error('Invalid JSON:', error)
  }
}

function cancelEdit() {
  currentFile.value = null
  fileContent.value = ''
  fileError.value = ''
}

function handleFileManagerCancel() {
  fileManagerModalVisible.value = false
  currentLanguageCode.value = ''
  currentLanguageFiles.value = []
  currentFile.value = null
  fileContent.value = ''
  fileError.value = ''
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>
