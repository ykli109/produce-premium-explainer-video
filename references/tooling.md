# 确定性辅助工具

这些工具只使用 Python 标准库；用当前环境获准的 Python 运行，不因工具需要而自动安装软件。它们不进行网络请求、上传、发布、本地 Codex 连接或 Skill 自动改写，也不能验证画面美感、事实正确性和实际声音体验。

从 Skill 根目录执行以下示例。路径都是示例，请替换为本次项目工作区；不要把真实运行报告或私人清单放进公共 Skill 仓库。

## 文件清单与下载回读

生成源文件清单：

```sh
python scripts/asset_manifest.py create \
  --root ./project-output/assets \
  --output ./project-output/asset-manifest.json
```

对接收或完整下载回来的目录核验同一份源清单：

```sh
python scripts/asset_manifest.py verify \
  --root ./project-output/readback \
  --manifest ./project-output/asset-manifest.json \
  --strict
```

- 每项记录规范的相对路径、字节数、SHA-256；清单必须位于被扫描目录外，避免把自己纳入自己的哈希
- 拒绝绝对路径、父目录穿越、重复条目和符号链接等不安全输入
- 缺失、大小或哈希不匹配会失败。非严格模式报告额外文件但不因此失败；`--strict` 下额外文件也失败
- 返回码：0 验证成功；1 内容不匹配；2 输入或使用错误
- 新建输出默认拒绝覆盖已有文件，使用明确的新版本路径

扫描时目录应停止并发写入，源清单必须可信。清单覆盖常规文件的内容与大小，不记录空目录、文件权限或时间戳，也不判断媒体可播性、许可或链接可访问性。工具需要输出父目录已存在，不会自动创建一套项目工作区。

核验的是当前目录的完整本地字节，不能证明它们已经来自网络。执行者须真实完成上传后的完整下载，再把该目录交给 verify。对已上传文件仅请求响应头或一段字节，不算回读。

可把 assets 目录和它旁边的清单一起装进最终 ZIP。ZIP 自身的哈希另放包外交付记录，不自引用。此工具生成 JSON 清单；交付目录示例中的 SHA256SUMS.txt 可用该 JSON 清单替代，或额外输出供人阅读的等价文本。

## 结构化运行报告

```sh
python scripts/run_report.py new \
  --run-id example-run \
  --mode planning \
  --output ./project-output/run-report.json

python scripts/run_report.py validate \
  --input ./project-output/run-report.json
```

模式使用：topic、planning、full-video、asset-pack、local-library-import、retrospective-improve。

报告分为 run、stages、checks、issues、learning_candidates、evolution、artifacts、permissions。生成时没有已通过检查；真实执行后再填充结果。重要字段：

- stages 和 checks：实际范围、状态、证据和未执行原因；pass 需要证据引用
- issues：问题、影响环节、纠正、用户反馈、严重程度及状态
- learning_candidates：项目偏好、可复用知识或临时事实，附证据及候选状态
- evolution：候选、最小 diff、结构与行为回归、版本、落盘、回滚和远端同步。structure 与 regression 为必需；regression 的 defect_evidence 和 normal_path_evidence 分别记录旧缺陷与正常路径。behavior 仅在确实不适用时可设 required=false、status=n/a，并解释理由
- artifacts 与 permissions：实际产物和本轮动作范围，不保存凭据

只列当前任务范围内的检查；不适用要说明，未执行不能冒充通过。每轮完成时要记录实际改进检查；没有候选可写 no_change 和原因，不必强行生成补丁。结构校验能拒绝字段缺失、非法状态或记录相互矛盾，但不会打开证据验证真伪，不能证明测试真的运行或视频令人满意。执行者须根据实际影响决定行为试用是否适用；不能为了绕过失败而改为不适用。失败保旧、回滚及远端同步有额外状态约束，以工具的真实错误信息为准。

返回码：0 报告结构有效；2 报告或输入无效。有效报告仍可能如实记录失败、阻断和未执行。

## 测试与 Skill 结构校验

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
```

单测在临时目录中使用合成文件，检查正常清单、内容损坏、缺失、额外文件、路径安全及报告状态。不会操作真实素材库或远端仓库。

如果环境提供 skill-creator 的 quick_validate.py，另用它验证此 Skill；不要猜它的位置或声称它包含在本仓库。还需解析 JSON、CSV、YAML并核对相对引用。缺少可用验证器或 YAML 解析依赖时，记录准确阻断，不为检查偷偷安装依赖。

独立行为试用的原始请求位于 [行为回归请求](../tests/behavior-cases.md)。它们不属于已完成测试的证明；执行后将真实范围与结果记录在项目报告。
