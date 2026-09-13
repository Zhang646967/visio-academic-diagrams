# 回归示例：不能把相关性变成因果

[合成材料](synthetic-paper.md)只描述关联，无数值结果。[内容模型](paper-model.json)的关系为associated_with，[图计划](figure-plan.json)必须保持association。
[布局](layout.json)使用无箭头线，并保留“No causal conclusion”标注。
自动测试会将关系故意改为causal，确认校验器拒绝这种类型转换；这仍不能证明任意实际论文的因果判断正确。
