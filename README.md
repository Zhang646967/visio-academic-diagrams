# Visio Academic Diagrams

**让 AI 先理解论文中的问题、方法与证据，再把正确的关系转成可在 Visio 中实现的图。**

`v0.2.0` · 中文优先 · Agent Skills 目录格式 · Python 3.10+ 可选静态检查 · 原创部分 MIT

[快速使用](#快速使用) · [功能边界](#功能边界) · [示例](examples/README.md) · [AI入口](SKILL.md) · [功能索引](references/INDEX.md) · [验证记录](VALIDATION.md) · [公开发布](docs/GITHUB-PUBLISH.md) · [English](README.en.md)

## 这是什么

一个可按需读取的科研制图 Skill 与知识库。它不是 Visio 插件、桌面控制程序或论文自动理解模型，也不是微软教程的全文镜像。

它把原来的“制图教程 → 操作指导”改造成：

```text
论文、方法草稿、伪代码、公式或研究提纲
    ↓ 阅读范围、术语、假设、论点、方法、证据、局限
paper-model.json：带来源定位的论文内容模型
    ↓ 图的目标、节点、关系类型、必要内容、明确省略项
figure-plan.json：与软件无关的语义图方案
    ↓ 选择真正需要的 Visio 功能，核对版本和许可证
layout.json：形状、尺寸、中心坐标、连线、字号与导出条件
    ↓ 每一步都有对象、菜单、数值、预期结果和检查方式
你在 Visio 实现 → 截图/源文件审查 → 修改 → 投稿输出
```

同一篇论文可以生成不同视图，而不是把所有内容挤进一张流程图：**阅读思维导图**解释“这篇论文讲什么”，**方法流程图**解释“它如何执行”，**证据图或证明依赖图**解释“为什么可以得出结论”。视图共享内容 ID，但不共享错误的箭头语义。

## v0.2.0 的主要变化

| 方面 | 已实现 |
|---|---|
| Visio 知识组织 | 26 个功能族、220 个能力/专题入口；54 项有文档支持的操作路线，166 项为需继续查证的专题索引 |
| 功能理解 | 不只记菜单：解释形状、模具、主控形状、实例、连接、容器、图层、数据关联与自动化的区别 |
| 论文理解 | 按研究问题、输入输出、假设、方法、贡献声明、证据、结果、局限建立内容模型；标明已读和未读范围 |
| 论文类型 | 算法、机器学习、实证、理论、综述、定性、系统和其他研究分别选取适当的阅读与制图策略 |
| 科学语义 | 区分层级、控制流、数据流、依赖、相关、因果、证据和消息；不为美观虚构步骤或结论 |
| 可追溯性 | 节点与边关联内容 ID/证据 ID；区分原文陈述、推断、设计建议、未知项 |
| 示例与检查 | 原版逐步实例 + 3 组原创合成材料、4 组论文/语义图/坐标配套示例；74 项自动测试 |
| 可维护性 | 57 项来源登记、版本/生命周期提示、离线检索、原始来源阅读深度、SHA-256 发布文件清单 |

**这些是本仓库的条目数，不是 Visio 的功能总数，也不是“已掌握全部功能”的证明。** 具体范围见[功能边界](#功能边界)。

## 快速使用

### 作为本地 Agent Skill

保留整个文件夹，目录名为 `visio-academic-diagrams`。在支持本地技能的 Codex 环境中放入以下位置之一，避免安装重复副本：[A01][A02]

```text
项目目录/.agents/skills/visio-academic-diagrams/SKILL.md
或
$HOME/.agents/skills/visio-academic-diagrams/SKILL.md
```

Windows 的个人目录通常是 `%USERPROFILE%\.agents\skills\`。`SKILL.md` 的同级 `references/`、`assets/`、`examples/` 和 `scripts/` 不能丢失。

在 Codex CLI/IDE 的技能选择器中选择本技能，或在请求中写 `$visio-academic-diagrams`。普通聊天可上传整个包，让具备文件读取能力的 AI 先解压读取 `SKILL.md`，再按需读取索引和模块。上传一次不代表永久记忆，也不代表安装成账户级插件。[A02]

### 用于阅读论文

```text
使用 $visio-academic-diagrams。
先读取我提供的论文，明确已读范围、未读范围、研究问题和论证结构。
建立带页码/章节定位的内容模型，不要把推断写成原文事实。
为理解论文设计一张思维导图，并说明父子关系和跨主题关联各代表什么。
再判断这篇论文是否还需要方法流程图、证据图或证明依赖图。
我使用的 Visio 环境是：……
```

### 用于论文方法制图

```text
使用 $visio-academic-diagrams。
根据下面的方法草稿，先检查输入输出、算法分支、循环和终止条件。
输出：内容模型摘要、图方案、节点/边表、最终尺寸、毫米坐标和手工操作步骤。
区分算法控制流和数据依赖；所有设计建议都单独标注。
每一步写清选择哪个对象、打开哪个菜单、输入什么数值、如何检查。
期刊尚未确定，不要把通用样式冒充期刊强制标准。
方法如下：……
```

### 用于现有图审查或功能查找

```text
使用 $visio-academic-diagrams 检查这张图。
先检查科研逻辑和关系，再检查排版；最后给对应 Visio 修复步骤。
没有源文件时，不要声称已经验证真实粘附、字体嵌入或隐藏数据。
```

无需运行 Python 就能使用文字 Skill。需要离线查功能时：

```bash
python scripts/lookup_capability.py "思维导图"
python scripts/lookup_capability.py "ShapeSheet" --limit 8
python scripts/lookup_capability.py "LC01" --json
```

`index-only` 的结果会指向官方检索路线；AI 必须先取得具体章节，不能凭索引捏造操作步骤。

## 从一段方法形成两张不同的图

[paper-to-multiview 示例](examples/paper-to-multiview/README.md) 使用原创教学方法：初始化、评价候选、判断预算、更新并循环。它**没有**真实实验数据，也不宣称全局最优。

阅读图围绕“问题、方法、证据和局限”组织主题，父子线不表示算法顺序。算法图则保留判断的 Yes/No 出口和正确回边。两张图关联同一份内容模型，因此改动一个方法事实时，可以检查两张图是否同时更新。

另有[相关不等于因果](examples/association-not-causation/README.md)和[证明依赖](examples/proof-dependencies/README.md)示例，演示为什么不能把每条关系都画成普通流程箭头。

原版[16步迭代流程操作](examples/iterative-optimization/walkthrough.zh-CN.md)仍保留，用于查看详细菜单、数值和检查点的交付样式。所有坐标都是设计规格，**没有附加假装已经在 Visio 渲染的图片或 `.vsdx` 文件**。

## 功能边界

### “所有功能”采用导航覆盖，不采用虚假的穷尽承诺

[功能族说明](references/feature-atlas.md)与[机器可读能力表](assets/capabilities.json)提供从常用到高级功能的入口，包括页面、形状、连接、文本、布局、脑图、专用图种、数据、协作、导出、ShapeSheet 和 API。

`document-backed` 表示本包有官方依据和操作路线，**不表示用户版本实测**。`index-only` 表示仅建立功能含义、使用场景及官方查询路线，不能直接给精确菜单。不同版别、许可、语言、平台和更新阶段需另行核实。

微软的脑图文档区分桌面 Brainstorming 与网页操作[M30][M31]。Excel 的 Visio Data Visualizer 加载项已在官方退役安排中于 **2026-03-02** 停止服务；这与桌面版 Data Visualizer 模板不是同一功能[M23][M42][M43]。退役入口保留用于识别旧教程，不用于新操作方案。

### “任意论文”采用通用阅读协议，不声称理解保证

它可以接收不同学科材料并据此选择策略，但复杂专业结论仍须结合原文、专业知识和作者核对。只读取摘要不能生成可复现级算法；数据不全不能补造结果；原文假说即使是直接陈述，也仍是“假说”。

脚本检查声明的结构、来源 ID 和关系类型，**不会判断引文是否真正支持某个陈述**，不会证明定理、验证因果识别、识别所有数据泄漏或替代同行评议。见[论文理解协议](references/paper-understanding.md)。

### “符合论文标准”以目标期刊为条件

本包将通用设计建议与 IEEE、Elsevier、PLOS ONE 等来源快照分开。字号、线宽、图宽、分辨率和允许格式需要按最终投稿指南核验；不把 A4 当单栏图宽，不把截图当默认终稿，不把 SVG/PDF 后缀当内容完全矢量的证明。[P01]–[P09] 对应条目见[来源登记](references/source-register.md)及[出版配置](references/publication-profiles.md)。

## 目录与维护入口

```text
SKILL.md                      AI的任务路由与约束
references/                   论文理解、功能机制、操作、图种、期刊、审图
assets/                       功能/来源登记、Schema、输入与输出模板
examples/                     原创材料、语义图、坐标和手工步骤
scripts/                      检索、结构检查、打包及显式GitHub发布
agents/openai.yaml            可选宿主显示配置
tests/                       单元测试、人工评测场景、真实运行记录
docs/                        架构、发布、维护及历史记录
README.md / README.en.md      中文与英文使用说明
LICENSE / SOURCES-NOTICE.md    原创许可与外部来源边界
manifest.sha256               经审查的发布文件清单与哈希
```

阅读入口：[AI工作流](SKILL.md) · [论文分类](references/paper-types.md) · [图种选择](references/diagram-selection.md) · [科研到Visio映射](references/research-to-visio.md) · [更新方法](references/knowledge-maintenance.md)。

## 检查与构建

在技能根目录运行。工具仅用 Python 标准库，无需额外安装 Python 包；Visio 人工试做仍需用户自己的软件环境。

```bash
python scripts/validate_package.py
python -m unittest discover -s tests -v
python scripts/validate_research.py examples/paper-to-multiview/paper-model.json examples/paper-to-multiview/algorithm-plan.json
python scripts/validate_bundle.py examples/paper-to-multiview/paper-model.json examples/paper-to-multiview/algorithm-plan.json examples/paper-to-multiview/algorithm-layout.json
python scripts/build_release.py --output ../visio-academic-diagrams-v0.2.0.zip
```

`build_release.py` 只打包清单内文件，并拒绝覆盖已有 ZIP。修改技能后必须审查并刷新清单；不能忽略哈希失配。静态检查和打包本身不联网。`validate_spec.py --output` 可显式写入一个新报告，其他校验默认只读。

当前 **74 项单元测试通过，4 组新示例通过配套检查**。未完成 Visio GUI 试做、真实论文专家评审、独立模型任务成功率评估或 GitHub 在线发布测试。完整范围见 [VALIDATION.md](VALIDATION.md)；不能把单元测试通过率作为科研理解准确率。

## 发布到 GitHub

本目录已准备为公开仓库根目录；本地包的存在不表示远程仓库已经创建。见[发布说明](docs/GITHUB-PUBLISH.md)。发布需要你本机的 Git、GitHub CLI 及有建仓权限的账户。

```bash
# 默认仅检查，无联网、无上传。
python scripts/publish_github.py --owner YOUR_GITHUB_LOGIN --repo visio-academic-diagrams

# 审查文件并在本机完成 gh 认证后，明确执行公开发布。
python scripts/publish_github.py --owner YOUR_GITHUB_LOGIN --repo visio-academic-diagrams --public --execute
```

脚本核对登录账户，仅复制哈希清单里的文件到隔离临时目录，创建**新**仓库，不覆盖同名仓库，不强制推送。上传后检查公开可见性和提交 SHA；只有成功才打印确认链接。不要在聊天、README 或公开 issue 中粘贴 token。

## 贡献与许可

先阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [SECURITY.md](SECURITY.md)。扩充功能应增加准确来源和可审查案例，而不是只增加条目数。真实论文和审稿材料默认放在此公开仓库之外。

本项目原创文档、代码和合成示例采用 [MIT](LICENSE)；微软、出版机构和其他外部内容仍遵守各自权利与条款，参见 [SOURCES-NOTICE.md](SOURCES-NOTICE.md)。本项目并非 Microsoft、OpenAI 或任何期刊的官方产品。来源编号 `[Mxx]`、`[Pxx]`、`[Rxx]`、`[Axx]` 的标题、链接和阅读深度见[来源登记](references/source-register.md)。
