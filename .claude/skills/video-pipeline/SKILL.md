---
name: video-pipeline
description: 短视频流水线入口卡（主题驱动：说一个主题→自动产出成品素材+后期包）。做任何一集（01~11）或任何新主题时先读我，我再指到对应抽屉。触发词：做视频、走流程、做新主题、新的一集、事实/叙事/呈现/验收/发布。
---

# 短视频流水线（入口卡，只管顺序和交接）

> 大白话：我是菜单，不做菜。细节全在 `references/` 抽屉里，用哪步拿哪屉。
> 项目地图见根目录 `CLAUDE.md`，素材清单见 `视频制作/CLAUDE.md`。
> 本项目已升级为**主题驱动流水线**（2026-10-12）：目标 = 用户说一个主题 → AI 自动产出成品素材包+后期包，用户只做 GES 导入验收和发布。

## 五步单向走，不许跳步回改

| 步 | 读哪个抽屉 | 产出交接物 | 没这个不许进下一步 |
|---|---|---|---|
| 1.事实锁死 | `references/step1-fact.md` + **审校**`references/fact-auditor.md` | 事实卡一页+母版kml | 没事实卡不开文案 |
| 2.叙事定稿 | `references/step2-narrative.md` | 文案+分镜 | 文案没定稿不动脚本 |
| 2.5 分镜预演 | `references/design-loop.md` + **模板**`references/shot-templates.md` + **词汇**`references/lexicon.md` + **粮库**`references/data-sources.md` | 配方草案(机器卡口过)+预演板+锁版签名 | 没锁版不渲染 |
| 3.呈现生成 | `references/step3-present.md` + **编码**`references/ges-expert.md` + **镜头**`references/cinematography.md` | esp+kml成对 | `verify`没过不进GES |
| 4.亲眼验收 | `references/step4-review.md` | 问题单 | 用户没播一遍不发布 |
| 5.发布复盘 | `references/step5-publish.md` + **后期**`references/post-production.md` | 标题封面+渲染操作清单+剪辑节奏表+复盘一行 | 没复盘不开下一主题 |

## 三条铁律（哪步都一样）

1. **单向不回流**：呈现里发现路线错，回到第1步改母版重走，不在呈现里凑合。
2. **只认交接物**：上步没产出，下步不开工，口头说的不算。
3. **动手前存档**：改脚本或母版KML前先 `git add -A; git commit -m "checkpoint:..."`。

## 新主题流程（≠做既有某集）

```
说一个主题
→ 步1：建该主题"母版KML"（含精度声明）+ 事实卡（走 fact-auditor 三查）
→ 定稿：分集划分 → 每集 cam 逐点坐标 + alts/tilts 节奏数组（走 cinematography 规范）
       地形地板线：open-meteo elevation API 采样一次写死进表（免费无密钥；注明来源日期）
→ 步3：generate → verify（退出码0）
→ 步4：用户 GES 重测（拖入顺序：先esp后kml）
→ 步5：后期包（post-production 交付物定义）
```

**下一步工程任务（写在此防遗忘）**：`make_video_assets.py` 目前硬编码"蒙古大迂回"专用（母版文件名、17 断言、OPENING_LINE、kml 剪取规则）——要泛化为"主题无关引擎"：母版路径/断言数/剪取规格全部参数化，CLIPS 表成为纯主题层。

## 现有文件对应（别另起炉灶）

- 事实唯一底稿：`蒙古大迂回_三路路线.kml`（17地标，脚本硬断言，勿手改结构）。
- 叙事和呈现交界：`make_video_assets.py` 的 `CLIPS` 表（cam 逐点坐标 + alts/tilts 逐点数组 + hold 定场静止秒）。
- 生成校验：`python make_video_assets.py generate` → `verify`（退出码0才算过）。
- 成品：`视频制作/XX_*.esp` + `XX_*.kml`，先拖esp后拖kml进GES。

## 2026-10-13 定调（重大转折，详见根目录 `memory/decisions.md` ADR-005~008）

- 本项目重定义：**真产品=这套 AI 视频系统（skill/hooks/workflow harness）**，蒙古包抄南宋只是测试用例
- 成片规格：**竖屏 1080×1920**；时长不锁死，由事实密度定（分镜层拿定义权）
- 分工口诀：**几何正确归机器，观感受众归后期**（后期=baocut 为主选、剪映为备份——ADR-006）
- 渲染器：**自建引擎为主**（竖屏原生+翻山剖面+高程夸张，GES 三死穴）；GES 转"横屏震撼航拍配菜"（竖屏上部画面+下部字幕带版式）；裁决=三张牌擂台赛（ADR-008）
- 风格裁判：参照"三维地图看世界"拆解（二抄一反，ADR-007）；**来源标注义务一票否决**
