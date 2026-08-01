<template>
  <div class="futures-kline-page">
    <!-- 搜索栏 -->
    <el-card class="search-card" shadow="never">
      <el-row :gutter="16" align="middle">
        <el-col :span="12">
          <el-input
            v-model="keyword"
            placeholder="搜索品种名称或代码，如：铜、沪铜、CU..."
            clearable
            :prefix-icon="Search"
            @input="onSearch"
            @clear="onSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-select v-model="selectedExchange" clearable placeholder="交易所" @change="onSearch">
            <el-option label="上期所 SHFE" value="SHFE" />
            <el-option label="大商所 DCE" value="DCE" />
            <el-option label="郑商所 CZCE" value="CZCE" />
            <el-option label="中金所 CFFEX" value="CFFEX" />
            <el-option label="上期能源 INE" value="INE" />
            <el-option label="广期所 GFEX" value="GFEX" />
          </el-select>
        </el-col>
        <el-col :span="6" style="text-align:right">
          <el-tag type="info">{{ totalProducts }} 个品种</el-tag>
          <el-tag type="success" style="margin-left:8px">{{ totalContracts }} 个合约</el-tag>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="16" class="main-row">
      <!-- 左侧：品种列表 -->
      <el-col :span="7">
        <el-card class="left-card" shadow="never">
          <template #header>
            <div class="left-header">
              <span class="card-title">期货品种</span>
              <div class="alpha-nav">
                <span
                  v-for="letter in alphabetList"
                  :key="letter"
                  class="alpha-chip"
                  :class="{ active: activeAlpha === letter }"
                  @click="jumpToAlpha(letter)"
                >{{ letter }}</span>
              </div>
            </div>
          </template>

          <div class="product-scroll" v-loading="loadingProducts">
            <el-empty v-if="!loadingProducts && Object.keys(groupedProducts).length === 0" description="暂无品种数据" />
            <div
              v-for="(products, letter) in groupedProducts"
              :key="letter"
              :ref="el => { if (el) alphaRefs[letter] = el }"
              class="alpha-group"
            >
              <div class="alpha-label">{{ letter }}</div>
              <div class="product-chips">
                <div
                  v-for="p in products"
                  :key="p.fut_code + p.exchange"
                  class="product-chip"
                  :class="{ selected: selectedProduct?.fut_code === p.fut_code && selectedProduct?.exchange === p.exchange }"
                  @click="selectProduct(p)"
                >
                  <span class="product-name">{{ p.product_name }}</span>
                  <span class="product-code">{{ p.fut_code }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：合约选择 + K线图 -->
      <el-col :span="17">
        <el-card class="right-card" shadow="never">
          <template #header>
            <div class="chart-header">
              <div class="chart-title-area">
                <span class="card-title">
                  {{ selectedProduct ? `${selectedProduct.product_name}（${selectedProduct.fut_code}·${selectedProduct.exchange}）` : '请选择品种' }}
                </span>
                <!-- 合约选择 -->
                <el-select
                  v-if="selectedProduct && contractList.length"
                  v-model="selectedCode"
                  size="small"
                  style="width:180px; margin-left:12px"
                  placeholder="选择合约"
                  @change="loadKline"
                  filterable
                >
                  <el-option
                    v-for="c in contractList"
                    :key="c.ts_code"
                    :label="c.name"
                    :value="c.ts_code"
                  />
                </el-select>
              </div>
              <el-radio-group v-if="selectedCode" v-model="dateRange" size="small" @change="loadKline">
                <el-radio-button value="1M">近1月</el-radio-button>
                <el-radio-button value="3M">近3月</el-radio-button>
                <el-radio-button value="6M">近6月</el-radio-button>
                <el-radio-button value="1Y">近1年</el-radio-button>
                <el-radio-button value="3Y">近3年</el-radio-button>
                <el-radio-button value="ALL">全部</el-radio-button>
              </el-radio-group>
            </div>
          </template>

          <div class="chart-body">
            <el-empty v-if="!selectedProduct" description="← 从左侧选择品种" style="margin-top:80px" />
            <el-empty v-else-if="!selectedCode && contractList.length" description="请选择合约" style="margin-top:80px" />
            <div v-else v-loading="loadingKline" class="chart-wrap">
              <el-empty v-if="!loadingKline && klineData.length === 0" description="该合约暂无K线数据（同步中）" style="margin-top:60px" />
              <template v-else>
                <div ref="chartDom" class="echarts-main" />
                <div ref="volDom" class="echarts-vol" />
              </template>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { Search } from '@element-plus/icons-vue'
import axios from 'axios'
import * as echarts from 'echarts'

const API = '/api'

// ── 状态 ──────────────────────────────────────
const keyword = ref('')
const selectedExchange = ref('')
const groupedProducts = ref({})   // { A: [ProductItem...], ... }
const loadingProducts = ref(false)

const selectedProduct = ref(null) // ProductItem
const contractList = ref([])      // ContractItem[]
const selectedCode = ref('')

const loadingKline = ref(false)
const klineData = ref([])
const dateRange = ref('1Y')

const alphaRefs = reactive({})
const activeAlpha = ref('')

let chartInst = null
let volInst = null
const chartDom = ref(null)
const volDom = ref(null)

// ── 计算 ──────────────────────────────────────
const alphabetList = computed(() => Object.keys(groupedProducts.value).sort())
const totalProducts = computed(() =>
  Object.values(groupedProducts.value).reduce((s, arr) => s + arr.length, 0)
)
const totalContracts = computed(() => contractList.value.length)

// ── 品种列表 ──────────────────────────────────
async function fetchProducts() {
  loadingProducts.value = true
  try {
    const params = {}
    if (keyword.value) params.keyword = keyword.value
    if (selectedExchange.value) params.exchange = selectedExchange.value
    const { data } = await axios.get(`${API}/futures/products/grouped`, { params })
    groupedProducts.value = data
  } catch (e) {
    console.error(e)
  } finally {
    loadingProducts.value = false
  }
}

let searchTimer = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(fetchProducts, 280)
}

