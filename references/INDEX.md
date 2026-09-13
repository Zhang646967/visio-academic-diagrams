# 功能与任务索引 — v0.2.0

先按任务读模块，再查能力ID；不要每次加载全部索引。完整条目在[能力表](../assets/capabilities.json)，功能含义在[功能族说明](feature-atlas.md)。

54项document-backed拥有文档支持路线，166项index-only只有待查证专题路线；两者均未进行GUI实测。版本适用性和生命周期必须另查。

## 任务路由

| 任务 | 最小阅读集 |
|---|---|
| 读论文，提炼思路 | [理解协议](paper-understanding.md)、[论文类型](paper-types.md)、[关系语义](graph-semantics.md) |
| 不知道该画什么图 | [图种选择](diagram-selection.md)、[科研到Visio](research-to-visio.md) |
| 思维导图、脑图 | [脑图设计](recipes-mindmap.md)、[脑图操作](operations-mindmap.md) |
| 算法循环、流程 | [流程图](recipes-flowchart.md)、[连接线](operations-connectors.md) |
| 数据管线与系统 | [管线](recipes-pipeline.md)、[架构](recipes-architecture.md) |
| 论点、证据、证明 | [证据与依赖图](recipes-evidence-proof.md) |
| 多张图共同讲论文 | [多视图一致性](multi-view-consistency.md) |
| 精确尺寸、字线 | [页面](operations-page.md)、[形状](operations-shapes.md)、[文字](operations-text.md)、[布局](operations-layout.md) |
| 分组、图层、数据 | [结构](operations-structure.md)、[扩展操作](operations-advanced.md) |
| 网页版 | [版本环境](environment.md)、[网页差异](operations-web.md) |
| 冷门/高级功能 | [机制](visio-mental-model.md)、[高级索引](advanced-index.md)、[扩展索引](operations-extended-index.md) |
| 投稿与审图 | [期刊](publication-profiles.md)、[导出](operations-export.md)、[审图](review-checklist.md) |

## 文档操作入口

| ID | 能力 | 模块 |
|---|---|---|
| PG01 | 新建基础流程图 | [operations-page.md](operations-page.md) |
| PG02 | 自定义绘图页 | [operations-page.md](operations-page.md) |
| PG03 | 拟合绘图边界 | [operations-page.md](operations-page.md) |
| PG04 | 打印纸设置 | [operations-page.md](operations-page.md) |
| PG05 | 保存可编辑源文件 | [operations-page.md](operations-page.md) |
| SH01 | 拖入模板形状 | [operations-shapes.md](operations-shapes.md) |
| SH02 | 精确宽高 | [operations-shapes.md](operations-shapes.md) |
| SH03 | 精确中心位置 | [operations-shapes.md](operations-shapes.md) |
| SH04 | 旋转 | [operations-shapes.md](operations-shapes.md) |
| SH05 | 填充和轮廓 | [operations-shapes.md](operations-shapes.md) |
| SH06 | 保存个人模板 | [operations-shapes.md](operations-shapes.md) |
| LY01 | 对齐 | [operations-layout.md](operations-layout.md) |
| LY02 | 均匀分布 | [operations-layout.md](operations-layout.md) |
| LY03 | 自动对齐及间距 | [operations-layout.md](operations-layout.md) |
| LY04 | 网页版对齐与分布 | [operations-layout.md](operations-layout.md) |
| TX01 | 节点文字 | [operations-text.md](operations-text.md) |
| TX02 | 字体与对齐 | [operations-text.md](operations-text.md) |
| TX03 | 独立注释 | [operations-text.md](operations-text.md) |
| TX04 | 调整文本块位置 | [operations-text.md](operations-text.md) |
| TX05 | 连接线标签 | [operations-text.md](operations-text.md) |
| CN01 | 添加连接线 | [operations-connectors.md](operations-connectors.md) |
| CN02 | 固定连接点或动态连接 | [operations-connectors.md](operations-connectors.md) |
| CN03 | 线型与箭头 | [operations-connectors.md](operations-connectors.md) |
| CN04 | 直角与反馈走线 | [operations-connectors.md](operations-connectors.md) |
| CN05 | 粘附开关 | [operations-connectors.md](operations-connectors.md) |
| CN06 | 增加连接点 | [operations-connectors.md](operations-connectors.md) |
| CN07 | AutoConnect | [operations-connectors.md](operations-connectors.md) |
| ST01 | 建立容器 | [operations-structure.md](operations-structure.md) |
| ST02 | 解散容器 | [operations-structure.md](operations-structure.md) |
| ST03 | 分配图层 | [operations-structure.md](operations-structure.md) |
| ST04 | 图层属性 | [operations-structure.md](operations-structure.md) |
| ST05 | 查看形状数据 | [operations-structure.md](operations-structure.md) |
| ST06 | 导入并刷新外部数据 | [operations-structure.md](operations-structure.md) |
| EX01 | 导出PDF | [operations-export.md](operations-export.md) |
| EX02 | 导出图形格式 | [operations-export.md](operations-export.md) |
| EX03 | 网页导出 | [operations-export.md](operations-export.md) |
| WB01 | 网页画布 | [operations-web.md](operations-web.md) |
| WB02 | 网页形状格式 | [operations-web.md](operations-web.md) |
| WB03 | 网页容器 | [operations-web.md](operations-web.md) |
| WB04 | 网页BPMN门槛 | [operations-web.md](operations-web.md) |
| PJ01 | 时间线里程碑和区间 | [operations-advanced.md](operations-advanced.md) |
| DA05 | CSV/Excel过程表到节点关系 | [operations-advanced.md](operations-advanced.md) |
| DA06 | 桌面Data Visualizer双向同步 | [operations-advanced.md](operations-advanced.md) |
| QA01 | 结构化图规则集和问题列表 | [operations-advanced.md](operations-advanced.md) |
| MM01 | 新建桌面头脑风暴图 | [operations-mindmap.md](operations-mindmap.md) |
| MM02 | 增加同级与子主题 | [operations-mindmap.md](operations-mindmap.md) |
| MM03 | 批量增加子主题 | [operations-mindmap.md](operations-mindmap.md) |
| MM04 | 大纲窗口重新设定父主题 | [operations-mindmap.md](operations-mindmap.md) |
| MM05 | 自动整理与子树移动 | [operations-mindmap.md](operations-mindmap.md) |
| MM06 | 用关联线表达非层级关系 | [operations-mindmap.md](operations-mindmap.md) |
| MM07 | 新建网页版思维导图 | [operations-mindmap.md](operations-mindmap.md) |
| MM08 | 网页版新增子主题与同级主题 | [operations-mindmap.md](operations-mindmap.md) |
| MM09 | 网页版重新设定父节点 | [operations-mindmap.md](operations-mindmap.md) |
| MM10 | 网页版删除单节点与整子树区别 | [operations-mindmap.md](operations-mindmap.md) |

## 官方目录查询

运行 `python scripts/lookup_capability.py "关键词"`（技能根目录）或直接查JSON。条目保存中英文关键词、功能族、适用平台、官方查询建议、来源、科学用途与核验状态。

发现条目不足时沿微软官方目录查找具体章节，登记后再使用；不是以现有220条人为限定Visio功能边界。
