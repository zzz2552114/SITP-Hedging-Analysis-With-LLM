---
trigger: always_on
---

# 02_safety — Do Not Break My Machine

## Absolute禁止
- 禁止执行任何会删除/格式化磁盘、或大范围删除文件的命令
- 禁止清理非工作区目录
- 禁止修改用户目录、系统目录、注册表、磁盘分区相关配置

## Repo 保护文件（禁止删除/重命名）
- TEAM_GUIDE.md
- .agent/**（Rules/Workflows）
- docs/**（如存在）
如果确实需要变更，必须先在对话中说明原因，并给出替代方案。