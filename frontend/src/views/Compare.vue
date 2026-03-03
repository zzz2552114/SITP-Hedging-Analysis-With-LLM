<template>
  <div class="compare-page">
    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span class="title">套保渗透率统计</span>
          <div class="filters">
            <el-input-number v-model="year" :min="2000" :max="2030" style="width:130px" />
            <el-input v-model="businessCore" placeholder="核心业务关键词，如：铜加工" clearable style="width:220px" />
            <el-button type="primary" @click="search" :loading="loading"><el-icon><DataAnalysis /></el-icon> 分析比对</el-button>
          </div>
        </div>
      </template>

      <!-- 统计概览 -->
      <div v-if="result" class="overview">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="业务年度" :value="result.biz_year" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="涉及公司总数" :value="result.total_companies" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="开展套保公司数" :value="result.hedging_companies">
              <template #suffix>/ {{ result.total_companies }}</template>
            </el-statistic>
          </el-col>
          <el-col :span="6">
            <el-statistic title="套保渗透率">
              <template #default>
                <span class="rate" :class="{ high: result.penetration_rate > 0.5 }">
                  {{ (result.penetration_rate * 100).toFixed(1) }}%
                </span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
      </div>

      <!-- 公司列表 -->
      <el-table v-if="result" :data="result.companies" stripe border style="width:100%;margin-top:20px">
        <el-table-column prop="stock_code" label="股票代码" width="100" />
        <el-table-column prop="company_short_name" label="公司简称" width="120" />
        <el-table-column prop="company_name" label="公司全称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="has_hedging" label="是否套保" width="100">
          <template #default="{ row }">
            <el-tag :type="row.has_hedging ? 'success' : 'danger'" size="small">
              {{ row.has_hedging ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="year_hedging_limit" label="年套保额度(万元)" width="150" />
        <el-table-column prop="hedging_commodity_list" label="涉及商品" min-width="180">
          <template #default="{ row }">
            <el-tag v-for="c in row.hedging_commodity_list" :key="c" size="small" style="margin:2px" type="info">{{ c }}</el-tag>
            <span v-if="!row.hedging_commodity_list?.length" style="color:#c0c4cc">—</span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="searched && !result" description="未找到符合条件的数据" />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'
const year = ref(2024)
const businessCore = ref('')
const loading = ref(false)
const result = ref(null)
const searched = ref(false)

const search = async () => {
  if (!businessCore.value) return ElMessage.warning('请输入核心业务关键词')
  loading.value = true
  searched.value = true
  try {
    const res = await axios.get(`${API}/compare/hedging_by_business`, {
      params: { year: year.value, business_core: businessCore.value }
    })
    result.value = res.data.total_companies > 0 ? res.data : null
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '查询失败')
    result.value = null
  } finally { loading.value = false }
}
</script>

<style scoped>
.compare-page { max-width: 1200px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.filters { display: flex; gap: 10px; align-items: center; }
.overview { background: #f5f7fa; border-radius: 8px; padding: 24px; margin-top: 4px; }
.rate { font-size: 28px; font-weight: 700; color: #909399; }
.rate.high { color: #67c23a; }
</style>
