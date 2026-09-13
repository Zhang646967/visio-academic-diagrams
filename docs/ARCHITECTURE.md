# 设计架构与不变量

## 设计目标
把功能知识与科研理解分层，避免“知道哪个按钮”被误当成“理解了论文”。核心入口小于500行，按任务取模块，不把所有220条能力塞进上下文。[A01]

## 三个可检查的中间产物

| 产物 | 契约 | 作用 | 不负责 |
|---|---|---|---|
| paper-model | [Schema](../assets/paper-model.schema.json) | 输入范围、论文项、证据定位、带类型关系、未知项 | 自动证明原文陈述为真 |
| figure-plan | [Schema](../assets/figure-plan.schema.json) | 图目标、来源关联、关系语义、关键项与省略项、图注 | 毫米坐标或某款软件菜单 |
| layout | [Schema](../assets/diagram-spec.schema.json) | 形状、布局、连线、文字、输出尺寸 | 实际字体、连接粘附或完整期刊合规 |

内容ID在多图间稳定；节点ID在图内稳定。重新排版不应重写科学关系。
语义与排版通过figure_plan_id、节点ID、边ID和标签匹配。控流程允许条件边，依赖图可显式反转论文的“依赖于”方向，但不得静默反转。
源内容的explicit/inferred/proposed/unknown不能在投影时变得更确定。这个状态检查不能检测自然语言偷偷改写成强结论，仍需人工复述核对。

## 验证的不同层次
`validate_research.py`检查声明结构与来源；`validate_spec.py`检查名义几何；`validate_bundle.py`检查两者是否漂移。`shape_errors`仅实现本包两份研究Schema用到的JSON Schema子集，不是通用JSON Schema引擎。
合成示例用于可重复的错误检测；真实论文的准确理解应采用学科专家核对、双向复述和用户审查。`tests/scenarios.md`是尚待执行的行为评测设计，不是已经完成的模型评测。

## 版本与兼容
旧几何Schema1.0保存在[单独文件](../assets/diagram-spec-v1.0.schema.json)，当前几何1.1扩展图种并保留旧示例。论文与语义方案Schema独立为1.0。技能发行版本为0.2.0，三者不要混为一谈。

## 知识更新
修改操作必须先核验官方章节、适用版本和生命周期，更新sources/capabilities；只有概览依据的条目继续保持index-only。维护流程见[知识维护](../references/knowledge-maintenance.md)。
