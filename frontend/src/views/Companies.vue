<template>
  <div class="companies-page">
    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span class="title">公司与主营业务查询</span>
          <div class="filters">
            <el-input v-model="keyword" placeholder="搜索公司名称/代码" clearable style="width:200px" @keyup.enter="search" />
            <el-select v-model="market" placeholder="市场" clearable style="width:120px" @change="search">
              <el-option label="全部" value="" />
              <el-option label="深交所" value="SZSE" />
              <el-option label="上交所" value="SSE" />
              <el-option label="北交所" value="BSE" />
            </el-select>
            <el-button type="primary" @click="search"><el-icon><Search /></el-icon> 搜索</el-button>
          </div>
        </div>
      </template>

      <el-table :data="companies" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="stock_code" label="股票代码" width="100" />
        <el-table-column prop="company_name" label="公司全称" min-width="200" />
        <el-table-column prop="company_short_name" label="简称" width="100" />
        <el-table-column prop="market" label="市场" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="primary" link @click="showBusiness(row.stock_code)">查看主营业务</el-button>
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

    <!-- 主营业务弹窗 -->
    <el-dialog v-model="bizVisible" :title="`${bizCode} 主营业务`" width="700px">
      <el-form inline style="margin-bottom:12px">
        <el-form-item label="年份">
          <el-input-number v-model="bizYear" :min="2000" :max="2030" @change="fetchBiz" />
        </el-form-item>
      </el-form>
      <el-table :data="bizList" v-loading="bizLoading" border stripe>
        <el-table-column prop="biz_year" label="年份" width="80" />
        <el-table-column prop="industry_class" label="行业分类" width="140" />
        <el-table-column prop="business_core" label="核心业务" width="160" />
        <el-table-column prop="main_business" label="主营业务描述" min-width="200" show-overflow-tooltip />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'
const keyword = ref('')
const market = ref('')
const page = ref(1)
const size = 20
const total = ref(0)
const companies = ref([])
const loading = ref(false)

const search = async () => {
  loading.value = true
  try {
    const res = await axios.get(`${API}/companies`, { params: { keyword: keyword.value, market: market.value, page: page.value, size } })
    companies.value = res.data.items
    total.value = res.data.total
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

// 主营业务弹窗
const bizVisible = ref(false)
const bizCode = ref('')
const bizYear = ref(2024)
const bizList = ref([])
const bizLoading = ref(false)

const showBusiness = (code) => {
  bizCode.value = code
  bizVisible.value = true
  fetchBiz()
}

const fetchBiz = async () => {
  bizLoading.value = true
  try {
    const res = await axios.get(`${API}/businesses`, { params: { year: bizYear.value, page: 1, size: 50 } })
    // 前端过滤匹配当前公司（因 businesses API 暂不支持 stock_code 筛选）
    bizList.value = res.data.items.filter(b => b.stock_code === bizCode.value)
  } catch (e) { console.error(e) }
  finally { bizLoading.value = false }
}

onMounted(search)
</script>

<style scoped>
.companies-page { max-width: 1100px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; }
.title { font-size: 18px; font-weight: 600; }
.filters { display: flex; gap: 10px; align-items: center; }
</style>
