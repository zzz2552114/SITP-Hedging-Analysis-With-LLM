<template>
  <el-container class="app-layout">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo-area" @click="$router.push('/')">
        <el-icon :size="22" color="#409eff"><DataLine /></el-icon>
        <span v-show="!isCollapse" class="logo-text">SITP 避险分析</span>
      </div>
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        router
        class="sidebar-menu"
        background-color="#fff"
        text-color="#303133"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>

        <el-sub-menu index="data-group">
          <template #title>
            <el-icon><Operation /></el-icon>
            <span>数据采集</span>
          </template>
          <el-menu-item index="/crawler">
            <el-icon><Download /></el-icon>
            <span>公告爬虫</span>
          </el-menu-item>
          <el-menu-item index="/analyzer">
            <el-icon><Cpu /></el-icon>
            <span>LLM 分析</span>
          </el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="query-group">
          <template #title>
            <el-icon><Search /></el-icon>
            <span>数据查询</span>
          </template>
          <el-menu-item index="/companies">
            <el-icon><OfficeBuilding /></el-icon>
            <span>公司与主营业务</span>
          </el-menu-item>
          <el-menu-item index="/commodities">
            <el-icon><PriceTag /></el-icon>
            <span>商品类目</span>
          </el-menu-item>
          <el-menu-item index="/announcements">
            <el-icon><Document /></el-icon>
            <span>公告管理</span>
          </el-menu-item>
          <el-menu-item index="/hedges">
            <el-icon><TrendCharts /></el-icon>
            <span>套保明细</span>
          </el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/compare">
          <el-icon><DataAnalysis /></el-icon>
          <span>渗透率统计</span>
        </el-menu-item>
      </el-menu>

      <div class="collapse-btn" @click="isCollapse = !isCollapse">
        <el-icon><Fold v-if="!isCollapse" /><Expand v-else /></el-icon>
      </div>
    </el-aside>

    <el-container>
      <el-header class="topbar">
        <span class="page-title">{{ $route.meta.title || 'SITP 避险分析系统' }}</span>
        <span class="subtitle">FastAPI + Vue3 智能处理引擎</span>
      </el-header>
      <el-main class="main-area">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'

const isCollapse = ref(false)
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
}
.sidebar {
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
  overflow: hidden;
}
.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}
.logo-text {
  font-size: 17px;
  font-weight: 700;
  color: #2c3e50;
  white-space: nowrap;
}
.sidebar-menu {
  border-right: none;
  flex: 1;
  overflow-y: auto;
}
.collapse-btn {
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border-top: 1px solid #f0f0f0;
  color: #909399;
  flex-shrink: 0;
}
.collapse-btn:hover {
  color: #409eff;
  background: #f5f7fa;
}
.topbar {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
}
.page-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}
.subtitle {
  font-size: 13px;
  color: #909399;
}
.main-area {
  background: #f5f7fa;
  padding: 20px;
}
</style>
