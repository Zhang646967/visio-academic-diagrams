# 同一篇材料，生成两种互补视图

所有内容来自[原创合成短文](synthetic-paper.md)，不是用户论文。例子故意不提供实测效果或全局最优证明，以测试AI是否会补造结论。

[内容模型](paper-model.json)保留问题、前提、控制逻辑和局限。
[阅读脑图](mindmap-plan.json)回答“研究什么、怎样做、没有证明什么”；[算法图](algorithm-plan.json)回答“哪个条件下走哪个分支”。
两张图通过item ID共享同一含义。脑图的主题分组是proposed编辑组织，不是作者的执行步骤。

## 操作和参数
脑图优先按[原生路线](../../references/operations-mindmap.md)建立父子结构。需固定版式时，用[mindmap-layout.json](mindmap-layout.json)中的10个节点、9条层级边和毫米坐标手工绘制；这不是原生Auto-Arrange的预测坐标。
算法用[algorithm-layout.json](algorithm-layout.json)，其几何沿用并回归测试v0.1.0的布局。详细16步操作见[继承示例](../iterative-optimization/walkthrough.zh-CN.md)。内容来源以本目录的合成短文为准。

## 验证
在仓库根运行：
```bash
python scripts/validate_bundle.py examples/paper-to-multiview/paper-model.json examples/paper-to-multiview/mindmap-plan.json examples/paper-to-multiview/mindmap-layout.json
python scripts/validate_bundle.py examples/paper-to-multiview/paper-model.json examples/paper-to-multiview/algorithm-plan.json examples/paper-to-multiview/algorithm-layout.json
```
静态检查不能测量真实文字或Visio自动路由，用户需按检查点实际绘制并反馈。
