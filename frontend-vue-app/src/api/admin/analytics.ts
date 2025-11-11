// src/api/admin/analytics.ts
import { requestClient } from '@/api/request';
import { 
  type MonthlyLoginData,
  type AnalyticsOverviewData,
  type AnalyticsTrendsData,
  type AnalyticsVisitsData,
  type AnalyticsSourcesData,
  type AnalyticsRegionsData
} from '@/_core/types/api';

// Fetch analytics overview data
export async function fetchAnalyticsOverview() {
  return requestClient.get<AnalyticsOverviewData>('/admin/analytics/overview');
}

// Fetch analytics trends data
export async function fetchAnalyticsTrends(days: number = 30) {
  return requestClient.get<AnalyticsTrendsData>('/admin/analytics/trends', {
    params: { days }
  });
}

// Fetch analytics visits data
export async function fetchAnalyticsVisits(period: string = 'month') {
  return requestClient.get<AnalyticsVisitsData[]>('/admin/analytics/visits', {
    params: { period }
  });
}

// Fetch analytics sources data
export async function fetchAnalyticsSources() {
  return requestClient.get<AnalyticsSourcesData[]>('/admin/analytics/sources');
}

// Fetch analytics regions data
export async function fetchAnalyticsRegions() {
  return requestClient.get<AnalyticsRegionsData[]>('/admin/analytics/regions');
}

// Fetch monthly login statistics
export async function fetchMonthlyLogins(months: number = 12) {
  return requestClient.get<MonthlyLoginData[]>('/admin/analytics/monthly-logins', {
    params: { months }
  });
}
