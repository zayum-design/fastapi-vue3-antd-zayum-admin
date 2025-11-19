<script lang="ts" setup>
import type { EchartsUIType } from '@/plugins/echarts';
import { onMounted, ref } from 'vue';
import { EchartsUI, useEcharts } from '@/plugins/echarts';
import { fetchAnalyticsRegions } from '@/api/admin/analytics';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(true);

// 获取地区分布数据
const loadRegionData = async () => {
  try {
    loading.value = true;
    const response = await fetchAnalyticsRegions();
    
    // 处理响应数据
    let regionData: Array<{name: string, value: number}> = [];
    if (response && Array.isArray(response)) {
      // 如果返回的是数组格式，直接使用
      regionData = response.map((item: any) => ({
        name: item.region,
        value: item.count || item.visits
      }));
    }

    // 如果没有数据，使用默认数据
    if (regionData.length === 0) {
      regionData = [];
    }

    renderEcharts({
      series: [
        {
          animationDelay() {
            return Math.random() * 400;
          },
          animationEasing: 'exponentialInOut',
          animationType: 'scale',
          center: ['50%', '50%'],
          color: ['#5ab1ef', '#b6a2de', '#67e0e3', '#2ec7c9', '#ffb980', '#d87a80', '#8d98b3', '#e5cf0d', '#97b552', '#95706d'],
          data: regionData.sort((a, b) => {
            return a.value - b.value;
          }),
          name: '用户地区分布',
          radius: '80%',
          roseType: 'radius',
          type: 'pie',
        },
      ],
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
    });
  } catch (error) {
    console.error('Failed to fetch region data:', error);
    // 出错时使用默认数据
    renderEcharts({
      series: [],
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
    });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadRegionData();
});
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
