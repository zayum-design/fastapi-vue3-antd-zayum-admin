<script lang="ts" setup>
import type { EchartsUIType } from '@/plugins/echarts';
import { onMounted, ref } from 'vue';
import { EchartsUI, useEcharts } from '@/plugins/echarts';
import { fetchAnalyticsSources } from '@/api/admin/analytics';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
const loading = ref(true);

// 获取客户端数据
const loadClientData = async () => {
  try {
    loading.value = true;
    const response = await fetchAnalyticsSources();
    
    // 处理响应数据
    let clientData: Array<{name: string, value: number}> = [];
    if (response && Array.isArray(response)) {
      // 如果返回的是数组格式，直接使用
      clientData = response.map((item: any) => ({
        name: item.source,
        value: item.count
      }));
    } else if (response) {
      // 如果返回的是对象格式，尝试获取数据
      const sourcesData = (response as any).userSources || (response as any).actionSources || [];
      if (sourcesData.length > 0) {
        clientData = sourcesData.map((source: any) => ({
          name: source.source,
          value: source.count
        }));
      }
    }

    // 如果没有数据，使用默认数据
    if (clientData.length === 0) {
      clientData = [
        { name: '网页', value: 1048 },
        { name: '移动端', value: 735 },
        { name: 'Ipad', value: 580 },
        { name: '客户端', value: 484 },
        { name: '第三方', value: 300 },
        { name: '其它', value: 200 },
      ];
    }

    // 准备雷达图数据
    const radarIndicators = clientData.map((item: {name: string, value: number}) => ({ name: item.name }));
    const radarValues = clientData.map((item: {name: string, value: number}) => item.value);

    renderEcharts({
      legend: {
        bottom: 0,
        data: ['客户端分布'],
      },
      radar: {
        indicator: radarIndicators,
        radius: '60%',
        splitNumber: 8,
      },
      series: [
        {
          areaStyle: {
            opacity: 0.3,
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,.2)',
            shadowOffsetX: 0,
            shadowOffsetY: 10,
          },
          data: [
            {
              itemStyle: {
                color: '#5ab1ef',
              },
              name: '客户端分布',
              value: radarValues,
            },
          ],
          itemStyle: {
            borderRadius: 10,
            borderWidth: 2,
          },
          symbolSize: 0,
          type: 'radar',
        },
      ],
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c}'
      },
    });
  } catch (error) {
    console.error('Failed to fetch client data:', error);
    // 出错时使用默认数据
    renderEcharts({
      legend: {
        bottom: 0,
        data: ['客户端分布'],
      },
      radar: {
        indicator: [
          { name: '网页' },
          { name: '移动端' },
          { name: 'Ipad' },
          { name: '客户端' },
          { name: '第三方' },
          { name: '其它' },
        ],
        radius: '60%',
        splitNumber: 8,
      },
      series: [
        {
          areaStyle: {
            opacity: 0.3,
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,.2)',
            shadowOffsetX: 0,
            shadowOffsetY: 10,
          },
          data: [
            {
              itemStyle: {
                color: '#5ab1ef',
              },
              name: '客户端分布',
              value: [1048, 735, 580, 484, 300, 200],
            },
          ],
          itemStyle: {
            borderRadius: 10,
            borderWidth: 2,
          },
          symbolSize: 0,
          type: 'radar',
        },
      ],
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c}'
      },
    });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadClientData();
});
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
