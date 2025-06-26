import { defineStore } from 'pinia'
import { ref } from 'vue'

interface Plugin {
  id: string
  name: string
  description: string
  routes?: Array<{
    path: string
    name: string
    meta?: {
      title: string
    }
  }>
  active?: boolean
}

export const usePluginStore = defineStore('plugin', () => {
  const availablePlugins = ref<Plugin[]>([])
  const activePlugins = ref<Plugin[]>([])

  const loadPlugins = async () => {
    // 模拟加载插件
    availablePlugins.value = [
      {
        id: 'sample',
        name: '示例插件',
        description: '这是一个示例插件',
        routes: [
          {
            path: '/plugins/sample/dashboard',
            name: 'sample-dashboard',
            meta: { title: '示例仪表盘' }
          }
        ]
      }
    ]
    activePlugins.value = []
  }

  const activatePlugin = async (pluginId: string) => {
    const plugin = availablePlugins.value.find(p => p.id === pluginId)
    if (plugin) {
      activePlugins.value.push(plugin)
      return { status: 'success' }
    }
    return { status: 'error', message: '插件未找到' }
  }

  return {
    availablePlugins,
    activePlugins,
    loadPlugins,
    activatePlugin
  }
})
