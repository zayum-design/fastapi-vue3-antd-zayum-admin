/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly PROD: boolean
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_NAMESPACE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
