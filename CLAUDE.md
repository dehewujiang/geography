# 《中央帝国的军事密码》视频素材工程 — AI 接手文档

> **文档体系（GEB）**：播种 2026-09-28 ｜ 维护者：dehewujiang + AI 会话。
> 本文档在 `CLAUDE.md` 与 `AGENTS.md` 两个文件名下同时存在，**内容必须逐字一致**（本机无符号链接权限，坚果云同步也只认物理文件，故采用复制对）。
> **修改任意一份后，必须立即同步另一份**：改 CLAUDE.md → `Copy-Item CLAUDE.md AGENTS.md -Force`；改 AGENTS.md → `Copy-Item AGENTS.md CLAUDE.md -Force`（在项目根目录执行）。

书稿文件夹 + 地图动画素材。**不是软件项目**：没有测试框架、没有构建链。核心是一条单向流水线：
**母版 KML → `make_video_assets.py` → `视频制作/` 下的 GES 素材**（.esp 相机动画 + .kml 路线图层，成对编号 01~11，按成片顺序使用）。

## 文件角色

| 路径 | 角色 |
|---|---|
| `蒙古大迂回_三路路线.kml` | **母版**：17 个地标（7 条路线 + 10 个地点），全项目唯一坐标来源；改路线只改这里。脚本硬断言地标数=17，增删地标须同步改断言 |
| `视频制作/XX_*.esp` | GES 相机动画工程（生成物，勿手改） |
| `视频制作/XX_*.kml` | 路线图层（成品；`generate-kml` 可从母版重剪、与现状逐字节一致——正常流程无需动） |
| `make_video_assets.py` | 生成器 + 重剪器 + 校验器（纯标准库；**别装 numpy 等依赖**） |
| `kml.json` | 早期会话导出记录（研究物，与流程无关，勿删勿用） |
| `蒙古大迂回_三路路线_备份20260928.kml.bak` | 用户保留的母版备份，勿删 |

## 命令（Windows PowerShell）

```powershell
python make_video_assets.py generate      # 重写全部 11 个 .esp
python make_video_assets.py generate-kml  # 从母版重剪 11 个 .kml（与既有成品逐字节一致）
python make_video_assets.py verify        # 回归校验：解码值与路线/方位逐项比对；退出码 0=通过
```

- 中文输出乱码时前缀：`$env:PYTHONIOENCODING='utf-8'; [Console]::OutputEncoding=[System.Text.Encoding]::UTF8;`
- `verify` 就是本项目的测试：改完必跑，不跑不许说完成。

## GES .esp 数值编码（血泪教训，改代码前必读）

.esp 里所有数字是"归一化值" = (实际值 − 下限) / (上限 − 下限)，GES 按**固定标准区间**还原：

| 属性 | 标准区间 | 换算 |
|---|---|---|
| 经度 | −180 ~ 180 | 值 = (lon+180)/360 |
| 纬度 | −89.9999 ~ 89.9999 | 值 = (lat+89.9999)/179.9998 |
| 高度（米） | −500 ~ 65117481 | 值 = (alt+500)/65117981 |
| rotationX = 水平朝向 | 0 ~ 360 | 值 = **罗盘方位角**/360（正北=0°，顺时针，90°=东） |
| rotationY = 俯仰 | 0 ~ 180 | 值 = 俯仰/180（0=垂直俯瞰，90=平视） |

- 每个块必须**同时**声明 `minValueRange` + `maxValueRange`，值保持在区间内（不写负方位角）。
- **禁止**：自定义区间归一化 / 只写 min / 负值——2026-09-28 的 v1 全踩了，导致镜头方向反向、位置乱飞（旧版在 git 历史有档）。
- 文件骨架（modelVersion 17 属性树）**不可动**，只动数值；当前骨架已实测可导入 GES。
- 编码依据与完整调研结论见 `make_video_assets.py` 头部 [PROTOCOL]——**不要重新调研**；尤其弃用 mkatzef/google-studio-utils 旧编码（v1 的坑）。
- 调镜头（高度/俯角/时长/路点）→ 只改脚本 `CLIPS` 表 → `generate` → `verify`。参数唯一来源是脚本，永远不手改 .esp；.kml 剪取规格也在 `CLIPS` 表 `kml` 字段，重剪用 `generate-kml`。

## GES 验收只能由用户完成

- 打开 earth.google.com/studio 需要用户自己的 Google 账号，AI 无法代开代测。
- 用户验收：新建空白项目 → 拖入 `XX.esp` → 拖入 `XX.kml` → 播放，看"镜头沿路线、面朝飞行方向"。
- 若方向仍不对（症状 → 修法）：**背对/反向** → 全部方位角 +180°（`build_esp` 里 pans 生成处）重新生成；**歪向一侧/镜像** → 方位角取值约定翻转；**位置/高度错** → 先 `verify` 看解码值，再查区间声明。

## 操作纪律

- 动手前先提交 checkpoint（`git add -A; git commit -m "checkpoint: ..."`）；git 仅作本机回退锚点，用户不用 git。
- 母版 KML、`.bak`、`kml.json` 只读；`视频制作/*.kml` 不手改（改剪法 → 改脚本 → `generate-kml` 重剪）；删除等不可逆操作先问用户。
- 项目在坚果云同步：改完文件后，用户需等同步完成再在 GES 里测试。

## 文档体系（L1/L2/L3，任何 AI 的导航）

| 层 | 位置 | 内容 |
|---|---|---|
| L1 · 本目录 | `CLAUDE.md` / `AGENTS.md`（同内容复制对） | 全局地图：文件角色、命令、编码规范、纪律 |
| L2 · `视频制作/` | `视频制作/CLAUDE.md` / `视频制作/AGENTS.md`（同内容复制对） | 成员清单 + 父级链接 |
| L3 · 代码文件头 | `make_video_assets.py` 的 [INPUT]/[OUTPUT]/[POS]/[PROTOCOL] | 文件级契约 |

- 接手顺序：先读 L1 → 需要时读 L2 → 改代码前先看 L3 头部。
- 同步义务：目录成员有增减/改动 → 更新对应 L2；L2 变化 → 回查 L1；一次任务收尾跑 `/geb-workflow` 做 L3→L2→L1 同构检查。
