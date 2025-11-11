<script lang="ts" setup>
import type { EchartsUIType } from '@/plugins/echarts';

import { onMounted, ref } from 'vue';

import { EchartsUI, useEcharts } from '@/plugins/echarts';
import { fetchMonthlyLogins } from '@/api/admin/analytics';
import type { MonthlyLoginData } from '@/_core/types/api';

 
const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

    const loadMonthlyLoginData = async () => {
      try {
        const monthlyData = await fetchMonthlyLogins(12);
        
        if (!monthlyData || !Array.isArray(monthlyData)) {
          console.error('API返回数据格式错误，使用默认数据');
          renderDefaultChart();
          return;
        }
        
        // 提取月份和登录人数数据
        const monthLabels = monthlyData.map((item: MonthlyLoginData) => {
          const [year, month] = item.month.split('-');
          return `${year}年${parseInt(month)}月`;
        });
        
        const loginCounts = monthlyData.map((item: MonthlyLoginData) => item.count);
        
        // 计算Y轴最大值，留出一些空间
        const maxCount = Math.max(...loginCounts);
        const yAxisMax = Math.ceil(maxCount * 1.2);
        
        renderEcharts({
          grid: {
            bottom: 0,
            containLabel: true,
            left: '1%',
            right: '1%',
            top: '2%',
          },
          series: [
            {
              barMaxWidth: 80,
              data: loginCounts,
              type: 'bar',
              itemStyle: {
                color: '#4f69fd',
              },
            },
          ],
          tooltip: {
            axisPointer: {
              lineStyle: {
                color: '#4f69fd',
                width: 1,
              },
            },
            trigger: 'axis',
            formatter: (params: any) => {
              const data = params[0];
              return `${data.name}<br/>登录人数: ${data.value}`;
            },
          },
          xAxis: {
            data: monthLabels,
            type: 'category',
            axisLabel: {
              interval: 0,
              rotate: 0,
            },
          },
          yAxis: {
            max: yAxisMax,
            splitNumber: 4,
            type: 'value',
            name: '登录人数',
          },
        });
      } catch (error) {
        console.error('Failed to load monthly login data:', error);
        // 如果API调用失败，使用默认数据
        renderDefaultChart();
      }
    };

const renderDefaultChart = () => {
  renderEcharts({
    grid: {
      bottom: 0,
      containLabel: true,
      left: '1%',
      right: '1%',
      top: '2%',
    },
    series: [
      {
        barMaxWidth: 80,
        data: [
          3000, 2000, 3333, 5000, 3200, 4200, 3200, 2100, 3000, 5100, 6000,
          3200,
        ],
        type: 'bar',
        itemStyle: {
          color: '#4f69fd',
        },
      },
    ],
    tooltip: {
      axisPointer: {
        lineStyle: {
          color: '#4f69fd',
          width: 1,
        },
      },
      trigger: 'axis',
      formatter: (params: any) => {
        const data = params[0];
        return `${data.name}<br/>登录人数: ${data.value}`;
      },
    },
    xAxis: {
      data: Array.from({ length: 12 }).map((_item, index) => `${index + 1}月`),
      type: 'category',
    },
    yAxis: {
      max: 8000,
      splitNumber: 4,
      type: 'value',
      name: '登录人数',
    },
  });
};

onMounted(() => {
  loadMonthlyLoginData();
});
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
