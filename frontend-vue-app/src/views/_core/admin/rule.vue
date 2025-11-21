<template>
  <div>
    <a-row justify="center">
      <a-col :span="24">
        <a-card bordered>
          <a-card-header class="flex items-center justify-between">
            <a-space wrap>
              <AccessControl :codes="['admin.rule.add', 'all']" type="code">
                <a-button
                  type="primary"
                  success
                  @click="openDialog(currentItem, 'add')"
                >
                  <template #icon>
                    <FileAddOutlined />
                  </template>
                  {{ $t("common.add_item") }}
                </a-button>
              </AccessControl>
              <AccessControl :codes="['admin.rule.delete', 'all']" type="code">
                <a-popconfirm
                  :title="$t('common.confirm_delete')"
                  :ok-text="$t('common.yes')"
                  :cancel-text="$t('common.no')"
                  @confirm="deleteSelectedItems"
                >
                  <a-button
                    type="primary"
                    danger
                    :disabled="state.selectedRowIds.length === 0"
                    shape="round"
                    :size="size"
                  >
                    <template #icon>
                      <DeleteOutlined />
                    </template>
                    {{ $t("common.delete_selected") }}
                  </a-button>
                </a-popconfirm>
              </AccessControl>
              <a-input-search
                v-model:value="search"
                :placeholder="$t('common.search')"
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
              <template v-if="column.key === 'meta'">
                {{ formatMeta(record.meta) }}
              </template>
              <template v-if="column.key === 'permission'">
                {{ formatPermission(record.permission) }}
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
                  <AccessControl
                    :codes="['admin.rule.edit', 'all']"
                    type="code"
                  >
                    <a-button
                      size="small"
                      type="primary"
                      @click="openDialog(record, 'edit')"
                    >
                      <EditOutlined /> </a-button
                  ></AccessControl>
                  <AccessControl
                    :codes="['admin.rule.delete', 'all']"
                    type="code"
                  >
                    <a-popconfirm
                      :title="$t('common.confirm_delete')"
                      :ok-text="$t('common.yes')"
                      :cancel-text="$t('common.no')"
                      @confirm="deleteItem(record.id)"
                    >
                      <a-button size="small" type="primary" danger>
                        <template #icon>
                          <DeleteOutlined />
                        </template>
                      </a-button>
                    </a-popconfirm>
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
      :width="800"
    >
      <a-form
        :model="currentItem"
        :label-col="labelCol"
        :wrapper-col="wrapperCol"
        ref="form"
        :rules="formRules"
      >
        <a-form-item :label="$t('admin.rule.id')" v-if="mode !== 'add'">
          <a-input v-model:value="currentItem.id" :disabled="true" />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.rule_type')"
          :rules="formRules.rule_type"
        >
          <a-select
            v-model:value="currentItem.rule_type"
            :disabled="mode === 'view'"
          >
            <a-select-option value="menu">{{
              $t("admin.rule.menu")
            }}</a-select-option>
            <a-select-option value="action">{{
              $t("admin.rule.action")
            }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.parent_id')"
          name="parent_id"
          :rules="formRules.parent_id"
        >
          <a-input
            v-model:value="currentItem.parent_id"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.name')"
          name="name"
          :rules="formRules.name"
        >
          <a-input
            v-model:value="currentItem.name"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.path')"
          name="path"
          :rules="formRules.path"
        >
          <a-input
            v-model:value="currentItem.path"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.component')"
          name="component"
          :rules="formRules.component"
        >
          <a-input
            v-model:value="currentItem.component"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.redirect')"
          name="redirect"
          :rules="formRules.redirect"
        >
          <a-input
            v-model:value="currentItem.redirect"
            :disabled="mode === 'view'"
          />
        </a-form-item>
        <a-form-item
          :label="$t('admin.rule.meta')"
          name="meta"
          :rules="formRules.meta"
        >
          <!-- Title field as hidden input with label display -->
          <div v-if="getMetaItem('title')" class="meta-field-display">
            <div class="field-row">
              <span class="field-label">{{ $t("admin.rule.meta_title") }}</span>
              <a-input
                :value="getMetaItem('title')?.value"
                @update:value="updateMetaItem('title', $event)"
                :placeholder="$t('admin.rule.meta_title_placeholder')"
                :disabled="mode === 'view'"
                style="flex: 1;"
              />
            </div>
          </div>

          <!-- Icon field as hidden input with label display -->
          <div v-if="getMetaItem('icon')" class="meta-field-display">
            <div class="field-row">
              <span class="field-label">{{ $t("admin.rule.meta_icon") }}</span>
              <div class="icon-field-wrapper">
                <a-input
                  :value="getMetaItem('icon')?.value"
                  @update:value="updateMetaItem('icon', $event)"
                  :placeholder="$t('admin.rule.meta_icon_placeholder')"
                  :disabled="mode === 'view'"
                  style="margin-right: 8px; flex: 1;"
                />
                <div class="icon-preview-wrapper" v-if="getMetaItem('icon')?.value">
                  <div class="selected-icon-preview">
                    <Icon :icon="getMetaItem('icon')?.value || ''" width="20" height="20" />
                  </div>
                </div>
                <a-button
                  type="primary"
                  @click="openIconDialog(metaItems.findIndex(item => item.key === 'icon'))"
                  :disabled="mode === 'view'"
                >
                  {{ $t("common.select") }}
                </a-button>
              </div>
            </div>
          </div>

          <!-- Other meta fields -->
          <div
            v-for="(item, index) in metaItems.filter(item => item.key !== 'title' && item.key !== 'icon')"
            :key="index"
            class="meta-item"
          >
            <a-input
              v-model:value="item.key"
              placeholder="Key"
              :disabled="mode === 'view'"
            />
            <a-input
              v-model:value="item.value"
              placeholder="Value"
              :disabled="mode === 'view'"
              style="margin-right: 8px;"
            />
            <a-button
              type="link"
              @click="removeMetaItem(index)"
              :disabled="mode === 'view'"
            >
              <CloseOutlined />
            </a-button>
          </div>
          <a-button
            type="dashed"
            @click="addMetaItem"
            :disabled="mode === 'view'"
          >
            {{ $t("common.add") }}
          </a-button>
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.permission')"
          name="permission"
          :rules="formRules.permission"
        >
          <a-checkbox-group v-model:value="permissionItems">
            <a-space>
              <a-checkbox value="add">{{ $t("common.add") }}</a-checkbox>
              <a-checkbox value="edit">{{ $t("common.edit") }}</a-checkbox>
              <a-checkbox value="delete">{{ $t("common.delete") }}</a-checkbox>
              <a-checkbox value="view">{{ $t("common.view") }}</a-checkbox>
            </a-space>
          </a-checkbox-group>
          <div
            v-for="(item, index) in otherPermissionItems"
            :key="index"
            class="permission-item"
          >
            <a-space>
              <a-input
                v-model:value="item.value"
                placeholder="Other Permission"
                :disabled="mode === 'view'" />

              <a-button
                type="link"
                @click="removeOtherPermissionItem(index)"
                :disabled="mode === 'view'"
              >
                <CloseOutlined /> </a-button
            ></a-space>
          </div>
          <a-space>
            <a-button
              type="dashed"
              @click="addOtherPermissionItem"
              :disabled="mode === 'view'"
            >
              {{ $t("common.add") }}
            </a-button></a-space
          >
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.menu_display_type')"
          :rules="formRules.menu_display_type"
        >
          <a-select
            v-model:value="currentItem.menu_display_type"
            :disabled="mode === 'view'"
          >
            <a-select-option value="ajax">{{
              $t("admin.rule.ajax")
            }}</a-select-option>
            <a-select-option value="addtabs">{{
              $t("admin.rule.addtabs")
            }}</a-select-option>
            <a-select-option value="blank">{{
              $t("admin.rule.blank")
            }}</a-select-option>
            <a-select-option value="dialog">{{
              $t("admin.rule.dialog")
            }}</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.model_name')"
          name="model_name"
          :rules="formRules.model_name"
        >
          <a-input
            v-model:value="currentItem.model_name"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item
          :label="$t('admin.rule.weigh')"
          name="weigh"
          :rules="formRules.weigh"
        >
          <a-input
            v-model:value="currentItem.weigh"
            :disabled="mode === 'view'"
          />
        </a-form-item>

        <a-form-item :label="$t('admin.rule.status')" :rules="formRules.status">
          <a-select
            v-model:value="currentItem.status"
            :disabled="mode === 'view'"
          >
            <a-select-option value="normal">{{
              $t("common.normal")
            }}</a-select-option>
            <a-select-option value="hidden">{{
              $t("common.hidden")
            }}</a-select-option>
            <a-select-option value="deleted">{{
              $t("common.deleted")
            }}</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Icon Selector Dialog -->
    <a-modal
      v-model:open="isIconDialogVisible"
      title="选择图标"
      @cancel="closeIconDialog"
      :maskClosable="false"
      :width="600"
      :zIndex="2000"
    >
      <div class="icon-selector">
        <a-input-search
          v-model:value="iconSearch"
          placeholder="搜索图标..."
          @search="filterIcons"
          style="margin-bottom: 16px;"
        />
        <div class="icon-grid">
          <div
            v-for="icon in filteredIcons"
            :key="icon"
            class="icon-item"
            :class="{ selected: selectedIcon === icon }"
            @click="selectIcon(icon)"
          >
            <div class="icon-preview">
              <Icon :icon="icon" width="24" height="24" />
            </div>
            <div class="icon-name">{{ icon }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <a-button @click="closeIconDialog">取消</a-button>
        <a-button type="primary" @click="confirmIconSelection">确定</a-button>
      </template>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, computed, onMounted, type UnwrapRef, h } from "vue";
import { AccessControl } from "@/_core/access";
import {
  fetchAdminRuleItems,
  saveAdminRule,
  deleteAdminRule,
} from "@/api/admin/admin_rule";
import { $t } from "@/locales";
import {
  FileAddOutlined,
  DeleteOutlined,
  EyeOutlined,
  EditOutlined,
  CloseOutlined,
} from "@ant-design/icons-vue";
import { Icon } from "@iconify/vue";
import { message, type FormInstance } from "ant-design-vue";
const form = ref<FormInstance | null>(null);

interface AdminRule {
  id: number;
  rule_type: string;
  parent_id: number | null;
  name: string;
  path: string;
  component: string | null;
  redirect: string | null;
  meta: any | null;
  permission: any | null;
  menu_display_type: string | null;
  model_name: string;
  weigh: number;
  status: string;
}

const currentItem: UnwrapRef<AdminRule> = reactive({
  id: 0,
  rule_type: "menu",
  parent_id: 0,
  name: "",
  path: "",
  component: "",
  redirect: "",
  meta: null,
  permission: null,
  menu_display_type: "ajax",
  model_name: "",
  weigh: 0,
  status: "normal",
});

const isDialogVisible = ref(false);
const confirmLoading = ref(false);
const dialogTitle = computed(() => {
  switch (mode.value) {
    case "view":
      return $t("common.view_item");
    case "add":
      return $t("common.add_item");
    case "edit":
      return $t("common.edit_item");
    default:
      return "";
  }
});

const mode = ref<"add" | "edit" | "view">("add"); // Mode for Add, Edit, View

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
const items = ref<any[]>([]);
const pagination = ref({ current: 1, pageSize: 1000, total: 0 });
const search = ref("");

const labelCol = { style: { width: "150px" } };
const wrapperCol = { span: 14 };

// Icon selector related variables
const isIconDialogVisible = ref(false);
const iconSearch = ref("");
const selectedIcon = ref("");
const currentIconIndex = ref(-1);

// Common MDI icons
const mdiIcons = [
  "mdi:account",
  "mdi:account-group",
  "mdi:account-group-outline",
  "mdi:home",
  "mdi:home-outline",
  "mdi:cog",
  "mdi:cog-outline",
  "mdi:settings",
  "mdi:settings-outline",
  "mdi:menu",
  "mdi:menu-open",
  "mdi:view-dashboard",
  "mdi:view-dashboard-outline",
  "mdi:chart-bar",
  "mdi:chart-bar-stacked",
  "mdi:chart-line",
  "mdi:chart-pie",
  "mdi:file",
  "mdi:file-outline",
  "mdi:folder",
  "mdi:folder-outline",
  "mdi:plus",
  "mdi:plus-box",
  "mdi:minus",
  "mdi:close",
  "mdi:check",
  "mdi:edit",
  "mdi:delete",
  "mdi:eye",
  "mdi:eye-outline",
  "mdi:lock",
  "mdi:lock-outline",
  "mdi:key",
  "mdi:key-outline",
  "mdi:bell",
  "mdi:bell-outline",
  "mdi:message",
  "mdi:message-outline",
  "mdi:email",
  "mdi:email-outline",
  "mdi:phone",
  "mdi:phone-outline",
  "mdi:calendar",
  "mdi:calendar-outline",
  "mdi:clock",
  "mdi:clock-outline",
  "mdi:star",
  "mdi:star-outline",
  "mdi:heart",
  "mdi:heart-outline",
  "mdi:thumb-up",
  "mdi:thumb-up-outline",
  "mdi:thumb-down",
  "mdi:thumb-down-outline",
  "mdi:share",
  "mdi:share-outline",
  "mdi:download",
  "mdi:upload",
  "mdi:refresh",
  "mdi:sync",
  "mdi:search",
  "mdi:filter",
  "mdi:sort",
  "mdi:arrow-up",
  "mdi:arrow-down",
  "mdi:arrow-left",
  "mdi:arrow-right",
  "mdi:chevron-up",
  "mdi:chevron-down",
  "mdi:chevron-left",
  "mdi:chevron-right",
  "mdi:information",
  "mdi:information-outline",
  "mdi:alert",
  "mdi:alert-outline",
  "mdi:warning",
  "mdi:warning-outline",
  "mdi:error",
  "mdi:error-outline",
  "mdi:success",
  "mdi:success-outline",
  "mdi:help",
  "mdi:help-outline",
  "mdi:question-mark",
  "mdi:question-mark-outline",
  "mdi:play",
  "mdi:pause",
  "mdi:stop",
  "mdi:skip-next",
  "mdi:skip-previous",
  "mdi:volume-high",
  "mdi:volume-medium",
  "mdi:volume-low",
  "mdi:volume-off",
  "mdi:image",
  "mdi:image-outline",
  "mdi:video",
  "mdi:video-outline",
  "mdi:music",
  "mdi:music-outline",
  "mdi:book",
  "mdi:book-outline",
  "mdi:bookmark",
  "mdi:bookmark-outline",
  "mdi:tag",
  "mdi:tag-outline",
  "mdi:link",
  "mdi:link-off",
  "mdi:attachment",
  "mdi:cloud",
  "mdi:cloud-outline",
  "mdi:cloud-upload",
  "mdi:cloud-download",
  "mdi:database",
  "mdi:database-outline",
  "mdi:server",
  "mdi:server-outline",
  "mdi:network",
  "mdi:network-outline",
  "mdi:wifi",
  "mdi:wifi-off",
  "mdi:bluetooth",
  "mdi:bluetooth-off",
  "mdi:battery",
  "mdi:battery-outline",
  "mdi:power",
  "mdi:power-off",
  "mdi:flash",
  "mdi:flash-outline",
  "mdi:lightbulb",
  "mdi:lightbulb-outline",
  "mdi:weather-sunny",
  "mdi:weather-night",
  "mdi:weather-rainy",
  "mdi:weather-snowy",
  "mdi:weather-windy",
  "mdi:weather-cloudy",
  "mdi:map",
  "mdi:map-outline",
  "mdi:location",
  "mdi:location-outline",
  "mdi:navigation",
  "mdi:compass",
  "mdi:compass-outline",
  "mdi:car",
  "mdi:car-outline",
  "mdi:bus",
  "mdi:bus-outline",
  "mdi:train",
  "mdi:train-outline",
  "mdi:airplane",
  "mdi:airplane-outline",
  "mdi:ship",
  "mdi:ship-outline",
  "mdi:bicycle",
  "mdi:bicycle-outline",
  "mdi:walk",
  "mdi:run",
  "mdi:swim",
  "mdi:golf",
  "mdi:ski",
  "mdi:snowboard",
  "mdi:gamepad",
  "mdi:gamepad-outline",
  "mdi:controller",
  "mdi:controller-outline",
  "mdi:headphones",
  "mdi:headphones-outline",
  "mdi:microphone",
  "mdi:microphone-outline",
  "mdi:speaker",
  "mdi:speaker-outline",
  "mdi:tv",
  "mdi:tv-outline",
  "mdi:monitor",
  "mdi:monitor-outline",
  "mdi:laptop",
  "mdi:laptop-outline",
  "mdi:tablet",
  "mdi:tablet-outline",
  "mdi:cellphone",
  "mdi:cellphone-outline",
  "mdi:desktop-mac",
  "mdi:desktop-mac-outline",
  "mdi:desktop-windows",
  "mdi:desktop-windows-outline",
  "mdi:apple",
  "mdi:microsoft",
  "mdi:google",
  "mdi:facebook",
  "mdi:twitter",
  "mdi:instagram",
  "mdi:linkedin",
  "mdi:youtube",
  "mdi:github",
  "mdi:git",
  "mdi:bitbucket",
  "mdi:docker",
  "mdi:kubernetes",
  "mdi:aws",
  "mdi:azure",
  "mdi:google-cloud",
  "mdi:digital-ocean",
  "mdi:heroku",
  "mdi:linux",
  "mdi:windows",
  "mdi:apple-ios",
  "mdi:android",
  "mdi:web",
  "mdi:web-outline",
  "mdi:language",
  "mdi:language-outline",
  "mdi:translate",
  "mdi:translate-outline",
  "mdi:code",
  "mdi:code-outline",
  "mdi:xml",
  "mdi:json",
  "mdi:markdown",
  "mdi:html",
  "mdi:css",
  "mdi:javascript",
  "mdi:typescript",
  "mdi:python",
  "mdi:java",
  "mdi:php",
  "mdi:ruby",
  "mdi:go",
  "mdi:rust",
  "mdi:swift",
  "mdi:kotlin",
  "mdi:scala",
  "mdi:c",
  "mdi:c-plus-plus",
  "mdi:c-sharp",
  "mdi:vue",
  "mdi:vue-outline",
  "mdi:react",
  "mdi:angular",
  "mdi:svelte",
  "mdi:ember",
  "mdi:backbone",
  "mdi:jquery",
  "mdi:bootstrap",
  "mdi:tailwind",
  "mdi:material-design",
  "mdi:ant-design",
  "mdi:element",
  "mdi:vuetify",
  "mdi:quasar",
  "mdi:nuxt",
  "mdi:next",
  "mdi:gatsby",
  "mdi:grid",
  "mdi:grid-outline",
  "mdi:list",
  "mdi:list-outline",
  "mdi:table",
  "mdi:table-outline",
  "mdi:card",
  "mdi:card-outline",
  "mdi:form",
  "mdi:form-outline",
  "mdi:input",
  "mdi:input-outline",
  "mdi:button",
  "mdi:button-outline",
  "mdi:select",
  "mdi:select-outline",
  "mdi:checkbox",
  "mdi:checkbox-outline",
  "mdi:radio",
  "mdi:radio-outline",
  "mdi:switch",
  "mdi:switch-outline",
  "mdi:slider",
  "mdi:slider-outline",
  "mdi:progress",
  "mdi:progress-outline",
  "mdi:spinner",
  "mdi:loading",
  "mdi:loading-outline",
  "mdi:refresh",
  "mdi:refresh-outline",
  "mdi:reload",
  "mdi:reload-outline",
  "mdi:undo",
  "mdi:redo",
  "mdi:save",
  "mdi:save-outline",
  "mdi:download",
  "mdi:download-outline",
  "mdi:upload",
  "mdi:upload-outline",
  "mdi:print",
  "mdi:print-outline",
  "mdi:scan",
  "mdi:scan-outline",
  "mdi:qrcode",
  "mdi:qrcode-outline",
  "mdi:barcode",
  "mdi:barcode-outline",
  "mdi:camera",
  "mdi:camera-outline",
  "mdi:image",
  "mdi:image-outline",
  "mdi:video",
  "mdi:video-outline",
  "mdi:music",
  "mdi:music-outline",
  "mdi:file",
  "mdi:file-outline",
  "mdi:folder",
  "mdi:folder-outline",
  "mdi:archive",
  "mdi:archive-outline",
  "mdi:zip",
  "mdi:zip-outline",
  "mdi:pdf",
  "mdi:pdf-outline",
  "mdi:word",
  "mdi:word-outline",
  "mdi:excel",
  "mdi:excel-outline",
  "mdi:powerpoint",
  "mdi:powerpoint-outline",
  "mdi:text",
  "mdi:text-outline",
  "mdi:document",
  "mdi:document-outline",
  "mdi:note",
  "mdi:note-outline",
  "mdi:sticky-note",
  "mdi:sticky-note-outline",
  "mdi:clipboard",
  "mdi:clipboard-outline",
  "mdi:cut",
  "mdi:copy",
  "mdi:paste",
  "mdi:scissors",
  "mdi:scissors-outline",
  "mdi:brush",
  "mdi:brush-outline",
  "mdi:pen",
  "mdi:pen-outline",
  "mdi:pencil",
  "mdi:pencil-outline",
  "mdi:eraser",
  "mdi:eraser-outline",
  "mdi:highlighter",
  "mdi:highlighter-outline",
  "mdi:marker",
  "mdi:marker-outline",
  "mdi:paint",
  "mdi:paint-outline",
  "mdi:palette",
  "mdi:palette-outline",
  "mdi:color",
  "mdi:color-outline",
  "mdi:gradient",
  "mdi:gradient-outline",
  "mdi:shadow",
  "mdi:shadow-outline",
  "mdi:opacity",
  "mdi:opacity-outline",
  "mdi:blur",
  "mdi:blur-outline",
  "mdi:filter",
  "mdi:filter-outline",
  "mdi:crop",
  "mdi:crop-outline",
  "mdi:rotate",
  "mdi:rotate-outline",
  "mdi:flip",
  "mdi:flip-outline",
  "mdi:scale",
  "mdi:scale-outline",
  "mdi:transform",
  "mdi:transform-outline",
  "mdi:layers",
  "mdi:layers-outline",
  "mdi:stack",
  "mdi:stack-outline",
  "mdi:group",
  "mdi:group-outline",
  "mdi:ungroup",
  "mdi:ungroup-outline",
  "mdi:align",
  "mdi:align-outline",
  "mdi:distribute",
  "mdi:distribute-outline",
  "mdi:arrange",
  "mdi:arrange-outline",
  "mdi:order",
  "mdi:order-outline",
  "mdi:sort",
  "mdi:sort-outline",
  "mdi:filter",
  "mdi:filter-outline",
  "mdi:search",
  "mdi:search-outline",
  "mdi:find",
  "mdi:find-outline",
  "mdi:replace",
  "mdi:replace-outline",
  "mdi:zoom-in",
  "mdi:zoom-out",
  "mdi:fit",
  "mdi:fit-outline",
  "mdi:fullscreen",
  "mdi:fullscreen-outline",
  "mdi:minimize",
  "mdi:minimize-outline",
  "mdi:maximize",
  "mdi:maximize-outline",
  "mdi:close",
  "mdi:close-outline",
  "mdi:check",
  "mdi:check-outline",
  "mdi:plus",
  "mdi:plus-outline",
  "mdi:minus",
  "mdi:minus-outline",
  "mdi:multiply",
  "mdi:multiply-outline",
  "mdi:divide",
  "mdi:divide-outline",
  "mdi:equal",
  "mdi:equal-outline",
  "mdi:not-equal",
  "mdi:not-equal-outline",
  "mdi:greater-than",
  "mdi:greater-than-outline",
  "mdi:less-than",
  "mdi:less-than-outline",
  "mdi:greater-than-or-equal",
  "mdi:greater-than-or-equal-outline",
  "mdi:less-than-or-equal",
  "mdi:less-than-or-equal-outline",
  "mdi:and",
  "mdi:and-outline",
  "mdi:or",
  "mdi:or-outline",
  "mdi:not",
  "mdi:not-outline",
  "mdi:xor",
  "mdi:xor-outline",
  "mdi:if",
  "mdi:if-outline",
  "mdi:else",
  "mdi:else-outline",
  "mdi:switch",
  "mdi:switch-outline",
  "mdi:case",
  "mdi:case-outline",
  "mdi:default",
  "mdi:default-outline",
  "mdi:break",
  "mdi:break-outline",
  "mdi:continue",
  "mdi:continue-outline",
  "mdi:return",
  "mdi:return-outline",
  "mdi:throw",
  "mdi:throw-outline",
  "mdi:try",
  "mdi:try-outline",
];

// Icon selector functions
const filteredIcons = computed(() => {
  if (!iconSearch.value) {
    return mdiIcons;
  }
  return mdiIcons.filter(icon => 
    icon.toLowerCase().includes(iconSearch.value.toLowerCase())
  );
});

const openIconDialog = (index: number) => {
  currentIconIndex.value = index;
  selectedIcon.value = metaItems.value[index]?.value || "";
  isIconDialogVisible.value = true;
};

const closeIconDialog = () => {
  isIconDialogVisible.value = false;
  selectedIcon.value = "";
  currentIconIndex.value = -1;
};

const selectIcon = (icon: string) => {
  selectedIcon.value = icon;
};

const confirmIconSelection = () => {
  if (currentIconIndex.value >= 0 && selectedIcon.value) {
    metaItems.value[currentIconIndex.value].value = selectedIcon.value;
  }
  closeIconDialog();
};

const filterIcons = () => {
  // Search is handled by computed property
};

const getIconPreview = (icon: string) => {
  // Return a simple text representation for the icon
  const iconName = icon.replace('mdi:', '');
  return iconName.split('-').map(word => 
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(' ');
};

// Validation rules
const formRules = reactive({
  rule_type: [{ required: true, message: $t("common.field_required") }],
  parent_id: [{ required: false }],
  name: [{ required: true, message: $t("common.field_required") }],
  path: [{ required: true, message: $t("common.field_required") }],
  component: [{ required: true, message: $t("common.field_required") }],
  redirect: [{ required: false }],
  meta: [{ required: false }],
  permission: [{ required: false }],
  menu_display_type: [{ required: false }],
  model_name: [{ required: true, message: $t("common.field_required") }],
  weigh: [{ required: true, message: $t("common.field_required") }],
  status: [{ required: true, message: $t("common.field_required") }],
});

const columns = computed(() => [
  { key: "tree", align: "center" },

  { 
    title: $t("admin.rule.id"), 
    dataIndex: "id", 
    align: "center", 
    key: "id",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  {
    title: $t("admin.rule.rule_type"),
    dataIndex: "rule_type",
    key: "rule_type",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  {
    title: $t("admin.rule.parent_id"),
    dataIndex: "parent_id",
    key: "parent_id",
    width: 90,
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  { 
    title: $t("admin.rule.name"), 
    dataIndex: "name", 
    key: "name",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  { 
    title: $t("admin.rule.path"), 
    dataIndex: "path", 
    key: "path",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  // { title: $t('admin.rule.component'), dataIndex: 'component', key: 'component' },

  // { title: $t("admin.rule.redirect"), dataIndex: "redirect", key: "redirect" },

  // {
  //   title: $t("admin.rule.meta"),
  //   dataIndex: "meta",
  //   key: "meta",
  //   customRender: ({ text }: { text: any }) => formatMeta(text),
  // },

  {
    title: $t("admin.rule.permission"),
    dataIndex: "permission",
    key: "permission",
    customRender: ({ text }: { text: any }) => formatPermission(text),
  },

  {
    title: $t("admin.rule.menu_display_type"),
    dataIndex: "menu_display_type",
    key: "menu_display_type",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  {
    title: $t("admin.rule.model_name"),
    dataIndex: "model_name",
    key: "model_name",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  { 
    title: $t("admin.rule.weigh"), 
    dataIndex: "weigh", 
    key: "weigh",
    sorter: true,
    sortDirections: ['ascend', 'descend'],
  },

  { 
    title: $t("admin.rule.status"), 
    dataIndex: "status", 
    key: "status",
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

// 格式化 meta 显示
const formatMeta = (meta: any) => {
  if (!meta) return "-";
  return Object.entries(meta)
    .map(([key, value]) => `${key}: ${value}`)
    .join(", ");
};

// 格式化 permission 显示
const formatPermission = (permission: any) => {
  if (!permission) return "-";
  return Object.keys(permission).join(", ");
};

const onSelectChange = (selectedRowIds: Key[]) => {
  state.selectedRowIds = selectedRowIds;
};

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

const openDialog = (item: any, modeText: "add" | "edit" | "view") => {
  mode.value = modeText;
  if (mode.value === "add") {
    resetCurrentItem();
  } else {
    Object.assign(currentItem, item);

    // 初始化 metaItems
    if (currentItem.meta) {
      try {
        metaItems.value = Object.keys(currentItem.meta).map((key) => ({
          key,
          value: currentItem.meta[key],
        }));
      } catch (e) {
        console.error("Failed to parse meta:", e);
        metaItems.value = [];
      }
    } else {
      metaItems.value = [];
    }

    // 初始化 permissionItems 和 otherPermissionItems
    if (currentItem.permission) {
      try {
        permissionItems.value = Object.keys(currentItem.permission).filter(
          (p) => ["add", "edit", "delete", "view"].includes(p)
        );
        otherPermissionItems.value = Object.keys(currentItem.permission)
          .filter((p) => !["add", "edit", "delete", "view"].includes(p))
          .map((p) => ({ value: p }));
      } catch (e) {
        console.error("Failed to parse permission:", e);
        permissionItems.value = [];
        otherPermissionItems.value = [];
      }
    } else {
      permissionItems.value = [];
      otherPermissionItems.value = [];
    }
  }
  isDialogVisible.value = true;
};

const resetCurrentItem = () => {
  Object.assign(currentItem, {
    id: 0,
    rule_type: "menu",
    parent_id: 0,
    name: "",
    path: "",
    component: "",
    redirect: "",
    meta: { title: "", icon: "" }, // 默认添加 title 和 icon
    permission: null,
    menu_display_type: "ajax",
    model_name: "",
    weigh: 0,
    status: "normal",
  });
  metaItems.value = [
    { key: "title", value: "" },
    { key: "icon", value: "" }
  ]; // 默认添加 title 和 icon
  permissionItems.value = [];
  otherPermissionItems.value = [];
};

const closeDialog = () => {
  isDialogVisible.value = false;
};

const onSubmit = async () => {
  confirmLoading.value = true;
  try {
    // 将 metaItems 转换为字典对象
    const meta = metaItems.value.reduce((acc, item) => {
      if (item.key && item.value) {
        acc[item.key] = item.value;
      }
      return acc;
    }, {} as Record<string, string>);
    currentItem.meta = meta;

    // 将 permissionItems 和 otherPermissionItems 合并为字典对象
    const permission = [
      ...permissionItems.value,
      ...otherPermissionItems.value.map((item) => item.value),
    ].reduce((acc, p) => {
      acc[p] = true; // 或者根据需要设置其他值
      return acc;
    }, {} as Record<string, boolean>);
    currentItem.permission = permission;

    // Validate the form before submission
    await form.value?.validate();
    if (mode.value === "add") {
      await saveItem();
      resetCurrentItem();
    } else if (mode.value === "edit") {
      await updateItem();
    }
    closeDialog();
  } catch (error) {
    // Handle validation errors
    console.error($t("common.form_validation_failed"), error);
  } finally {
    confirmLoading.value = false;
    fetchItems();
  }
};

const saveItem = async () => {
  try {
    await saveAdminRule({
      rule_type: currentItem.rule_type,
      parent_id: currentItem.parent_id,
      name: currentItem.name,
      path: currentItem.path,
      component: currentItem.component,
      redirect: currentItem.redirect,
      meta: currentItem.meta,
      permission: currentItem.permission,
      menu_display_type: currentItem.menu_display_type,
      model_name: currentItem.model_name,
      weigh: currentItem.weigh,
      status: currentItem.status,
    });
    message.success($t("common.save_success"));
  } catch (error) {
    console.error($t("common.save_item_failed"), error);
  }
};

const updateItem = async () => {
  try {
    await saveAdminRule({
      id: currentItem.id,
      rule_type: currentItem.rule_type,
      parent_id: currentItem.parent_id,
      name: currentItem.name,
      path: currentItem.path,
      component: currentItem.component,
      redirect: currentItem.redirect,
      meta: currentItem.meta,
      permission: currentItem.permission,
      menu_display_type: currentItem.menu_display_type,
      model_name: currentItem.model_name,
      weigh: currentItem.weigh,
      status: currentItem.status,
    });
    message.success($t("common.update_success"));
  } catch (error) {
    console.error($t("common.update_item_failed"), error);
  }
};

const deleteItem = async (id: number) => {
  try {
    await deleteAdminRule(id);
    message.success($t("common.delete_success"));
    fetchItems();
  } catch (error) {
    console.error($t("common.delete_item_failed"), error);
  }
};

const deleteSelectedItems = async () => {
  try {
    state.loading = true;
    const ids = Array.from(state.selectedRowIds);
    for (const id of ids) {
      const numericId = typeof id === "string" ? parseInt(id) : id;
      await deleteAdminRule(numericId);
    }
    fetchItems();
    state.selectedRowIds = [];
    message.success($t("common.delete_selected_success"));
  } catch (error) {
    console.error($t("common.delete_selected_failed"), error);
  } finally {
    state.loading = false;
  }
};
function addPrefixForTree(treeData: any[], level = 0) {
  return treeData.map((node, index) => {
    const isLast = index === treeData.length - 1;
    let prefix = "";
    if (level > 0) {
      const space = "&nbsp;&nbsp;&nbsp;&nbsp;".repeat(level - 1);
      prefix = space + (isLast ? "└ " : "├ ");
    }
    // 给 name 加上前缀
    node.name = prefix + node.name;
    // 如果有 children，则递归处理
    if (node.children && node.children.length > 0) {
      node.children = addPrefixForTree(node.children, level + 1);
    }
    return node;
  });
}

// 然后直接在 fetchItems 中：

const fetchItems = async () => {
  loading.value = true;
  try {
    const response = await fetchAdminRuleItems({
      page: pagination.value.current,
      perPage: pagination.value.pageSize,
      search: search.value,
      orderby: orderby.value,
    });
    // items.value = response.items;
    items.value = addPrefixForTree(response.items);
    pagination.value.total = response.total;
  } catch (error) {
    console.error($t("common.fetch_items_error"), error);
  } finally {
    loading.value = false;
  }
};

const metaItems = ref<{ key: string; value: string }[]>([]);
const addMetaItem = () => {
  metaItems.value.push({ key: "", value: "" });
};
const removeMetaItem = (index: number) => {
  metaItems.value.splice(index, 1);
};

const permissionItems = ref<string[]>([]);
const otherPermissionItems = ref<{ value: string }[]>([]);
const addOtherPermissionItem = () => {
  otherPermissionItems.value.push({ value: "" });
};
const removeOtherPermissionItem = (index: number) => {
  otherPermissionItems.value.splice(index, 1);
};

// Helper functions for meta items
const getMetaItem = (key: string) => {
  return metaItems.value.find(item => item.key === key);
};

const updateMetaItem = (key: string, value: string) => {
  const item = metaItems.value.find(item => item.key === key);
  if (item) {
    item.value = value;
  }
};

onMounted(() => {
  fetchItems();
});
</script>

<style scoped>
.meta-item,
.permission-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.meta-item .ant-input,
.permission-item .ant-input {
  margin-right: 8px;
}

/* Meta field display styles */
.meta-field-display {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background: #fafafa;
}

.field-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.field-label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
  min-width: 60px;
  text-align: right;
}

.icon-field-wrapper {
  display: flex;
  align-items: center;
  flex: 1;
  gap: 8px;
}

/* Icon selector styles */
.icon-selector {
  max-height: 400px;
  overflow-y: auto;
}

.icon-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  padding: 8px;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #fff;
}

.icon-item:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.1);
}

.icon-item.selected {
  border-color: #1890ff;
  background-color: #f0f8ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
}

.icon-preview {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 4px;
  background: #fafafa;
}

.icon-text {
  font-size: 12px;
  color: #666;
  text-align: center;
  line-height: 1.2;
}

.icon-name {
  font-size: 11px;
  color: #999;
  text-align: center;
  word-break: break-all;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Selected icon preview styles */
.icon-preview-wrapper {
  display: flex;
  align-items: center;
}

.selected-icon-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: #fafafa;
  margin-right: 8px;
  transition: all 0.2s ease;
}

.selected-icon-preview:hover {
  border-color: #1890ff;
  box-shadow: 0 2px 4px rgba(24, 144, 255, 0.1);
}
</style>
