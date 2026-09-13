# Visio Academic Diagrams

**让 AI 先理解论文中的问题、方法与证据，再把正确的关系转化为可在 Microsoft Visio 中实现的科研图。**

`v0.2.0` · 中文优先 · Agent Skills 目录结构 · Python 3.10+ 可选静态检查 · MIT（原创部分）

[快速开始](#快速开始) · [核心能力](#核心能力) · [工作流程](#工作流程) · [示例](examples/README.md) · [AI 入口](SKILL.md) · [功能索引](references/INDEX.md) · [验证记录](VALIDATION.md) · [English](README.en.md)

---

## 项目定位

`visio-academic-diagrams` 是一个面向科研场景的 **Agent Skill + 可检索知识库**。

它的目标不是让 AI 只会“画几个框和箭头”，而是建立一条完整链路：

```text
论文 / 方法草稿 / 伪代码 / 公式 / 研究提纲
        ↓
理解研究问题、假设、方法、证据、局限与术语
        ↓
建立 paper-model.json：带来源定位的论文内容模型
        ↓
选择真正适合的图种，并建立 figure-plan.json
        ↓
确定节点、关系、图层、尺寸、字号、连接线与版面
        ↓
生成可执行的 Visio 操作步骤
        ↓
用户在 Visio 中实现
        ↓
截图 / 源文件复核 → 修改 → 论文或报告输出
```

同一篇论文不应该被机械地塞进一张流程图。

本 Skill 会区分不同表达任务，例如：

- **阅读思维导图**：解释“论文讲了什么”
- **方法流程图**：解释“方法如何执行”
- **数据流 / 系统图**：解释“信息如何传递”
- **概念关系图**：解释“变量、机制与概念如何关联”
- **证据图 / 证明依赖图**：解释“结论依赖哪些证据或前提”

这些图可以共享同一份研究内容模型，但不会把“包含关系”“相关关系”“数据流”和“控制流”错误地画成同一种箭头。

---

## 核心能力

### 1. 先理解论文，再设计图

Skill 会先提取：

- 研究问题与研究对象
- 背景缺口
- 假设与前提
- 输入、输出与关键变量
- 算法 / 方法步骤
- 关键公式与参数
- 数据来源与验证方案
- 主要结果与局限
- 论文明确陈述、合理推断、设计建议和未知信息

科学陈述会区分：

```text
explicit   原文明确陈述
inferred   基于材料的推断
proposed   AI提出的设计建议
unknown    当前材料无法确定
```

目标是避免为了排版而补造论文中不存在的步骤、条件、数据或结论。

### 2. 不先画图，而是先选对图

AI 会先回答：

> 这张图究竟要让读者理解什么？

再选择适合的表达形式。

| 研究内容 | 更适合的图 |
|---|---|
| 算法执行步骤 | 流程图 |
| 论文阅读结构 | 思维导图 |
| 模块与接口 | 系统架构图 |
| 输入—处理—输出 | 数据管线图 |
| 理论变量关系 | 概念关系图 |
| 假设、证据与结论 | 证据图 |
| 定理或结论依赖 | 证明依赖图 |

复杂研究可以拆成多个互补视图，而不是追求一张“大而全”的图。

### 3. Visio 功能知识导航

当前版本将 Visio 能力组织为 **26 个功能族、220 个能力 / 专题入口**，覆盖页面与画布、Shape / Stencil / Master、文本、尺寸与位置、Connector、连接点、Align / Distribute、Container、Layer、Brainstorming、Flowchart、数据关联、Data Graphics、ShapeSheet、自动化、API、导出与出版准备。

机器可读入口：

- [功能族图谱](references/feature-atlas.md)
- [能力表](assets/capabilities.json)
- [扩展操作索引](references/operations-extended-index.md)

> `document-backed` 表示本仓库已有官方文档依据和操作路线，但不等于已经在你的具体 Visio 版本中实机验证。  
> `index-only` 表示它是检索入口；需要先查精确官方章节，再给出具体菜单或 API 参数。

### 4. 把图设计翻译为可执行 Visio 步骤

输出不会停留在“在 Visio 里画一个流程图”，而会尽量具体到对象、前置条件、菜单、参数、预期结果、检查与回退。

---

## 工作流程

### 第 1 步：理解研究材料

先读：

- [论文理解协议](references/paper-understanding.md)
- [论文类型](references/paper-types.md)

建立 `paper-model.json`，记录研究事实、证据定位、推断与未知项。

### 第 2 步：确定图的任务

先用一句话定义：

> 这张图希望读者在 10–20 秒内理解什么？

再使用：

- [图种选择](references/diagram-selection.md)
- [关系语义](references/graph-semantics.md)

建立 `figure-plan.json`。

### 第 3 步：映射到 Visio 功能

按任务读取：

- [科研到 Visio 映射](references/research-to-visio.md)
- [页面](references/operations-page.md)
- [形状](references/operations-shapes.md)
- [连接](references/operations-connectors.md)
- [布局](references/operations-layout.md)
- [文本](references/operations-text.md)
- [结构化对象](references/operations-structure.md)
- [高级功能](references/operations-advanced.md)

### 第 4 步：形成布局规格

记录节点 ID、形状类型、宽高、坐标、字号、线宽、连接关系、图层、页面尺寸与导出条件。

### 第 5 步：在 Visio 中实现并复核

复核顺序：

1. 科研逻辑
2. 节点与关系
3. 图形语义
4. 对齐与间距
5. 字号与线宽
6. 最终物理尺寸
7. 黑白 / 灰度可读性
8. 导出格式与目标期刊要求

---

## 快速开始

### 方法 A：克隆仓库

```bash
git clone https://github.com/Zhang646967/visio-academic-diagrams.git
```

然后将整个 `visio-academic-diagrams` 文件夹放入支持本地 Agent Skills 的目录，例如：

```text
项目目录/.agents/skills/visio-academic-diagrams/
```

或：

```text
$HOME/.agents/skills/visio-academic-diagrams/
```

Windows 常见个人目录：

```text
%USERPROFILE%\.agents\skills\visio-academic-diagrams\
```

不要只复制 `SKILL.md`。`references/`、`assets/`、`examples/`、`scripts/` 等配套内容也需要保留。

### 方法 B：普通聊天中临时使用

将仓库压缩后上传给具备文件读取能力的 AI，并要求它：

```text
先读取 SKILL.md，
然后按照其中的任务路由按需读取 references、assets 和 examples。
```

上传文件只代表当前对话可用，不等于安装成永久技能。

---

## 推荐提示词

### 论文 → 思维导图 / 流程图

```text
使用 $visio-academic-diagrams。

先阅读我提供的论文，明确实际读到的范围、
研究问题、假设、方法、证据、结果与局限。

先建立论文内容模型，再判断最适合的图种。
如果一张图无法准确表达，请拆成互补视图。

对于最终推荐的图：
1. 给出节点和关系表；
2. 解释每条箭头的科学含义；
3. 给出最终尺寸与布局方案；
4. 给出逐步 Visio 操作；
5. 每一步写明对象、菜单、参数、预期结果、检查与回退。
```

### 算法 / 优化方法 → 方法流程图

```text
使用 $visio-academic-diagrams。

根据下面的方法草稿检查：
输入、输出、初始化、循环、分支、停止条件、
失败路径以及数据依赖。

区分控制流和数据流。
不要因为排版方便而补造方法步骤。

然后设计适合论文正文的流程图，
给出节点/边表、布局、毫米尺寸和逐步 Visio 操作。
```

### 审查已有科研图

```text
使用 $visio-academic-diagrams 审查这张图。

先检查科研逻辑与关系语义，
再检查排版、字号、线宽、间距和导出风险。

最后只针对发现的问题给出 Visio 修复步骤。
没有源文件时，不要声称已经验证连接点、隐藏数据或字体嵌入。
```

---

## 示例

- [Paper → Multi-view](examples/paper-to-multiview/README.md)：同一研究内容分别形成阅读思维导图和算法流程图。
- [Association ≠ Causation](examples/association-not-causation/README.md)：演示为什么相关关系不能自动画成因果箭头。
- [Proof Dependencies](examples/proof-dependencies/README.md)：演示结论、引理与前提之间的依赖表达。
- [Iterative Optimization](examples/iterative-optimization/walkthrough.zh-CN.md)：包含详细 Visio 操作步骤、尺寸和检查点的迭代流程示例。

所有示例均为教学材料，不代表真实论文结果。

---

## 科研制图原则

本项目不会把“SCI 风格”理解为一个固定模板。真正的出版要求取决于目标期刊、单栏 / 双栏宽度、最小可读字号、文件格式、位图分辨率、线宽、字体政策以及彩色 / 灰度要求。

因此：

- 不默认 A4 是论文插图尺寸
- 不把截图作为默认终稿
- 不把 SVG / PDF 后缀自动视为“完全矢量”
- 不把一种出版社的要求套用到所有期刊

相关入口：

- [出版配置](references/publication-profiles.md)
- [导出操作](references/operations-export.md)
- [审图清单](references/review-checklist.md)

---

## 功能与可信边界

当前版本：

- 26 个功能族
- 220 个能力 / 专题入口
- 57 项来源登记
- 74 项单元测试
- 4 组主要结构化示例

这些数字描述的是**本仓库当前的知识条目和测试资产**，不是 Microsoft Visio 的官方功能总数。

另外：

- 静态测试不能证明真实 Visio GUI 行为
- 截图审查不能验证隐藏数据和字体嵌入
- 论文理解不能替代领域专家判断
- 结构校验不能证明因果、定理或实验设计正确
- 具体菜单可能受版本、平台、许可证和语言影响

完整范围见 [VALIDATION.md](VALIDATION.md)。

---

## 项目结构

```text
SKILL.md                       AI任务路由与核心约束
references/                    论文理解、图种、Visio功能、操作与出版规则
assets/                        能力表、Schema、模板和结构化记录
examples/                      原创教学材料和完整操作示例
scripts/                       检索、结构校验和发布辅助脚本
tests/                         自动测试与人工验收场景
docs/                          架构、安装、维护和发布说明
agents/openai.yaml             可选宿主显示配置
README.md / README.en.md       中文 / 英文项目说明
LICENSE                        原创部分许可证
SOURCES-NOTICE.md              外部来源与版权边界
VALIDATION.md                  验证范围与已知限制
```

---

## 本地检查

在仓库根目录可运行：

```bash
python scripts/validate_package.py
python -m unittest discover -s tests -v
python scripts/validate_research.py   examples/paper-to-multiview/paper-model.json   examples/paper-to-multiview/algorithm-plan.json
```

这些检查用于验证文件结构、Schema、引用和部分内部一致性，不等价于 Visio GUI 实机测试或科研正确性认证。

---

## 版本状态

当前公开版本：

```text
v0.2.0
```

后续更新重点包括：

- 扩展 Visio 功能族的文档覆盖
- 增加真实论文的匿名化评测案例
- 增加更多科研图类型
- 增强桌面版 / 网页版 / 许可差异提示
- 增加更系统的科研制图审查规则

---

## License

本仓库原创文档、脚本与教学示例采用 [MIT License](LICENSE)。

Microsoft Visio、Microsoft、期刊指南及外部文档的商标、版权和其他权利归各自权利人所有。  
本项目不是 Microsoft、OpenAI 或任何期刊的官方产品。

外部来源边界见 [SOURCES-NOTICE.md](SOURCES-NOTICE.md)。
