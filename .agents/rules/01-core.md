---
trigger: always_on
---

# 01_core — Demo Execution Constitution

## Mission
我们在做一个产品 demo：FastAPI + Vue3 + MySQL/Redis（可用 docker/本地替代）。
目标：AI 尽可能自主完成“计划→实现→测试→修复→提交”的闭环。

## Definition of Done (DoD)
任何任务只有满足以下条件才算完成：
1) 代码已实现，并且不引入明显技术债
2) 已补齐/更新测试（至少单元测试 + 关键路径 smoke test）
3) 运行 verify 流程全部通过（见 /verify 工作流）
4) 生成一次 git commit（见 /commit 或 /verify-and-commit）
5) 输出简短变更摘要（做了什么、改了哪些文件、如何验证）

## Git Discipline
- 所有改动必须可追溯：不要只改不提交
- Commit message 使用 Conventional Commits（feat/fix/chore/refactor/test/docs）
- 原子提交：一次 commit 只做一件事（一个 feature / 一个 bugfix）

## Work Style
- 先读代码再改：先定位入口文件、配置、依赖关系
- 先小步：优先小 PR / 小 commit
- 避免“想当然”：遇到不确定的配置/命令，先检查 repo 中现有脚本/README/Makefile

## Shared Team Guide
@TEAM_GUIDE.md