<template>
  <div class="hedges-page">
    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span class="title">套保明细查询</span>
          <div class="filters">
            <el-input v-model="stockCode" placeholder="股票代码" clearable style="width:120px" />
            <el-input-number v-model="year" :min="2000" :max="2030" placeholder="年份" style="width:130px" />
            <el-input-number v-model="catalogId" :min="1" placeholder="商品类目ID" style="width:150px" controls-position="right" />
            <el-button type="primary" @click="search"><el-icon><Search /></el-icon> 查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="items" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="stock_code" label="股票代码" width="90" />
        <el-table-column prop="announcement_id" label="公告ID" width="140" show-overflow-tooltip />
        <el-table-column prop="catalog_id" label="商品类目" width="90" />
        <el-table-column prop="biz_year" label="年份" width="70" />
        <el-table-column prop="hedging_limit" label="套保额度(万元)" width="130" />
        <el-table-column prop="hedging_direction" label="套保方向" width="100" />
        <el-table-column prop="hedging_term" label="期限" width="80" />
        <el-table-column prop="business_desc" label="业务描述" min-width="200" show-overflow-tooltip />
      </el-table>

      <el-pagination
        v-model:current-page="page"
        :page-size="size"
        :total="total"
        layout="total, prev, pager, next"
        style="margin-top:16px;justify-content:flex-end"
        @current-change="search"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'
const stockCode = ref('')
const year = ref(null)
const catalogId = ref(null)
const page = ref(1)
const size = 20
const total = ref(0)
const items = ref([])
const loading = ref(false)

const search = async () => {
  loading.value = true
  try {
    const params = { page: page.value, size }
    if (stockCode.value) params.stock_code = stockCode.value
    if (year.value) params.year = year.value
    if (catalogId.value) params.catalog_id = catalogId.value
    const res = await axios.get(`${API}/hedges`, { params })
    items.value = res.data.items
    total.value = res.data.total
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(search)
</script>

<style scoped>
.hedges-page { max-width: 1200px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.filters { display: flex; gap: 10px; align-items: center; }
</style>
