<template>
  <el-container class="layout-container">
    <el-header class="header">
      <div class="logo">
        <el-icon :size="24" color="#409eff"><DataLine /></el-icon>
        <span>SITP 避险公告大模型分析平台</span>
      </div>
      <div class="subtitle">FastAPI + Vue3 智能处理引擎</div>
    </el-header>
    
    <el-main class="main-content">
      <el-row :gutter="24">
        <!-- 爬虫控制面板 -->
        <el-col :span="12">
          <el-card class="box-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div>
                  <el-icon color="#67C23A"><Download /></el-icon>
                  <span class="card-title">公告爬虫模块</span>
                </div>
                <el-tag size="small" type="success">数据采集</el-tag>
              </div>
            </template>
            <el-form label-width="100px" :model="crawlerForm" label-position="left">
              <el-form-item label="搜索关键词">
                <el-input v-model="crawlerForm.search_key" placeholder="如：套期保值"></el-input>
              </el-form-item>
              <el-form-item label="时间范围">
                <el-col :span="11">
                  <el-date-picker type="date" placeholder="开始日期" v-model="crawlerForm.start_date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%;"></el-date-picker>
                </el-col>
                <el-col class="line" :span="2" style="text-align: center; color:#909399">-</el-col>
                <el-col :span="11">
                  <el-date-picker type="date" placeholder="结束日期" v-model="crawlerForm.end_date" format="YYYY-MM-DD" value-format="YYYY-MM-DD" style="width: 100%;"></el-date-picker>
                </el-col>
              </el-form-item>
              <el-form-item label="过滤关键词">
                <el-input v-model="crawlerForm.filter_keywords" placeholder="以逗号分隔，如：取消,终止"></el-input>
              </el-form-item>
              <el-form-item label="爬取页数大小">
                <el-input-number v-model="crawlerForm.page_size" :min="1" :max="100"></el-input-number>
              </el-form-item>
              <div class="action-bar">
                <el-button type="primary" size="large" @click="startCrawl" :loading="crawling" class="submit-btn" color="#409eff">
                  <el-icon><CopyDocument /></el-icon> 启动定向爬取
                </el-button>
                <el-button size="large" @click="fetchPdfs" plain><el-icon><RefreshRight /></el-icon> 刷新已下载</el-button>
              </div>
            </el-form>
            
            <div class="list-section">
              <div class="section-title">
                已归档 PDF 文件 ({{ pdfFiles.length }} 个)
              </div>
              <ul class="file-list nice-scroll">
                <li v-for="file in pdfFiles" :key="file">
                  <el-icon color="#f56c6c"><Document /></el-icon> 
                  <span class="file-name" :title="file">{{ file }}</span>
                </li>
                <li v-if="pdfFiles.length === 0" class="empty-text">暂未检测到本地 PDF 数据</li>
              </ul>
            </div>
          </el-card>
        </el-col>

        <!-- LLM 分析面板 -->
        <el-col :span="12">
          <el-card class="box-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <div>
                  <el-icon color="#E6A23C"><Cpu /></el-icon>
                  <span class="card-title">LLM 深度语义分析模块</span>
                </div>
                <el-tag size="small" type="warning">大模型处理</el-tag>
              </div>
            </template>
            <el-form label-width="120px" :model="llmForm" label-position="left">
              <el-form-item label="阿里云 API Key" required>
                <el-input v-model="llmForm.api_key" type="password" show-password placeholder="sk-xxxxxx..." clearable>
                  <template #prefix>
                    <el-icon><Key /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <div class="model-config-title">智能模型流配置</div>
              
              <el-row :gutter="10">
                <el-col :span="12">
                  <el-form-item label="1. 抽取分析模型" label-width="130px">
                    <el-select v-model="llmForm.model_settings.analysis">
                      <el-option label="模型A (DeepSeek-v3.2)" value="a"></el-option>
                      <el-option label="模型B (Qwen-Plus)" value="b"></el-option>
                      <el-option label="模型C (Qwen3-Max)" value="c"></el-option>
                      <el-option label="模型D (Qwen-Max)" value="d"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="2. 数据清洗模型" label-width="130px">
                    <el-select v-model="llmForm.model_settings.processing">
                      <el-option label="模型A (DeepSeek-v3.2)" value="a"></el-option>
                      <el-option label="模型B (Qwen-Plus)" value="b"></el-option>
                      <el-option label="模型C (Qwen3-Max)" value="c"></el-option>
                      <el-option label="模型D (Qwen-Max)" value="d"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="3. 结构重检模型" label-width="130px">
                    <el-select v-model="llmForm.model_settings.recheck">
                      <el-option label="模型A (DeepSeek-v3.2)" value="a"></el-option>
                      <el-option label="模型B (Qwen-Plus)" value="b"></el-option>
                      <el-option label="模型C (Qwen3-Max)" value="c"></el-option>
                      <el-option label="模型D (Qwen-Max)" value="d"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :span="12">
                  <el-form-item label="4. 专业汉化模型" label-width="130px">
                    <el-select v-model="llmForm.model_settings.translation">
                      <el-option label="模型A (DeepSeek-v3.2)" value="a"></el-option>
                      <el-option label="模型B (Qwen-Plus)" value="b"></el-option>
                      <el-option label="模型C (Qwen3-Max)" value="c"></el-option>
                      <el-option label="模型D (Qwen-Max)" value="d"></el-option>
                    </el-select>
                  </el-form-item>
                </el-col>
              </el-row>

              <div class="action-bar">
                <el-button type="warning" size="large" @click="startAnalysis" :loading="analyzing" class="submit-btn" color="#e6a23c">
                  <el-icon><MagicStick /></el-icon> 启动结构化提取引擎
                </el-button>
                <el-button size="large" @click="fetchResults" plain><el-icon><RefreshRight /></el-icon> 刷新报告列表</el-button>
              </div>
            </el-form>

            <div class="list-section">
              <div class="section-title">
                结构化报告池 ({{ resultFiles.length }} 份)
              </div>
              <ul class="file-list nice-scroll">
                <li v-for="file in resultFiles" :key="file">
                  <el-icon color="#67c23a"><DocumentChecked /></el-icon> 
                  <span class="file-name" :title="file">{{ file }}</span>
                </li>
                <li v-if="resultFiles.length === 0" class="empty-text">等待大模型产生输出结果</li>
              </ul>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-main>
  </el-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'
