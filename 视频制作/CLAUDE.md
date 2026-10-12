# 视频制作 — GES 素材成员清单（L2）

> 一旦我所属的文件夹有所变化，请务必更新我。
> 上级文档：[../CLAUDE.md](../CLAUDE.md)（同内容副本：`../AGENTS.md`）
> 本文档与同目录 `AGENTS.md` 为**同内容复制对**（本机无符号链接权限）；改哪份就以哪份为准、立即覆盖另一份：改 CLAUDE.md → `Copy-Item CLAUDE.md AGENTS.md -Force`；改 AGENTS.md → `Copy-Item AGENTS.md CLAUDE.md -Force`（在本目录内执行）。

## 成员清单（11 组 × 2 文件 = 22 个 ＋ 临时对照 2 个）

每个编号 = 一对文件，按成片顺序使用：`XX_*.esp`（相机动画，**先**拖入 GES）+ `XX_*.kml`（路线图层，**后**拖入）：

01_开场 ｜ 02_三路全景 ｜ 03_东路 ｜ 04_中路 ｜ 05_西路 ｜ 06_大理会师 ｜ 07_四川战场 ｜ 08_两湖北线 ｜ 09_两湖南线 ｜ 10_安南 ｜ 11_终章

- `03_东路_高版`（临时对照，2026-10-12晕动试点：唯一变量=高度翻倍，其余与03一致；用户对比后删败者，不占编号）

| 类型 | 数量 | 属性 |
|---|---|---|
| `XX_*.esp` | 11 | **生成物**：由根目录 `make_video_assets.py generate` 重写；严禁手改数值 |
| `XX_*.kml` | 11 | 路线图层（成品）：`generate-kml` 可从母版重剪（逐字节复刻现状），正常无需动 |

- 镜头参数（路点/高度/俯角/时长）唯一来源：`../make_video_assets.py` 的 `CLIPS` 表（含 .kml 剪取规格）；重剪 .kml 用 `python make_video_assets.py generate-kml`。
- 改完自检：根目录执行 `python make_video_assets.py verify`，须通过（退出码 0）。
- 对每个片段的解说、验收方式、GES 编码规范、故障症状→修法：见上级文档 `../CLAUDE.md`。
