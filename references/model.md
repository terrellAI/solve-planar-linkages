# 模型格式

先记录用户已确认的刚体与运动副关系。未确认的刚体归属不能写入正式求解计划，不能通过 rigid_points 着色或 rigid 操作暗中固化。示例模型的拓扑仅在对应案例内有效，不能根据点名字母向新图迁移。

所有点为二维向量，所有长度使用同一单位；输入角单位度。JSON顶层：

- `name`, `units`, `dimension_source`：名称、单位、尺寸来源。
- `fixed`：固定点字典。
- `plan`：几何构造列表。每个步骤输出唯一的新点；顺序可由已知点依赖自动整理。
- `lengths`：`[[点A,点B,长度],...]`，独立验证的刚性距离。多点刚体应包含足够的边及对角线，避免只校验生成公式。
- `rods`：绘图线段，`[[点A,点B],...]`。同一刚体可有多条绘图线段。
- `rigid_points`：用于一组刚体的着色，不负责定义约束；真正刚体关系由局部变换和距离检查表达。
- `rod_width`：所有运动杆统一宽度。
- `guides`：可选，固定或运动导杆与套筒的有限接合检查。

## 构造操作

| op | 字段 | 含义 |
|---|---|---|
| rotate | out, origin, local, ratio=1, phase_deg=0 | origin + R(ratio·θ+phase)·local |
| circles | out, p, q, r, s, branch | 已知圆心p/q和半径r/s的两圆交点 |
| circle_line | out, p, r, q, v, branch | 圆心p与固定直线q+tv交点，v自动归一化 |
| rigid | out, origin, known, known_local, target_local | 用已知方向恢复局部坐标架并变换目标点 |
| project | out, p, q, v | 点p到固定直线q+tv正交投影，仅用于确有此约束的运动副组合 |

`circles` 的 branch=+1 表示交点在从p指向q的左侧；`circle_line` 的+1表示从垂足沿+v方向。初始装配决定分支，不能逐帧贪心换根。

`rigid` 用 known_local 的方向定义局部横轴；其模长不参与缩放。若 known 是刚体上的固定铰点，必须在 lengths 中另行验证 origin-known 距离。若 known 是杆上的滑动铰点，只借其方向定向，不添加固定长度约束。

## 有限导杆

固定导杆：
```json
{"point":"F","origin":[0,0],"axis":[1,0],"lo":90,"hi":230,"sleeve_length":24,"rod_width":8,"hole_width":10}
```

运动导杆：把 origin/axis 换成 `origin_point` 和 `through_point`；轴为两点连线单位方向。lo/hi为沿轴相对原点的接合范围，可以为负。它描述滑块沿杆的套筒，不等同于所有槽形实体。

检查 t±sleeve_length/2∈[lo,hi]，孔宽必须大于杆宽。导杆的绘图实体端点也应覆盖该接合范围。

## 能力边界

构造计划仍需根据刚体与R/P副人工/代理推导。脚本不处理任意高阶闭环、空间机构、力学、接触动力学。完整任意刚体/运动副图自动分解、通用奇异位形延拓和自动尺寸最优设计不属于当前版本。
