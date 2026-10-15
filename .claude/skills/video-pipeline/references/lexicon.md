# 抽屉：术语词典（项目内叫法 ↔ 行业标准名）

> 一句话：我是词汇基建——设计、沟通、复盘、外部检索一律优先用行业标准名；没有标准名的自造词，先用加注，进化出专名后替换。
> 来源：2026-10-13 与用户对齐辩论后整理；标记 ①=行业标准 / ②=行内惯称 / ③=项目自造。

## 镜头调度

| 项目内说法 | 行业标准名 | 档 | 一句话 |
|---|---|---|---|
| 3D仰视（翻山镜头A） | low-angle shot（低角度仰拍）+ terrain flythrough（地形飞越） | ① | 贴地+仰角，山墙压脸 |
| 镜头跟路线走 | follow shot；游戏圈 chase camera | ① | |
| 空中压下来 | push in（推近）；摇臂镜头 crane shot | ① | |
| 绕目标转 | orbit shot（轨道环绕） | ① | |
| 转弯斜身像飞机 | aim-ahead 远点追踪（赛车/飞行圈惯称） | ② | 看前方2~4秒路点，转弯自然成坡 |
| 越拉越近+世界变压抑 | dolly zoom（希区柯克变焦/vertigo effect） | ① | 讲"山多压迫人多绝望"的神器 |
| 上帝视角 | bird's-eye view / top-down | ① | |
| 正北朝向 | north-up；朝向=bearing/heading（方位角） | ① | |

## 地图与地形

| 项目内说法 | 行业标准名 | 档 | 一句话 |
|---|---|---|---|
| 路线生长动画 | route reveal + draw-on / write-on effect（AE圈） | ① | |
| 里程碑弹出 | pin drop（地图图钉） | ② | |
| 剖面侧视动画（B镜头） | elevation profile（测绘标准词 cross-section）；实现=正交相机 orthographic side view | ①+③ | 同引擎直拍（ADR-013），非SVG贴图 |
| 大山拔高2~3倍 | vertical exaggeration（高程夸张） | ① | GIS正式术语 |
| 底图 | basemap | ① | Esri等 |
| 山体加明暗影 | hillshade（山体阴影） | ① | GIS正式术语 |
| 高程数据 | DEM（digital elevation model） | ① | |
| 路线地图卡片化 | 无专名 | ③ | 竖屏转场出现，占屏1/3 |

## 字幕与信息设计

| 项目内说法 | 行业标准名 | 档 | 一句话 |
|---|---|---|---|
| 底部白字幕条 | lower third（下三分之一字幕条） | ① | 剪辑/baocut层 |
| 毛笔章节大字卡 | title card；片头卡=bumper / title sequence | ① | |
| 86000→30000 对比 | counter animation / odometer effect（里程表效果） | ② | |
| 会动的强调文字 | kinetic typography；门类=motion graphics（MG动画） | ① | |
| 转弯不顿挫 | easing（缓动曲线：ease-in-out、cubic…） | ① | |
| 看了想吐 | motion sickness / simulation sickness（晕动症） | ① | |
| 上镜结尾接下镜开头 | match cut（匹配剪辑） | ① | |
| 天气维度剧情呼应 | （无专名，进事实卡分层：天时=季节/天气档） | ③ | 参考上片槽点 |

## 镜头原子补全清单（2026-10-13 新增六件，业内标准件，防模板封闭）

| 原子 | 档 | 干什么用 |
|---|---|---|
| 分态同屏 split-screen（地图+剖面上下同屏） | ① | 骑行赛事转播标准打法：上飞下爬同步；T-01⑤A/B 的进阶形态 |
| 等高线进出 contour morph | ① | "等高线多密=山多险"，最直观的险表达 |
| 时序光照（太阳压山/晨昏） | ① | 防"缺天时"槽点（参上片观众意见）；GES 光照可真做，引擎仿七成 |
| 地图放大镜 lens follow | ② | 路线过密时局部放大跟随；竖屏转场神器 |
| 双指推近手势拟真 | ② | 竖屏观众原生交互语感（纯项目内提出，待验证） |
| 底部进度烧尺 scrubber | ② | 里程传达长期手段（"两万五千里"从不缺席） |

增益回路：①设计环允许 LLM 标"需开发"收集新品种；②复盘把观众反馈转成模板修改。模板库=开放集，永不定稿。

## 流程与工序

| 项目内说法 | 行业标准名 | 档 | 一句话 |
|---|---|---|---|
| 机器先出静帧设计稿给用户点题 | previz（previsualization，分镜预演） | ① | 影视开机前标准工序 |
| 分镜表 | storyboard（分镜板） | ① | |
| 由动画引擎算出每个镜头的参数表 | camera path animation / keyframe interpolation | ① | |
| 分镜也走先红后绿 | 设计环（进 `design-loop.md`） | ③ | 与 TDD 同构 |
| 后期包清单交给AI剪辑软件 | edl 思想（edit decision list，剪辑决策单） | ① | ES暗线：EDL是行业老词 |
| 镜头最低离地 | minimum ground clearance（离地底线） | ② | 晕动纪律数字卡 |
