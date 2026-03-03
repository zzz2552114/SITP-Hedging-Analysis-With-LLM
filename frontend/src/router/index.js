import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/Home.vue"),
    meta: { title: "首页" },
  },
  {
    path: "/crawler",
    name: "Crawler",
    component: () => import("../views/Crawler.vue"),
    meta: { title: "公告爬虫" },
  },
  {
    path: "/analyzer",
    name: "Analyzer",
    component: () => import("../views/Analyzer.vue"),
    meta: { title: "LLM 分析" },
  },
  {
    path: "/companies",
    name: "Companies",
    component: () => import("../views/Companies.vue"),
    meta: { title: "公司与主营业务" },
  },
  {
    path: "/commodities",
    name: "Commodities",
    component: () => import("../views/Commodities.vue"),
    meta: { title: "商品类目" },
  },
  {
    path: "/announcements",
    name: "Announcements",
    component: () => import("../views/Announcements.vue"),
    meta: { title: "公告管理" },
  },
  {
    path: "/hedges",
    name: "Hedges",
    component: () => import("../views/Hedges.vue"),
    meta: { title: "套保明细" },
  },
  {
    path: "/compare",
    name: "Compare",
    component: () => import("../views/Compare.vue"),
    meta: { title: "渗透率统计" },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to) => {
  document.title = `${to.meta.title || "SITP"} - SITP 避险分析系统`;
});

export default router;