function jumpToAlpha(letter) {
  activeAlpha.value = letter
  const el = alphaRefs[letter]
  if (el) el.$el ? el.$el.scrollIntoView({ behavior: 'smooth', block: 'start' })
               : el.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
}

// ── 品种点击 → 拉合约列表 ────────────────────
async function selectProduct(p) {
  selectedProduct.value = p
  selectedCode.value = ''
  contractList.value = []
  klineData.value = []
  disposeCharts()

  try {
    const params = { exchange: p.exchange }
    const { data } = await axios.get(`${API}/futures/products/${p.fut_code}/contracts`, { params })
    contractList.value = data
    // 默认选第一个合约（最新）
    if (data.length) {
      selectedCode.value = data[0].ts_code
      loadKline()
    }
  } catch (e) {
    console.error(e)
  }
}

// ── K线加载 ───────────────────────────────────
function getDateRange() {
  const fmt = d => d.toISOString().slice(0, 10).replace(/-/g, '')
  const now = new Date()
  if (dateRange.value === 'ALL') return
  const days = { '1M': 30, '3M': 90, '6M': 180, '1Y': 365, '3Y': 1095 }[dateRange.value] || 365
  const start = new Date(now)
  start.setDate(start.getDate() - days)
  return { start_date: fmt(start), end_date: fmt(now) }
}

async function loadKline() {
  if (!selectedCode.value) return
  loadingKline.value = true
  klineData.value = []
  disposeCharts()
  try {
    const params = { limit: 10000, ...getDateRange() }
    const { data } = await axios.get(`${API}/futures/kline/${selectedCode.value}`, { params })
    klineData.value = data
    if (data.length) {
      await nextTick()
      requestAnimationFrame(renderChart)
    }
  } catch (e) {
    console.error(e)
  } finally {
    loadingKline.value = false
  }
}

// ── ECharts ───────────────────────────────────
function disposeCharts() {
  chartInst?.dispose(); chartInst = null
  volInst?.dispose(); volInst = null
}

