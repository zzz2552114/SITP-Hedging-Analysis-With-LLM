<template>
  <div class="analyzer-page">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <div><el-icon color="#E6A23C"><Cpu /></el-icon><span class="title">LLM 深度语义分析模块</span></div>
          <el-tag size="small" type="warning">大模型处理</el-tag>
        </div>
      </template>
      <el-form label-width="120px" :model="llmForm" label-position="left">
        <el-form-item label="阿里云 API Key" required>
          <el-input v-model="llmForm.api_key" type="password" show-password placeholder="sk-xxxxxx..." clearable>
            <template #prefix><el-icon><Key /></el-icon></template>
          </el-input>
        </el-form-item>

        <div class="model-config-title">智能模型流配置</div>
        <el-row :gutter="10">
          <el-col :span="12" v-for="m in modelFields" :key="m.key">
            <el-form-item :label="m.label" label-width="130px">
              <el-select v-model="llmForm.model_settings[m.key]">
                <el-option v-for="o in modelOptions" :key="o.value" :label="o.label" :value="o.value" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <div class="action-bar">
          <el-button type="warning" size="large" @click="startAnalysis" :loading="analyzing">
            <el-icon><MagicStick /></el-icon> 启动结构化提取引擎
          </el-button>
          <el-button size="large" @click="fetchResults" plain><el-icon><RefreshRight /></el-icon> 刷新报告列表</el-button>
        </div>
      </el-form>

      <div class="list-section">
        <div class="section-title">结构化报告池 ({{ resultFiles.length }} 份)</div>
        <ul class="file-list">
          <li v-for="file in resultFiles" :key="file">
            <el-icon color="#67c23a"><DocumentChecked /></el-icon>
            <span class="file-name" :title="file">{{ file }}</span>
          </li>
          <li v-if="resultFiles.length === 0" class="empty-text">等待大模型产生输出结果</li>
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
const analyzing = ref(false)
const resultFiles = ref([])

const modelOptions = [
  { label: '模型A (DeepSeek-v3.2)', value: 'a' },
  { label: '模型B (Qwen-Plus)', value: 'b' },
  { label: '模型C (Qwen3-Max)', value: 'c' },
  { label: '模型D (Qwen-Max)', value: 'd' },
]
const modelFields = [
  { key: 'analysis', label: '1. 抽取分析模型' },
  { key: 'processing', label: '2. 数据清洗模型' },
  { key: 'recheck', label: '3. 结构重检模型' },
  { key: 'translation', label: '4. 专业汉化模型' },
]

const llmForm = ref({
  api_key: '',
  model_settings: { analysis: 'a', processing: 'b', recheck: 'c', translation: 'b' }
})

const fetchResults = async () => {
  try { resultFiles.value = (await axios.get(`${API}/data/results`)).data } catch (e) { console.error(e) }
}

const startAnalysis = async () => {
  if (!llmForm.value.api_key) return ElMessage.warning('必须输入 API Key！')
  analyzing.value = true
  ElMessage.info('AI 处理引擎已启动，请耐心等待。')
  try {
    const res = await axios.post(`${API}/analyze`, llmForm.value)
    ElNotification({ title: '分析完成', message: res.data.message, type: 'success' })
    fetchResults()
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '分析执行失败')
  } finally { analyzing.value = false }
}

onMounted(fetchResults)
</script>

<style scoped>
.analyzer-page { max-width: 800px; margin: 0 auto; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header div { display: flex; align-items: center; gap: 8px; }
.title { font-size: 18px; font-weight: 600; }
.model-config-title { font-size: 14px; font-weight: bold; color: #606266; margin: 20px 0 15px; padding-left: 10px; border-left: 4px solid #e6a23c; }
.action-bar { margin-top: 24px; display: flex; gap: 12px; }
.list-section { margin-top: 30px; }
.section-title { font-size: 15px; font-weight: 600; margin-bottom: 10px; padding-left: 10px; border-left: 4px solid #e6a23c; }
.file-list { list-style: none; padding: 0; margin: 0; max-height: 300px; overflow-y: auto; border: 1px solid #ebeef5; border-radius: 8px; background: #fafafa; }
.file-list li { padding: 10px 16px; border-bottom: 1px solid #f2f6fc; font-size: 14px; color: #606266; display: flex; align-items: center; gap: 10px; }
.file-list li:last-child { border-bottom: none; }
.file-list li:hover { background: #fdf6ec; }
.file-name { flex: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.empty-text { height: 120px; color: #909399 !important; display: flex; align-items: center; justify-content: center; font-style: italic; }
</style>
