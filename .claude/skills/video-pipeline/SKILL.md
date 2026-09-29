---
name: video-pipeline
description: 《中央帝国的军事密码》短视频五步流水线入口卡。做任何一集（01~11）时先读我，我再指到对应抽屉。触发词：做视频、走流程、新的一集、事实/叙事/呈现/验收/发布。
---

# 短视频五步流水线（入口卡，只管顺序和交接）

> 大白话：我是菜单，不做菜。细节全在 `references/` 抽屉里，用哪步拿哪屉。
> 项目地图见根目录 `CLAUDE.md`，素材清单见 `视频制作/CLAUDE.md`。

## 五步单向走，不许跳步回改

| 步 | 读哪个抽屉 | 产出交接物 | 没这个不许进下一步 |
|---|---|---|---|
| 1.事实锁死 | `references/step1-fact.md`（母版四选一另见`kml-extract/hand/code/convert.md`） | 事实卡一页+母版kml | 没事实卡不开文案 |
| 2.叙事定稿 | `references/step2-narrative.md` | 文案+分镜 | 文案没定稿不动脚本 |
| 3.呈现生成 | `references/step3-present.md` | esp+kml成对 | `verify`没过不进GES |
| 4.亲眼验收 | `references/step4-review.md` | 问题单 | 用户没播一遍不发布 |
| 5.发布复盘 | `references/step5-publish.md` | 标题封面+复盘一行 | 没复盘不开下一集 |

## 三条铁律（哪步都一样）

1. **单向不回流**：呈现里发现路线错，回到第1步改母版重走，不在呈现里凑合。
2. **只认交接物**：上步没产出，下步不开工，口头说的不算。
3. **动手前存档**：改脚本或母版KML前先 `git add -A; git commit -m "checkpoint:..."`。

## 现有文件对应（别另起炉灶）

- 事实唯一底稿：`蒙古大迂回_三路路线.kml`（17地标，脚本硬断言，勿手改结构）。
- 叙事和呈现交界：`make_video_assets.py` 的 `CLIPS` 表。
- 生成校验：`python make_video_assets.py generate` → `verify`（退出码0才算过）。
- 成品：`视频制作/XX_*.esp` + `XX_*.kml`，先拖esp后拖kml进GES。
