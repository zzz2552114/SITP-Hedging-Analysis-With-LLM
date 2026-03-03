<template>
  <div class="announcements-page">
    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span class="title">公告管理</span>
          <div class="filters">
            <el-input v-model="stockCode" placeholder="股票代码" clearable style="width:120px" />
            <el-input-number v-model="year" :min="2000" :max="2030" placeholder="年份" style="width:130px" />
            <el-select v-model="parseStatus" placeholder="解析状态" clearable style="width:130px">
              <el-option label="全部" :value="null" />
              <el-option label="未解析" :value="0" />
              <el-option label="成功" :value="1" />
              <el-option label="失败" :value="2" />
            </el-select>
            <el-button type="primary" @click="search"><el-icon><Search /></el-icon> 查询</el-button>
          </div>
        </div>
      </template>

      <el-table :data="items" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="announcement_id" label="公告ID" width="140" show-overflow-tooltip />
        <el-table-column prop="stock_code" label="股票代码" width="90" />
        <el-table-column prop="announcement_title" label="公告标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="publish_date" label="发布日期" width="110" />
        <el-table-column prop="biz_year" label="业务年份" width="90" />
        <el-table-column prop="parse_status" label="解析状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.parse_status === 1 ? 'success' : row.parse_status === 2 ? 'danger' : 'info'" size="small">
              {{ row.parse_status === 0 ? '未解析' : row.parse_status === 1 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="viewPdf(row.announcement_id)">
              <el-icon><View /></el-icon> PDF
            </el-button>
          </template>
        </el-table-column>
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
const parseStatus = ref(null)
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
    if (parseStatus.value !== null) params.parse_status = parseStatus.value
    const res = await axios.get(`${API}/announcements`, { params })
    items.value = res.data.items
    total.value = res.data.total
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const viewPdf = (id) => {
  window.open(`${API}/announcements/${id}/pdf`, '_blank')
}

onMounted(search)
</script>

<style scoped>
.announcements-page { max-width: 1200px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.filters { display: flex; gap: 10px; align-items: center; }
</style>