import axios from 'axios'

// 后端 API 地址
const API_BASE_URL = 'http://127.0.0.1:8000/api'

// -- 状态 --
const crawling = ref(false)
const analyzing = ref(false)
const pdfFiles = ref([])
const resultFiles = ref([])

const crawlerForm = ref({
  search_key: '套期保值',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  filter_keywords: '',
  page_size: 30
})

const llmForm = ref({
  api_key: '',
  model_settings: {
    analysis: 'a',
    processing: 'b',
    recheck: 'c',
    translation: 'b'
  }
})

// -- API 交互 --
const fetchPdfs = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/data/pdfs`)
    pdfFiles.value = res.data
  } catch (error) {
    console.error('获取PDF列表失败:', error)
  }
}

const fetchResults = async () => {
  try {
    const res = await axios.get(`${API_BASE_URL}/data/results`)
    resultFiles.value = res.data
  } catch (error) {
    console.error('获取结果列表失败:', error)
  }
}

const startCrawl = async () => {
  if (!crawlerForm.value.search_key || !crawlerForm.value.start_date || !crawlerForm.value.end_date) {
    ElMessage.warning('请填写完整的搜索关键字和时间范围！')
    return
  }
  crawling.value = true
  ElMessage.info('爬虫后台任务已触发，请关注命令行日志并在稍后刷新列表。')
  try {
    const res = await axios.post(`${API_BASE_URL}/crawl`, crawlerForm.value)
    ElNotification({
      title: '任务完成',
      message: res.data.message || '爬虫任务执行完成',
      type: 'success'
    })
    fetchPdfs()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '网络错误: 爬虫执行失败')
  } finally {
    crawling.value = false
  }
}

const startAnalysis = async () => {
  if (!llmForm.value.api_key) {
    ElMessage.warning('必须输入您的 API Key 才能调用大模型！')
    return
  }
  
  if (pdfFiles.value.length === 0) {
    ElMessage.error('当前没有可分析的 PDF 文件，请先执行爬虫！')
    return
  }

  analyzing.value = true
  ElMessage.info('AI 处理引擎已启动并进行多页 PDF 提取解析，过程较慢，请耐心等待！')
  try {
    const res = await axios.post(`${API_BASE_URL}/analyze`, llmForm.value)
    ElNotification({
      title: '分析完成',
      message: res.data.message || 'LLM 工作流执行结束',
      type: 'success'
    })
    fetchResults()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || '网络错误: 分析执行失败')
  } finally {
    analyzing.value = false
  }
}

// -- 初始化 --
onMounted(() => {
  fetchPdfs()
  fetchResults()
})
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
}
.header {
  background-color: #fff;
  box-shadow: 0 1px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  position: sticky;
  top: 0;
  z-index: 100;
  height: 64px;
}
.logo {
  font-size: 22px;
  font-weight: 800;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 12px;
}
.subtitle {
  font-size: 14px;
  color: #909399;
  letter-spacing: 0.5px;
}
.main-content {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
}
.box-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
  transition: all 0.3s;
  height: 100%;
}
.box-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.06) !important;
  transform: translateY(-2px);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.card-header div {
  display: flex;
  align-items: center;
  gap: 8px;
}
.card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.model-config-title {
  font-size: 14px;
  font-weight: bold;
  color: #606266;
  margin: 20px 0 15px 0;
  padding-left: 10px;
  border-left: 4px solid #e6a23c;
  line-height: 1;
}
.action-bar {
  margin-top: 30px;
  display: flex;
  gap: 15px;
}
.submit-btn {
  flex: 1;
  font-weight: bold;
  letter-spacing: 1px;
}
.list-section {
  margin-top: 35px;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.section-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 14px;
  background-color: #409eff;
  border-radius: 2px;
}
.file-list {
  list-style: none;
  padding: 0;
  margin: 0;
  height: 280px;
  overflow-y: auto;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background-color: #fafafa;
}
.nice-scroll::-webkit-scrollbar {
  width: 6px;
}
.nice-scroll::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 3px;
}
.nice-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.file-list li {
  padding: 10px 16px;
  border-bottom: 1px solid #f2f6fc;
  font-size: 14px;
  color: #606266;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background-color 0.2s;
}
.file-list li:hover {
  background-color: #f0f9eb;
}
.file-list li:last-child {
  border-bottom: none;
}
.file-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.empty-text {
  height: 100%;
  color: #909399 !important;
  display: flex;
  align-items: center;
  justify-content: center;
  font-style: italic;
  font-size: 13px;
}
</style>
