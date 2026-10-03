# 机构类型索引与扩展资料

## 使用规则

按实际拓扑与几何构造识别机构，不按名称自动选求解器。先确认新图刚体与运动副；资料案例的字母归属只在该案例内有效。下面“已验证”仅指指定示例的运动学与装配分支，不代表该机构所有尺寸、所有变体都支持。

## 可运行的声明式案例

| 家族/用途 | 模型 | 构造计划 | 状态与边界 |
|---|---|---|---|
| 铰链四杆 | examples/fourbar.json | rotate → circles | 示例整周可达；其他尺寸需重验 |
| 对心/偏心曲柄滑块 | examples/slider_0.json、slider_30.json | rotate → circle_line | 固定直导轨与有限套筒 |
| 摆动导杆/槽杆 | examples/slotted_lever.json | rotate → rigid | 已知销决定杆方向 |
| 插床 | examples/slotter.json | rotate → rigid → circle_line | 导杆方向与输出滑块 |
| 连杆压床 | examples/press.json | rotate → circles → rigid → circle_line | 死点不能无分析穿越 |
| 四个已确认复合机构 | examples/case_6214.json～case_6217.json | 两圆、导轨、刚体变换组合 | 各案例拓扑独立 |
| 胶片进给爪四杆 | examples/film_advance.json | rotate → circles → rigid | E为连杆材料点；未模拟胶片接触/进给 |
| Hoeken比例近似直线四杆 | examples/hoeken.json | rotate → circles → rigid | 下述比例案例；近似直线必须报告指定区间与偏差（本例输入90°～270°、1°采样，拟合水平线的最大偏差约0.200mm，投影行程160mm） |
| Scott-Russell直角转换复合机构 | examples/scott_russell_driven.json | rotate → circle_line → circles → rigid | 曲柄滑块驱动有限范围Scott-Russell单元，理想输出x=0 |
| Klann六杆步行 | examples/klann.json | rotate → circles → rigid → circles → rigid | 专利初始坐标推杆长，整周采样；未模拟足地接触与负载 |

固定R/P求解器有14个JSON参考模型。槽轮接触切换见contact-switching.md，属于独立正向分析方法，不计入上述固定拓扑模型。

## 新案例的独立几何依据

### Hoeken比例四杆

取AB=40、AD=80、BC=CD=CE=100 mm，B、C、E共线且C位于BE中间。由BC方向构造E，禁止将E投影到直线上。AD:AB:BC:CD:CE=2:1:2.5:2.5:2.5来自图谱四杆子链的比例，本文件只建模该子链，不包含图谱中附加的平行四边形机构。

### Scott-Russell

固定O=(0,0)，S=(s,0)，OM=SM=MT=50，M是ST中点。两圆求M，刚体变换T=2M−S；由等圆得到M.x=s/2，因此T.x=0。用附加曲柄滑块产生S.x∈[40,80]，避免s=0或100的退化。S的水平导轨是实际P副；T的竖直线是机构计算结果，不额外添加输出导轨。

### Klann

坐标取US6260862B1表1的伸展姿态，缩放100倍并标明原表小数舍入。A对应轴15，F对应轴11，G对应轴9；B、C、K分别对应29x、27x、35x，属于连接臂；H、E对应37x、33x，与K属于腿刚体。先解C，再变换K，解H，最后变换E。刚体三角形必须检查三条边，不能用相同颜色代替刚体约束。原始姿态E=(0,0)作为独立手算验收；不同姿态的表中舍入坐标不直接当作精确杆长不变的证明。

## 已收集、尚无验证模型的方向

| 机构 | 可扩展价值 | 进入支持范围前的必要工作 |
|---|---|---|
| Watt六杆 | 多级闭环、连杆中点近似直线 | 确定具体倒置与固定点；给尺寸并验证两级闭环 |
| Stephenson I/II/III | 六杆拓扑与高阶闭环 | 逐型检查能否拆成已有原语；不能从Klann泛化到全部Stephenson |
| Chebyshev、Roberts | 近似直线的不同连杆曲线 | 确认输入往复区间、局部输出点与误差；避免声称整周精确直线 |
| Jansen步行 | 多个两圆构造的足端轨迹 | 取原作者/研究资料的准确拓扑和尺寸，逐级验证；杆线数不等于刚体数 |
| 平行四边形搬运 | 输出姿态保持、平行移动 | 分析共线死点及分支延拓，再选择正向构造 |
| Pantograph放大缩小 | 相似变换、轨迹缩放 | 明确自由度、输入点路径及所有独立输入；不能凭单个曲柄补齐多自由度 |
| 剪叉升降 | 对称几何与有限滑轨 | 明确驱动行程、滑块归属与折叠奇异 |
| 双滑块椭圆规 | 两个正交P副 | 增加合适输入路径或已有原语构造，分析端点奇异 |
| 苏格兰轭/Whitworth快回 | 销槽、偏心与工作段时间比 | 区分真实P副方向、槽内材料点与接触释放 |
| 棘轮、齿轮及其他凸轮 | 单向约束、连续接触、啮合 | 当前无通用接触/轮廓求解器，不能从尖顶适配器泛化支持 |
| 尖顶直动盘形凸轮（对心/偏置） | `cam.py` / `run_cam.py`，行程函数与反转法离散构造；见 [cam.md](cam.md) | 仅理想规定接触运动，滚子/平底/摆动凸轮另行推导 |

## 原始资料入口

- Hoeken教学模型：Koç University，https://mysite.ku.edu.tr/ilazoglu/hoekens-linkage/ 。比例与四杆子链参考DMG-Lib，https://www.dmg-lib.org/dmglib/handler?image=16515023 。
- Scott-Russell原作者CAD教学展示：Dassault 3DEXPERIENCE Edu，https://3dswym.3dexperience.3ds.com/post/3dexperience-edu-students/scott-russell-mechanism_iIaXVI3WRLu8YOTsYQ4MYA 。精确直线依据上面的独立等圆推导。
- Klann初始坐标与连接关系：US6260862B1，https://patents.google.com/patent/US6260862B1/en ，表1与权利要求1。
- Watt/Stephenson分类：University of Almería，https://ingmec.ual.es/tmm/L01_03b_six_bars.html ；Watt六杆图谱 https://www.dmg-lib.org/dmglib/handler?image=16431023 。
- Jansen原作者入口：https://www.strandbeest.com/ 。该入口未提供本次可直接读取的完整尺寸，因此列为待验证方向。
