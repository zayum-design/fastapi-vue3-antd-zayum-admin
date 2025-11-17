<script lang="ts" setup>
import type { EchartsUIType } from '@/plugins/echarts';
import { onMounted, ref } from 'vue';
import { EchartsUI, useEcharts } from '@/plugins/echarts';
import { fetchAnalyticsSources } from '@/api/admin/analytics';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(true);

// 获取来源数据
const loadSourceData = async () => {
  try {
    loading.value = true;
    const response = await fetchAnalyticsSources();
    
    // 处理响应数据
    let sourceData: Array<{name: string, value: number}> = [];
    if (response && Array.isArray(response)) {
      // 如果返回的是数组格式，直接使用
      sourceData = response.map((item: any) => ({
        name: item.source,
        value: item.count
      }));
    } else if (response) {
      // 如果返回的是对象格式，尝试获取数据
      const sourcesData = (response as any).actionSources || (response as any).userSources || [];
      if (sourcesData.length > 0) {
        sourceData = sourcesData.map((source: any) => ({
          name: source.source,
          value: source.count
        }));
      }
    }

    // 如果没有数据，使用默认数据
    if (sourceData.length === 0) {
      sourceData = [
        { name: '搜索引擎', value: 1048 },
        { name: '直接访问', value: 735 },
        { name: '邮件营销', value: 580 },
        { name: '联盟广告', value: 484 },
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
          data: sourceData,
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
          name: '访问来源',
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
    console.error('Failed to fetch source data:', error);
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
            { name: '搜索引擎', value: 1048 },
            { name: '直接访问', value: 735 },
            { name: '邮件营销', value: 580 },
            { name: '联盟广告', value: 484 },
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
          name: '访问来源',
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
  loadSourceData();
});
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
