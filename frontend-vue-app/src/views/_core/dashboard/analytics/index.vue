<script lang="ts" setup>
import { ref, onMounted } from 'vue';
import type { AnalysisOverviewItem } from '../workspace/components';
import type { TabOption } from '@/_core/types';

import {
  AnalysisChartCard,
  AnalysisChartsTabs,
  AnalysisOverview,
} from '@/views/_core/dashboard/analytics/analysis';
import {
  UsersIcon,
  UserPlusIcon,
  LoginIcon,
  ActivityIcon,
} from '@/_core/ui/icons';

import AnalyticsTrends from './analytics-trends.vue';
import AnalyticsVisitsData from './analytics-visits-data.vue';
import AnalyticsVisitsSales from './analytics-visits-sales.vue';
import AnalyticsVisits from './analytics-visits.vue';

import { fetchAnalyticsOverview } from '@/api/admin/analytics';

const overviewItems = ref<AnalysisOverviewItem[]>([]);
const loading = ref(true);

const chartTabs: TabOption[] = [
  {
    label: '流量趋势',
    value: 'trends',
  },
  {
    label: '月活跃量',
    value: 'visits',
  },
];

// Fetch analytics data from backend
const loadAnalyticsData = async () => {
  try {
    loading.value = true;
    const response = await fetchAnalyticsOverview();
    
    // Handle different response formats
    let data;
    if (Array.isArray(response)) {
      // If backend returns array format: [{ "totalValue": 3, "value": 3 }, ...]
      data = response;
    } else {
      // If backend returns object format: { totalUsers: 3, newUsers: 1, ... }
      data = [
        { totalValue: response.totalUsers || 0, value: response.totalUsers || 0 },
        { totalValue: response.newUsers || 0, value: response.newUsers || 0 },
        { totalValue: response.activeUsers || 0, value: response.activeUsers || 0 },
        { totalValue: response.totalVisits || 0, value: response.totalVisits || 0 },
      ];
    }
    
    // Map backend data to frontend format
    overviewItems.value = [
      {
        description: '总用户数量',
        icon: UsersIcon,
        title: '总用户',
        totalTitle: '总用户',
        totalValue: data[0]?.totalValue || 0,
        value: data[0]?.value || 0,
      },
      {
        description: '今日注册用户数量',
        icon: UserPlusIcon,
        title: '今日注册',
        totalTitle: '今日注册',
        totalValue: data[1]?.totalValue || 0,
        value: data[1]?.value || 0,
      },
      {
        description: '今日登录用户数量',
        icon: LoginIcon,
        title: '今日登录',
        totalTitle: '今日登录',
        totalValue: data[2]?.totalValue || 0,
        value: data[2]?.value || 0,
      },
      {
        description: '近7日活跃用户数量',
        icon: ActivityIcon,
        title: '近7日活跃',
        totalTitle: '近7日活跃',
        totalValue: data[3]?.totalValue || 0,
        value: data[3]?.value || 0,
      },
    ];
  } catch (error) {
    console.error('Failed to fetch analytics data:', error);
    // Fallback to default data if API fails
    overviewItems.value = [
      {
        description: '总用户数量',
        icon: UsersIcon,
        title: '总用户',
        totalTitle: '总用户',
        totalValue: 0,
        value: 0,
      },
      {
        description: '今日注册用户数量',
        icon: UserPlusIcon,
        title: '今日注册',
        totalTitle: '今日注册',
        totalValue: 0,
        value: 0,
      },
      {
        description: '今日登录用户数量',
        icon: LoginIcon,
        title: '今日登录',
        totalTitle: '今日登录',
        totalValue: 120_000,
        value: 8000,
      },
      {
        description: '近7日活跃用户数量',
        icon: ActivityIcon,
        title: '近7日活跃',
        totalTitle: '近7日活跃',
        totalValue: 0,
        value: 0,
      },
    ];
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadAnalyticsData();
});
</script>

<template>
  <div class="p-5">
    <AnalysisOverview :items="overviewItems" />
    <AnalysisChartsTabs :tabs="chartTabs" class="mt-5">
      <template #trends>
        <AnalyticsTrends />
      </template>
      <template #visits>
        <AnalyticsVisits />
      </template>
    </AnalysisChartsTabs>

    <div class="mt-5 w-full md:flex">
      <AnalysisChartCard class="mt-5 md:mr-4 md:mt-0 md:w-1/2" title="客户端">
        <AnalyticsVisitsData />
      </AnalysisChartCard>
      <AnalysisChartCard class="mt-5 md:mt-0 md:w-1/2" title="地区分步">
        <AnalyticsVisitsSales />
      </AnalysisChartCard>
    </div>
  </div>
</template>
