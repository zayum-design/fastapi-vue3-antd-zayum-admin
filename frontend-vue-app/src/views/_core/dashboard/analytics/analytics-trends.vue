<script lang="ts" setup>
import type { EchartsUIType } from '@/plugins/echarts';

import { onMounted, ref } from 'vue';

import { EchartsUI, useEcharts } from '@/plugins/echarts';
import { fetchAnalyticsTrends } from '@/api/admin/analytics';
import type { AnalyticsTrendsData } from '@/_core/types/api';

const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);

const loadTrendsData = async () => {
  try {
    // 调用API获取趋势数据
    console.log('开始调用API...');
    const trendsData: AnalyticsTrendsData = await fetchAnalyticsTrends(30);
    console.log('API响应:', trendsData);
    
    // 提取用户注册趋势和访问趋势数据
    const userTrends = trendsData?.userTrends || [];
    const visitTrends = trendsData?.visitTrends || [];
    
    console.log('userTrends:', userTrends);
    console.log('visitTrends:', visitTrends);
    
    // 如果API返回的数据为空，直接使用fallback数据
    if (userTrends.length === 0 || visitTrends.length === 0) {
      console.log('API返回数据为空，使用fallback数据');
      throw new Error('API返回数据为空');
    }
    
    // 生成日期标签（月/日格式）
    const dates = userTrends.map((item) => {
      const date = new Date(item.date);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    });
    
    // 提取注册用户数数据
    const registeredUsersData = userTrends.map((item) => item.count);
    
    // 提取用户登录数据（使用访问趋势作为用户登录数据的代理）
    const userLoginData = visitTrends.map((item) => item.count);
      
    renderEcharts({
      grid: {
        bottom: 0,
        containLabel: true,
        left: '1%',
        right: '1%',
        top: '2 %',
      },
      series: [
        {
          areaStyle: {},
          data: registeredUsersData,
          itemStyle: {
            color: '#5ab1ef',
          },
          smooth: true,
          type: 'line',
          name: '注册用户数',
        },
        {
          areaStyle: {},
          data: userLoginData,
          itemStyle: {
            color: '#019680',
          },
          smooth: true,
          type: 'line',
          name: '用户登录数',
        },
      ],
      tooltip: {
        axisPointer: {
          lineStyle: {
            color: '#019680',
            width: 1,
          },
        },
        trigger: 'axis',
      },
      legend: {
        data: ['注册用户数', '用户登录数'],
      },
      xAxis: {
        axisTick: {
          show: false,
        },
        boundaryGap: false,
        data: dates,
        splitLine: {
          lineStyle: {
            type: 'solid',
            width: 1,
          },
          show: true,
        },
        type: 'category',
      },
      yAxis: [
        {
          axisTick: {
            show: false,
          },
          splitArea: {
            show: true,
          },
          splitNumber: 4,
          type: 'value',
        },
      ],
    });
 
  } catch (error) {
    console.error('Failed to load trends data:', error);
    // Fallback to static data if API fails
  }
};

onMounted(() => {
  loadTrendsData();
});
</script>

<template>
  <EchartsUI ref="chartRef" />
</template>
