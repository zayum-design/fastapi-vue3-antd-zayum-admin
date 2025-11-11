<template>
  <BaseBreadcrumb :title="pageData.title" :breadcrumbs="breadcrumbs" />

  <v-row justify="center">
    <v-col cols="12" md="12">
      <v-card flat>
        <v-card-title class="d-flex align-center pe-2">
          <v-btn color="primary" @click="addDialog = true">
            <template #prepend>
              <FileAddOutlined :style="{ fontSize: '17px' }" color="success" />
            </template>
            {{ $t("Add") }}
          </v-btn>
          <v-btn
            color="error"
            @click="deleteAllDialog = true"
            class="ml-4"
            :disabled="selected.length === 0"
          >
            <template #prepend>
              <DeleteOutlined :style="{ fontSize: '17px' }" color="success" />
            </template>
            {{ $t("Delete selected") }}
          </v-btn>

          <v-spacer></v-spacer>

          <v-text-field
            v-model="search"
            density="compact"
            label="Search"
            prepend-inner-icon="mdi-magnify"
            variant="solo-filled"
            flat
            hide-details
            single-line
          ></v-text-field>
        </v-card-title>

        <v-divider></v-divider>

        <v-data-table
          v-model="selected"
          :headers="headers"
          :items="items"
          :items-per-page="itemsPerPage"
          :server-items-length="totalItems"
          @update:options="loadItems"
          item-key="id"
          loading-text="Loading... Please wait"
          :loading="loading"
          show-select
          class="custom-data-table"
          fixed-header
        >
          <template #item.actions="{ item, index }">
            <div class="text-end" style="width: 120px">
              <v-btn
                icon
                class="rounded-sm"
                variant="flat"
                size="small"
                @click="openDialog(index, 'view')"
              >
                <EyeOutlined :style="{ fontSize: '17px' }" />
              </v-btn>

              <v-btn
                icon
                class="rounded-sm"
                variant="flat"
                size="small"
                @click="openDialog(index, 'edit')"
              >
                <EditOutlined :style="{ fontSize: '17px' }" />
              </v-btn>

              <v-btn
                class="text-error rounded-sm"
                icon
                variant="flat"
                size="small"
                @click="openDialog(index, 'delete')"
              >
                <DeleteOutlined :style="{ fontSize: '17px' }" />
              </v-btn>
            </div>
          </template>

          <template #no-data>
            <v-alert type="info" class="ma-4" v-if="!loading">{{
              $t("No data available")
            }}</v-alert>
          </template>
        </v-data-table>
      </v-card>
    </v-col>
  </v-row>

  <!-- Add New Item Dialog -->
  <v-dialog v-model="addDialog" max-width="600">
    <v-card>
      <v-card-title>{{ $t('Add New') }}</v-card-title>
      <v-card-text>
        <v-row>
          {{ fields_forms }}
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="addDialog = false">{{ $t("Cancel") }}</v-btn>
        <v-btn color="primary" @click="addNewItem">{{ $t("Save") }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- View Item Details Dialog -->
  <v-dialog v-model="viewDialog" max-width="600">
    <v-card>
      <v-card-title>{{ $t('Details') }}</v-card-title>
      <v-card-text>
        <v-row>
          {{ view_fields }}
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="viewDialog = false">{{
          $t("Close")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Edit Item Dialog -->
  <v-dialog v-model="editDialog" max-width="600">
    <v-card>
      <v-card-title>{{ $t('Edit') }}</v-card-title>
      <v-card-text>
        <v-row>
          {{ fields_forms_edit }}
        </v-row>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="editDialog = false">{{ $t("Cancel") }}</v-btn>
        <v-btn color="primary" @click="updateItem">{{ $t("Save") }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Delete Confirmation Dialog -->
  <v-dialog v-model="deleteDialog" max-width="400">
    <v-card>
      <v-card-title class="headline">{{ $t("Are you sure?") }}</v-card-title>
      <v-card-text>{{
        $t("Do you really want to delete this item?")
      }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="deleteDialog = false">{{ $t("Cancel") }}</v-btn>
        <v-btn color="error" @click="deleteItem">{{ $t("Delete") }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Delete All Confirmation Dialog -->
  <v-dialog v-model="deleteAllDialog" max-width="400">
    <v-card>
      <v-card-title class="headline">{{ $t("Are you sure?") }}</v-card-title>
      <v-card-text>{{
        $t("Do you really want to delete all selected items?")
      }}</v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="deleteAllDialog = false">{{ $t("Cancel") }}</v-btn>
        <v-btn color="error" @click="confirmDeleteAll">{{
          $t("Delete")
        }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Error Alert Dialog -->
  <v-dialog v-model="showError" max-width="500">
    <v-card>
      <v-card-title class="headline">{{ $t("Error") }}</v-card-title>
      <v-card-text>
        <div
          v-for="(msg, index) in errorMessages"
          :key="index"
          style="margin-bottom: 8px"
        >
          {{ msg }}
        </div>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="showError = false">{{ $t("OK") }}</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Deleting Overlay -->
  <v-overlay v-model="deleting" class="align-center justify-center">
    <v-progress-circular
      :value="deleteProgress"
      color="teal"
      size="100"
      width="15"
      indeterminate
    >
      {{ deleteProgress }}%
    </v-progress-circular>
  </v-overlay>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from "vue";
import BaseBreadcrumb from "@/components/shared/BaseBreadcrumb.vue";
import {
  FileAddOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from "@ant-design/icons-vue";
import { useRouter } from "vue-router";
import { fetchWrapper } from '@/utils/helpers/fetch-wrapper';
import type { ApiResponse, SuccessResponse, ErrorResponse } from '@/types/api';

import { useI18n } from "vue-i18n";
import moment from 'moment-timezone';
import { convertToTitleCase } from "@/utils/utils";

// Define the time zone
const TIME_ZONE = import.meta.env.VITE_TIME_ZONE || 'Asia/Shanghai';

const router = useRouter();
const { t } = useI18n();

const pageData = ref({ title: t('{{ class_name }} List') });
const breadcrumbs = ref([{ title: t('{{ class_name }}'), disabled: true, href: "#" }]);

// Search keyword
const search = ref("");

// Loading state
const loading = ref(false);

// Current page and items per page
const page = ref(1);
const itemsPerPage = ref(10);
const totalItems = ref(0);

// Sort
const sortKey = ref('id');
const sortOrder = ref('decc');

// Compute total page count based on totalItems and itemsPerPage
const pageCount = computed(() => {
  return Math.ceil(totalItems.value / itemsPerPage.value);
});

// Define enums if any
{{ enums_text }}

// Define {{ class_name }} interface
interface {{ class_name }} {
  {{ interface_fields }}
}

interface {{ class_name }}New {
  {{ interface_fields_new }}
}

// {{ class_name }} data
const items = ref<{{ class_name }}[]>([]);
const selected = ref<number[]>([]); // Store selected item IDs

// Dialog controls
const editDialog = ref(false);
const deleteDialog = ref(false);
const viewDialog = ref(false);
const addDialog = ref(false);
const deleteAllDialog = ref(false);

// Error handling
const errorMessages = ref<string[]>([]);
const showError = ref(false);

// Selected item details and new item information
const selectedItem = reactive<{{ class_name }}>({
  {{ selected_item_fields }}
});

const newItem = reactive<{{ class_name }}New>({
  {{ new_item_fields }}
});

// Define headers for the data table
const headers = [
  {{ headers }}
  {
    title: t('Actions'),
    value: 'actions',
    sortable: false,
    align: 'end' as const,
    width: '150px',
    headerProps: {
      style: 'position: sticky; right: 0; z-index: 2;',
    },
    cellProps: {
      style: 'position: sticky; right: 0; z-index: 1;',
    },
  },
];


const titlesString = headers
  .map(h => {
    const content = h.title || h.text
    // 关键：想输出 "a":"a" 格式，就这么写
    return `"${content}":"${content}"`
  })
  .join(', ')
console.log("===========", titlesString)

// Metadata for fields to determine rendering type
const fieldsMeta: Partial<Record<keyof {{ class_name }}, { type: string, options: string[], labels: Record<string, string> }>> = {
  {{ fields_meta }}
  // Add more fields with enum types if necessary
};

 
// Compute item keys as (keyof {{ class_name }})[]
const itemKeys = computed<(keyof {{ class_name }})[]>(() => Object.keys(newItem) as (keyof {{ class_name }})[]);

// Fetch item list from API
async function fetchItems() {
let url = `/{{ table_name.replace('sys_', '') }}/list?page=${page.value}&per_page=${itemsPerPage.value}&orderby=${sortKey.value}_${sortOrder.value}`;
if (search.value) {
  url += `&search=${encodeURIComponent(search.value)}`;
}
  loading.value = true;
  try {
    const data = await fetchWrapper.get<ApiResponse>(url);
    if (data.code === 1) {
      const successData = data as SuccessResponse;
      // Assuming SuccessResponse has a 'data' property with 'items' and 'total'
      items.value = (successData.data.items as {{ class_name }}[]).map((item: {{ class_name }}) => ({
        {{ mapped_fields }}
      }));

      totalItems.value = successData.data.total;
    } else {
      const errorData = data as ErrorResponse;
      if (errorData.data?.errors) {
        errorMessages.value = errorData.data.errors.map(err => err.message);
      } else {
        errorMessages.value = [data.msg || t("Failed to fetch items.")];
      }
      showError.value = true;
    }
  } catch (error: any) {
    console.error("Error fetching items:", error);
    errorMessages.value = [error.message || t("An error occurred while fetching items")];
    showError.value = true;
  } finally {
    loading.value = false;
  }
}

// Watch for changes in search to reset page and fetch items
watch(
  search,
  () => {
    page.value = 1;
    fetchItems();
  }
);

// Watch for changes in page to fetch items
watch(page, () => {
  fetchItems();
});

// Watch for changes in itemsPerPage to reset page and fetch items
watch(itemsPerPage, () => {
  page.value = 1;
  fetchItems();
});

// Watch for changes in selected items
watch(selected, () => {
  console.log("Selected items changed", selected.value);
});

// Load items when table options change
async function loadItems(options: any) {
  console.log("Loading items with options", options);
  if (Array.isArray(options.sortBy) && options.sortBy.length > 0) {
    const sortRule = options.sortBy[0];
    sortKey.value = sortRule.key; 
    sortOrder.value = sortRule.order; 
  } else {
    // 如果 sortBy 不存在或为空，可以选择设置默认值或忽略这次更新
    console.log("No valid sorting options provided.");
  }
  page.value = options.page;
  itemsPerPage.value = options.itemsPerPage;
  fetchItems();
}

// Open dialog based on type (edit, delete, view)
const openDialog = (index: number, type: "edit" | "delete" | "view") => {
  const item = items.value[index];
  Object.assign(selectedItem, {
    {{ selected_item_assignment }}
  });

  if (type === "edit") {
    editDialog.value = true;
  } else if (type === "delete") {
    deleteDialog.value = true;
  } else if (type === "view") {
    viewDialog.value = true;
  }
};

// Delete selected items with progress indication
const deleting = ref(false);
const deleteProgress = ref(0);

const deleteSelectedItemsWithProgress = async () => {
  deleting.value = true;
  deleteProgress.value = 0;
  const total = selected.value.length;

  for (let i = 0; i < total; i++) {
    const itemId = selected.value[i];
    try {
      const data = await fetchWrapper.delete<ApiResponse>(`/{{ table_name.replace('sys_', '') }}/delete/${itemId}`);
      if (data.code === 1) {
        const idx = items.value.findIndex((u) => u.id === itemId);
        if (idx > -1) {
          items.value.splice(idx, 1);
        }
      } else {
        const errorData = data as ErrorResponse;
        if (errorData.data?.errors) {
          errorMessages.value = errorData.data.errors.map(err => err.message);
        } else {
          errorMessages.value = [data.msg || t('failedToDeleteItem', { itemId })];
        }
        showError.value = true;
      }
    } catch (error: any) {
      console.error(`Error deleting item ID: ${itemId}`, error);
      errorMessages.value = [error.message || t('An error occurred while deleting the item')];
      showError.value = true;
    }
    deleteProgress.value = Math.round(((i + 1) / total) * 100);
    console.log("Delete progress:", deleteProgress.value);
  }

  deleting.value = false;
  selected.value = [];
  fetchItems();
};

// Delete a single item
const deleteItem = async () => {
  try {
    const data = await fetchWrapper.delete<ApiResponse>(`/{{ table_name.replace('sys_', '') }}/delete/${selectedItem.id}`);
    if (data.code === 1) {
      fetchItems();
    } else {
      const errorData = data as ErrorResponse;
      if (errorData.data?.errors) {
        errorMessages.value = errorData.data.errors.map(err => err.message);
      } else {
        errorMessages.value = [data.msg || t("failedToDeleteItem", { itemId: selectedItem.id })];
      }
      showError.value = true;
    }
  } catch (error: any) {
    console.error(`Error deleting item ID: ${selectedItem.id}`, error);
    errorMessages.value = [error.message || t("An error occurred while deleting the item")];
    showError.value = true;
  }
  deleteDialog.value = false;
};

// Add a new item
const addNewItem = async () => {
  console.log("Adding new item", newItem);
  {{ validation_checks }}
  try {
    const payload = {
      {{ payload_fields_new }}
    };
    const data = await fetchWrapper.post<ApiResponse>(`/{{ table_name.replace('sys_', '') }}/create`, payload);
    if (data.code === 1) {
      addDialog.value = false;
      fetchItems();
      // Reset newItem to default values
      Object.assign(newItem, {
        {{ reset_fields }}
      });
    } else {
      const errorData = data as ErrorResponse;
      if (errorData.data?.errors) {
        errorMessages.value = errorData.data.errors.map(err => err.message);
      } else {
        errorMessages.value = [data.msg || t("Failed to create item")];
      }
      showError.value = true;
    }
  } catch (error: any) {
    console.error("Error creating item:", error);
    errorMessages.value = [error.message || t("An error occurred while creating the item")];
    showError.value = true;
  }
};

// Update an existing item
const updateItem = async () => {
  try {
    const payload = {
      {{ payload_fields_edit }}
    };
    const data = await fetchWrapper.put<ApiResponse>(`/{{ table_name.replace('sys_', '') }}/update/${selectedItem.id}`, payload);
    if (data.code === 1) {
      editDialog.value = false;
      fetchItems();
    } else {
      const errorData = data as ErrorResponse;
      if (errorData.data?.errors) {
        errorMessages.value = errorData.data.errors.map(err => err.message);
      } else {
        errorMessages.value = [data.msg || t('failedToUpdateItem', { itemId: selectedItem.id })];
      }
      showError.value = true;
    }
  } catch (error: any) {
    console.error(`Error updating item ID: ${selectedItem.id}`, error);
    errorMessages.value = [error.message || t("An error occurred while updating the item")];
    showError.value = true;
  }
};

// Navigate to item detail page
function goToDetail(id: number) {
  router.push(`/{{ table_name.replace('sys_', '') }}/${id}`);
}

// Confirm and delete all selected items
const confirmDeleteAll = () => {
  deleteAllDialog.value = false;
  deleteSelectedItemsWithProgress();
};
</script>

<style scoped>
.rounded-sm {
  border-radius: 4px; /* Adjust as needed */
}
</style>
