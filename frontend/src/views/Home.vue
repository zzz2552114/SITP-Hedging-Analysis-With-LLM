<template>
  <div class="home-page">
    <div class="welcome">
      <h1>SITP 避险公告大模型分析平台</h1>
      <p>基于巨潮资讯网套期保值公告 PDF 的 LLM 结构化分析与展示系统</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="6" v-for="card in navCards" :key="card.route">
        <el-card shadow="hover" class="nav-card" @click="$router.push(card.route)">
          <div class="card-icon" :style="{ background: card.color }">
            <el-icon :size="28" color="#fff"><component :is="card.icon" /></el-icon>
          </div>
          <div class="card-info">
            <div class="card-title">{{ card.title }}</div>
            <div class="card-desc">{{ card.desc }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
const navCards = [
  { title: '公告爬虫', desc: '从巨潮资讯网定向爬取套保公告 PDF', route: '/crawler', icon: 'Download', color: '#67c23a' },
  { title: 'LLM 分析', desc: '调用大语言模型进行结构化提取', route: '/analyzer', icon: 'Cpu', color: '#e6a23c' },
  { title: '公司与主营业务', desc: '按年份查看上市公司主营业务', route: '/companies', icon: 'OfficeBuilding', color: '#409eff' },
  { title: '商品类目', desc: '浏览期货商品标准分类层级', route: '/commodities', icon: 'PriceTag', color: '#909399' },
  { title: '公告管理', desc: '查看公告解析状态与 PDF 预览', route: '/announcements', icon: 'Document', color: '#f56c6c' },
  { title: '套保明细', desc: '按年份、公司、商品筛选套保记录', route: '/hedges', icon: 'TrendCharts', color: '#009688' },
  { title: '渗透率统计', desc: '同业套保渗透率比对分析', route: '/compare', icon: 'DataAnalysis', color: '#673ab7' },
]
</script>

<style scoped>
.home-page {
  max-width: 1200px;
  margin: 0 auto;
}
.welcome {
  text-align: center;
  padding: 40px 0 36px;
}
.welcome h1 {
  font-size: 28px;
  color: #303133;
  margin: 0 0 10px;
}
.welcome p {
  color: #909399;
  font-size: 15px;
  margin: 0;
}
.nav-card {
  cursor: pointer;
  margin-bottom: 20px;
  border-radius: 10px;
  transition: all 0.25s;
}
.nav-card:hover {
  transform: translateY(-4px);
}
.card-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}
.card-info .card-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 6px;
}
.card-info .card-desc {
  font-size: 13px;
  color: #909399;
  line-height: 1.5;
}
</style>
