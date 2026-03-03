<template>
  <div class="commodities-page">
    <el-card shadow="never">
      <template #header>
        <div class="header-row">
          <span class="title">期货商品类目浏览</span>
          <el-select v-model="filterLevel" placeholder="按层级筛选" clearable style="width:160px" @change="fetch">
            <el-option label="全部" :value="null" />
            <el-option label="一级分类" :value="1" />
            <el-option label="二级分类" :value="2" />
            <el-option label="三级分类" :value="3" />
          </el-select>
        </div>
      </template>

      <el-table :data="items" v-loading="loading" stripe border style="width:100%">
        <el-table-column prop="catalog_id" label="ID" width="70" />
        <el-table-column prop="catalog_level" label="层级" width="70">
          <template #default="{ row }">
            <el-tag :type="row.catalog_level === 1 ? 'danger' : row.catalog_level === 2 ? 'warning' : 'info'" size="small">
              L{{ row.catalog_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="commodity_full_name" label="商品全称" min-width="180" />
        <el-table-column prop="commodity_short_name" label="简称" width="120" />
        <el-table-column prop="exchange" label="交易所" width="120" />
        <el-table-column prop="association_code" label="协会代码" width="120" />
        <el-table-column prop="parent_catalog_id" label="父级ID" width="80" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'
const items = ref([])
const loading = ref(false)
const filterLevel = ref(null)

const fetch = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterLevel.value !== null) params.level = filterLevel.value
    items.value = (await axios.get(`${API}/commodities`, { params })).data
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

onMounted(fetch)
</script>

<style scoped>
.commodities-page { max-width: 1000px; margin: 0 auto; }
.header-row { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 18px; font-weight: 600; }
</style>
