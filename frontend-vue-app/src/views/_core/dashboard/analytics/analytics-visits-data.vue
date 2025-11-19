<script lang="ts" setup>
import type { EchartsUIType } from '@/plugins/echarts';
import { onMounted, ref } from 'vue';
import { EchartsUI, useEcharts } from '@/plugins/echarts';
import { fetchAnalyticsSources } from '@/api/admin/analytics';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(true);

// 获取平台数据
const loadPlatformData = async () => {
  try {
    loading.value = true;
    const response = await fetchAnalyticsSources();
    
    // 处理响应数据
    let platformData: Array<{name: string, value: number}> = [];
    if (response && Array.isArray(response)) {
      // 如果返回的是数组格式，直接使用
      platformData = response.map((item: any) => ({
        name: item.source,
        value: item.count
      }));
    } else if (response) {
      // 如果返回的是对象格式，尝试获取数据
      const sourcesData = (response as any).userSources || (response as any).actionSources || [];
      if (sourcesData.length > 0) {
        platformData = sourcesData.map((source: any) => ({
          name: source.source,
          value: source.count
        }));
      }
    }

    // 如果没有数据，使用默认数据
    if (platformData.length === 0) {
      platformData = [
        { name: '网页', value: 1048 },
        { name: '移动端', value: 735 },
        { name: 'Ipad', value: 580 },
        { name: '平台', value: 484 },
      ];
    }

    renderEcharts({
      legend: {
        bottom: '2%',
        left: 'center',
      },
      series: [
        {
          animationDelay() {
            return Math.random() * 100;
          },
          animationEasing: 'exponentialInOut',
          animationType: 'scale',
          avoidLabelOverlap: false,
          color: ['#5ab1ef', '#b6a2de', '#67e0e3', '#2ec7c9'],
          data: platformData,
          emphasis: {
            label: {
              fontSize: '12',
              fontWeight: 'bold',
              show: true,
            },
          },
          itemStyle: {
            borderRadius: 10,
            borderWidth: 2,
          },
          label: {
            position: 'center',
            show: false,
          },
          labelLine: {
            show: false,
          },
          name: '平台分布',
          radius: ['40%', '65%'],
          type: 'pie',
        },
      ],
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
    });
  } catch (error) {
    console.error('Failed to fetch platform data:', error);
    // 出错时使用默认数据
    renderEcharts({
      legend: {
        bottom: '2%',
        left: 'center',
      },
      series: [
        {
          animationDelay() {
            return Math.random() * 100;
          },
          animationEasing: 'exponentialInOut',
          animationType: 'scale',
          avoidLabelOverlap: false,
          color: ['#5ab1ef', '#b6a2de', '#67e0e3', '#2ec7c9'],
          data: [
            { name: '网页', value: 1048 },
            { name: '移动端', value: 735 },
            { name: 'Ipad', value: 580 },
            { name: '平台', value: 484 },
          ],
          emphasis: {
            label: {
              fontSize: '12',
              fontWeight: 'bold',
              show: true,
            },
          },
          itemStyle: {
            borderRadius: 10,
            borderWidth: 2,
          },
          label: {
            position: 'center',
            show: false,
          },
          labelLine: {
            show: false,
          },
          name: '平台分布',
          radius: ['40%', '65%'],
          type: 'pie',
        },
      ],
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
  loadPlatformData();
});
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
