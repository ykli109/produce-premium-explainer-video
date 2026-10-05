# 精品知识科普视频制作 Skill

从选题到视频、可编辑资产包及本地 Codex 素材库入库，并按每轮实际证据检查与改进制作流程。

入口是 [SKILL.md](SKILL.md)。支持六种模式：`topic`、`planning`、`full-video`、`asset-pack`、`local-library-import`、`retrospective-improve`。可只执行一个阶段，也可从已完成的阶段恢复，不必每次重走全流程。

示例请求：

- “找一个大众能理解的充电知识选题，只做选题和前 20 秒规划”
- “把这条视频做完，先给关键帧和真实有声核心段”
- “用已有主片和工程生成可编辑资产包”
- “交给本地 Codex 导入指定素材库，恢复上次未完成的文件”
- “根据本轮失败和反馈检查 Skill，验证可复用修复后更新”

[阶段流程](references/production-stages.md)、[本地入库](references/local-codex-library-adapter.md) 和 [自进化机制](references/self-evolution.md) 按需读取。空白模板在 `templates/`；标准库辅助工具与单测用法见 [工具说明](references/tooling.md)。

公开仓库仅包含通用方法、空白模板、合成测试与代码。真实项目报告、私有素材、账号路径和凭据不属于 Skill 发布内容。工具不自动获取电脑权限、安装软件、上传、发布或改写 Skill；自进化更新必须有证据、授权范围与通过的回归检查。

本仓库没有自动安装或同步动作。按使用环境的技能加载方式选择此目录，能力不足时按交接模板报告阻断，不假定所有环境都具备本地 Codex 或视频生成工具。
