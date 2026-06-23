# ANSYS 接触分析最佳实践

> 来源: ANSYS Mechanical APDL Contact Technology Guide (v241)
> 整理: cae-agent 项目

---

## 接触算法选择

| 算法 | 适用场景 | 注意事项 |
|------|---------|---------|
| Augmented Lagrange | 通用，默认推荐 | 对刚度敏感度低 |
| Pure Penalty | 简单接触，计算快 | 刚度需要调试 |
| Normal Lagrange | 零穿透要求 | 可能引起收敛问题 |
| MPC | 绑定接触、刚柔耦合 | 线性求解，无穿透 |

---

## 接触刚度设置

- **默认法向刚度因子 FKN = 1.0**：适用于大多数绑定/不分离接触
- **FKN = 0.1 ~ 0.5**：弯曲主导问题，避免刚度过大引起震颤
- **FKN = 0.01 ~ 0.1**：接触穿透过大时的调试起点
- **每子步更新刚度 (KEYOPT(10)=2)**：大变形问题推荐

---

## 常见接触错误及排查

### 接触穿透过大 (Contact Penetration)
1. 增大 FKN 法向刚度因子
2. 检查接触/目标面方向是否正确（翻转法向）
3. 加密接触区网格
4. 检查初始间隙 Pinball 半径设置

### 接触震颤 (Contact Chatter)
1. 减小 FKN
2. 切换到 Augmented Lagrange 算法
3. 增加子步数
4. 检查是否发生刚体位移

### 接触不收敛
1. 减小初始时间步
2. 启用自动时间步 (AUTOTS,ON)
3. 检查接触初始状态（是否 OPEN / FAR）
4. 使用接触稳定阻尼 (FDAMP / FDMN)

---

## Named Selection 前缀命名规范

适合与 `batch-contact` 技能配合使用：

```
NS_SRC_<特征名>    ← 源面 (Contact/Source)
NS_TGT_<特征名>    ← 目标面 (Target)

示例:
NS_SRC_BOLT_01     NS_TGT_BOLT_01   → AUTO_CONTACT_BOLT_01
NS_SRC_FLANGE_A    NS_TGT_FLANGE_A  → AUTO_CONTACT_FLANGE_A
```

---

## 参考

- ANSYS Mechanical APDL Contact Technology Guide (PDF: book/v241/ANSYS_Mechanical_APDL_Contact_Technology_Guide.pdf)
- ANSYS Mechanical APDL Structural Analysis Guide (PDF: book/v241/ANSYS_Mechanical_APDL_Structural_Analysis_Guide.pdf)