function renderChart() {
  if (!klineData.value.length || !chartDom.value || !volDom.value) return

  const dates = klineData.value.map(d => d.trade_date)
  const ohlc  = klineData.value.map(d => [d.open, d.close, d.low, d.high])
  const vols  = klineData.value.map(d => ({
    value: d.vol ?? 0,
    itemStyle: { color: (d.close ?? 0) >= (d.open ?? 0) ? '#ef5350' : '#26a69a' }
  }))

  const contractName = contractList.value.find(c => c.ts_code === selectedCode.value)?.name || selectedCode.value

  chartInst = echarts.init(chartDom.value)
  chartInst.setOption({
    backgroundColor: '#fff',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter(params) {
        const idx = params[0]?.dataIndex
        const d = klineData.value[idx]
        if (!d) return ''
        const fmtDate = `${d.trade_date.slice(0,4)}-${d.trade_date.slice(4,6)}-${d.trade_date.slice(6)}`
        const color = (d.close ?? 0) >= (d.open ?? 0) ? '#ef5350' : '#26a69a'
        return `<div style="line-height:1.8">
          <b>${fmtDate}</b><br/>
          开 <b style="color:${color}">${d.open ?? '-'}</b> &nbsp;
          收 <b style="color:${color}">${d.close ?? '-'}</b><br/>
          高 ${d.high ?? '-'} &nbsp; 低 ${d.low ?? '-'}<br/>
          结算 ${d.settle ?? '-'} &nbsp; 持仓 ${d.oi ?? '-'}<br/>
          涨跌 ${d.change1 ?? '-'}
        </div>`
      }
    },
    legend: { data: [contractName], top: 4, textStyle: { fontSize: 12 } },
    grid: { left: 65, right: 20, top: 36, bottom: 36 },
    xAxis: {
      type: 'category', data: dates, splitLine: { show: false },
      axisLabel: { formatter: v => `${v.slice(0,4)}-${v.slice(4,6)}-${v.slice(6)}`, fontSize: 11 }
    },
    yAxis: { scale: true, splitArea: { show: true }, axisLabel: { fontSize: 11 } },
    dataZoom: [
      { type: 'inside', start: 60, end: 100 },
      { show: true, type: 'slider', bottom: 4, height: 20 }
    ],
    series: [{
      name: contractName,
      type: 'candlestick',
      data: ohlc,
      itemStyle: {
        color: '#ef5350', color0: '#26a69a',
        borderColor: '#ef5350', borderColor0: '#26a69a'
      }
    }]
  })

  volInst = echarts.init(volDom.value)
  volInst.setOption({
    backgroundColor: '#fff',
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: 65, right: 20, top: 6, bottom: 30 },
    xAxis: { type: 'category', data: dates, axisLabel: { show: false }, splitLine: { show: false } },
    yAxis: { scale: true, splitNumber: 2, axisLabel: { fontSize: 10 } },
    dataZoom: [
      { type: 'inside', start: 60, end: 100, xAxisIndex: [0] },
      { show: false, type: 'slider', xAxisIndex: [0] }
    ],
    series: [{ name: '成交量', type: 'bar', data: vols, barMaxWidth: 10 }]
  })

  // 联动缩放
  chartInst.on('dataZoom', () => {
    const opt = chartInst.getOption()
    const dz = opt.dataZoom?.[0]
    if (dz && volInst) {
      volInst.dispatchAction({ type: 'dataZoom', dataZoomIndex: 0, start: dz.start, end: dz.end })
    }
  })
}

function onResize() {
  chartInst?.resize()
  volInst?.resize()
}

onMounted(() => {
  fetchProducts()
  window.addEventListener('resize', onResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', onResize)
  disposeCharts()
})
</script>

<style scoped>
.futures-kline-page {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.search-card { flex-shrink: 0; }
.main-row { flex: 1; align-items: stretch; }

/* 左侧 */
.left-card {
  height: calc(100vh - 196px);
  display: flex;
  flex-direction: column;
}
.left-card :deep(.el-card__header) { padding: 10px 14px; flex-shrink: 0; }
.left-card :deep(.el-card__body) { flex: 1; overflow: hidden; padding: 0; }
.left-header { display: flex; flex-direction: column; gap: 6px; }
.alpha-nav { display: flex; flex-wrap: wrap; gap: 3px; }
.alpha-chip {
  padding: 1px 6px; border-radius: 3px; font-size: 11px;
  cursor: pointer; background: #f0f2f5; color: #606266;
  user-select: none; transition: background 0.15s;
}
.alpha-chip:hover, .alpha-chip.active { background: #409eff; color: #fff; }

.product-scroll { height: 100%; overflow-y: auto; padding: 8px 10px; }
.alpha-group { margin-bottom: 10px; }
.alpha-label {
  font-size: 12px; font-weight: 700; color: #409eff;
  padding: 3px 0 4px; border-bottom: 1px solid #f0f0f0; margin-bottom: 6px;
}
.product-chips { display: flex; flex-wrap: wrap; gap: 6px; }
.product-chip {
  display: flex; flex-direction: column; align-items: center;
  padding: 5px 10px; border-radius: 6px; cursor: pointer;
  background: #f5f7fa; border: 1px solid #e4e7ed;
  transition: all 0.15s; min-width: 60px;
}
.product-chip:hover { background: #ecf5ff; border-color: #b3d8ff; }
.product-chip.selected { background: #409eff; border-color: #409eff; }
.product-chip.selected .product-name,
.product-chip.selected .product-code { color: #fff; }
.product-name { font-size: 13px; font-weight: 600; color: #303133; line-height: 1.3; }
.product-code { font-size: 10px; color: #909399; margin-top: 1px; }

/* 右侧 */
.right-card {
  height: calc(100vh - 196px);
  display: flex;
  flex-direction: column;
}
.right-card :deep(.el-card__header) { padding: 10px 16px; flex-shrink: 0; }
.right-card :deep(.el-card__body) { flex: 1; overflow: hidden; padding: 0; }

.chart-header {
  display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
.chart-title-area { display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.card-title { font-weight: 600; font-size: 14px; }

.chart-body { height: 100%; display: flex; flex-direction: column; }
.chart-wrap { flex: 1; display: flex; flex-direction: column; padding: 8px 14px; min-height: 0; }
.echarts-main { flex: 1; min-height: 300px; }
.echarts-vol { height: 110px; flex-shrink: 0; margin-top: 4px; }
</style>
