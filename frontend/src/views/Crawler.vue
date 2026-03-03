<template>
  <div class="crawler-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div><el-icon color="#67C23A"><Download /></el-icon><span class="title">公告爬虫模块</span></div>
          <el-tag size="small" type="success">数据采集</el-tag>
        </div>
      </template>
      <el-form label-width="100px" :model="crawlerForm" label-position="left">
        <el-form-item label="搜索关键词">
          <el-input v-model="crawlerForm.search_key" placeholder="如：套期保值" />
        </el-form-item>
        <el-form-item label="时间范围">
          <el-col :span="11">
            <el-date-picker type="date" placeholder="开始日期" v-model="crawlerForm.start_date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:100%" />
          </el-col>
          <el-col :span="2" style="text-align:center;color:#909399">-</el-col>
          <el-col :span="11">
            <el-date-picker type="date" placeholder="结束日期" v-model="crawlerForm.end_date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width:100%" />
          </el-col>
        </el-form-item>
        <el-form-item label="过滤关键词">
          <el-input v-model="crawlerForm.filter_keywords" placeholder="以逗号分隔，如：取消,终止" />
        </el-form-item>
        <el-form-item label="爬取页数大小">
          <el-input-number v-model="crawlerForm.page_size" :min="1" :max="100" />
        </el-form-item>
        <div class="action-bar">
          <el-button type="primary" size="large" @click="startCrawl" :loading="crawling">
            <el-icon><CopyDocument /></el-icon> 启动定向爬取
          </el-button>
          <el-button size="large" @click="fetchPdfs" plain><el-icon><RefreshRight /></el-icon> 刷新已下载</el-button>
        </div>
      </el-form>

      <div class="list-section">
        <div class="section-title">已归档 PDF 文件 ({{ pdfFiles.length }} 个)</div>
        <ul class="file-list">
          <li v-for="file in pdfFiles" :key="file">
            <el-icon color="#f56c6c"><Document /></el-icon>
            <span class="file-name" :title="file">{{ file }}</span>
          </li>
          <li v-if="pdfFiles.length === 0" class="empty-text">暂未检测到本地 PDF 数据</li>
        </ul>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import axios from 'axios'

const API = 'http://127.0.0.1:8000/api'
const crawling = ref(false)
const pdfFiles = ref([])

const crawlerForm = ref({
  search_key: '套期保值',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  filter_keywords: '',
  page_size: 30
})

const fetchPdfs = async () => {
  try { pdfFiles.value = (await axios.get(`${API}/data/pdfs`)).data } catch (e) { console.error(e) }
}

const startCrawl = async () => {
  if (!crawlerForm.value.search_key || !crawlerForm.value.start_date || !crawlerForm.value.end_date) {
    return ElMessage.warning('请填写完整的搜索关键字和时间范围！')
  }
  crawling.value = true
  ElMessage.info('爬虫后台任务已触发，请稍后刷新列表。')
  try {
    const res = await axios.post(`${API}/crawl`, crawlerForm.value)
    ElNotification({ title: '任务完成', message: res.data.message, type: 'success' })
    fetchPdfs()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '爬虫执行失败')
  } finally { crawling.value = false }
}

onMounted(fetchPdfs)
</script>

<style scoped>
.crawler-page { max-width: 800px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header div { display: flex; align-items: center; gap: 8px; }
.title { font-size: 18px; font-weight: 600; }
.action-bar { margin-top: 24px; display: flex; gap: 12px; }
.list-section { margin-top: 30px; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: 10px; padding-left: 10px; border-left: 4px solid #67c23a; }
.file-list { list-style: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto; border: 1px solid #ebeef5; border-radius: 8px; background: #fafafa; }
.file-list li { padding: 10px 16px; border-bottom: 1px solid #f2f6fc; font-size: 14px; color: #606266; display: flex; align-items: center; gap: 10px; }
.file-list li:last-child { border-bottom: none; }
.file-list li:hover { background: #f0f9eb; }
.file-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.empty-text { height: 120px; color: #909399 !important; display: flex; align-items: center; justify-content: center; font-style: italic; }
</style>
