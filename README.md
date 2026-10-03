# 杆件机构 Skill · solve-planar-linkages

从机构图出发，先确认刚体与运动副，再用向量、旋转矩阵和几何构造正向求解平面机构。
支持运动验证、尺寸可行性调整、流畅 GIF 与每 10° 坐标导出。

## 能做什么

- 标注机架、构件、铰点、滑块、转动副 R、移动副 P 和待确认关系。
- 使用驱动旋转、两圆交点、圆与直线导轨交点及刚体点变换组织正向计算。
- 检查杆长、运动副、装配分支、周期闭合、有限导轨接合与间隙。
- 默认以 0.1° 间隔采样检查；连续可达性证明另行推导。
- 默认动画每圈 300 帧、每帧 20 ms，实读验收 GIF 小于 5,000,000 字节。
- 包含 14 个固定拓扑 JSON 案例，以及接触切换分析说明。

不能从任意图片自动识别并求解所有机构。
固定 R/P 求解器只支持模型格式中列出的构造原语；一般闭环和接触切换不能冒充已支持模型。

## 安装到 Codex

将本仓库完整克隆到 Codex 的技能发现目录，目录名保持 `solve-planar-linkages`。
例如在项目中使用：

```bash
mkdir -p .agents/skills
git clone https://github.com/terrellAI/solve-planar-linkages.git .agents/skills/solve-planar-linkages
python -m pip install -r .agents/skills/solve-planar-linkages/requirements.txt
```

本仓库为公开仓库，可直接克隆。不要把账号密码写进命令、配置或仓库。
若运行环境使用其他技能目录，将整个仓库放入该环境实际扫描的目录。
在 Codex 中用 `$solve-planar-linkages` 指定技能，并提供机构图、连接关系和尺寸约束。

## 用本次机构图入门

![用户提供的机构图](docs/mechanism-input.png)

### 本次实际调用输出：拓扑确认图

![本图的带引线拓扑确认图](docs/topology-confirmation.png)

上图为确认前的真实首轮输出。用户随后回复“正确”，确认 ABD 刚体等关系，再继续完成验证；新图仍需独立确认。

本次实际执行记录见 [机构图使用指南](docs/usage-example.md)：拓扑已确认，示例模型已完成连续可达性、导轨接合、0.1°采样和300帧动画验证。

![已验证的真实机构动画](docs/verified-example/animation.gif)
第一条消息可直接复制：

```text
使用 $solve-planar-linkages 分析我附上的机构图。
先输出带引线的拓扑标注图，区分机架、刚体、R副、P副、滑块与纯辅助点。
请区分 O、A、B、C、D、E 与带下标的姿态标记；不要把不同姿态画成新增构件。
不要预设 OAB、CBD 或其他字母组合属于同一刚体。
对刚体归属、滑块方向、导轨归属、输入输出有歧义的地方，逐项提问并等待确认。
本图没有提供尺寸；拓扑确认后，采用明确标注的示例尺寸。
确认后用向量与旋转矩阵正向求解，给出示意图、手算案例、流畅动画、每10度坐标和验证报告。
```

## 直接运行内置案例

在仓库根目录执行：

```bash
python scripts/run_model.py references/examples/fourbar.json --out output/fourbar --gif
python scripts/run_model.py references/examples/case_6216.json --out output/case_6216 --gif
```

输出：`animation.gif`、`preview.png`、`coordinates_10deg.csv`、`verification.json`。
内置案例的字母和刚体归属仅适用于各自模型，不能移植到本次机构图。

## 验证

```bash
python scripts/test_linkage.py
python scripts/test_animation.py
python scripts/test_expanded_examples.py
```

本仓库发布时已运行以上回归检查。检查通过只覆盖现有实现和案例，不意味着本次未确认机构已求解。

## 文件索引

| 路径 | 用途 |
|---|---|
| `SKILL.md` | 技能触发条件与完整工作流程 |
| `agents/openai.yaml` | 技能显示信息 |
| `scripts/` | 正向求解、渲染及回归检查 |
| `references/model.md` | JSON 模型格式 |
| `references/geometry.md` | 几何推导与边界条件 |
| `references/mechanism-catalog.md` | 案例目录与支持范围 |
| `references/contact-switching.md` | 接触切换机构分析 |
| `references/examples/` | 14 个声明式模型 |
| `docs/usage-example.md` | 本次机构图使用说明 |

未经确认的刚体关系必须保留为待确认项。
几何运动验证不等同于三维碰撞、强度或实际加工验证。
