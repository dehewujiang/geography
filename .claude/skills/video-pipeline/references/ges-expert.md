# GES 专家模块（编码协议 + 参数清单 + 故障速查）

> 抽取自 2026-09-28 v1 踩坑 + 2026-10-12 真实导出样本逆向。**禁止重新调研**——这里每条都有证据来源。
> 证据等级：[文档确认]=真实导出 GES 工程样本（modelVersion 17，Stanford-NavLab/nerfstudio Transamerica 模板 + gist 8665504665ca8f622bd7753c3b50f910 + mkatzef esp 模板）。

## 1. 数值编码铁律（ vital — v1 全踩过的坑）

GES modelVersion 17 关键帧值 = (实际值 − 下限) / (上限 − 下限)，区间一律标准区间：

| 属性 | 标准区间 | 说明 |
|---|---|---|
| 经度 longitude | −180 ~ 180 | |
| 纬度 latitude | −89.9999 ~ 89.9999 | |
| 高度 altitude | −500 ~ 65117481（米） | 块内声明 `"logarithmic": false` |
| 水平转向 rotationX | 0 ~ 360 | **罗盘方位角**：正北=0°，顺时针，90°=正东；禁负值（用 unfold 收敛到最短弧±180°，允许略越界） |
| 俯仰 rotationY | 0 ~ 180 | **0=垂直俯瞰（顶视），90=平视地平线**；⚠️ 数值越大越抬、雾越重。贴地跟拍用 25~35°（v2.1 曾错设 60~70 已纠正） |

- 每块必须同时声明 `minValueRange` + `maxValueRange`。
- 文件骨架（modelVersion 17 属性树）不可动，只动数值。
- 时间轴：关键帧 `time` ∈ [0,1]，**严格递增**（同刻重复帧 GES 不接受）；首 0 尾 1。
- 插值速度分配：时间按"已飞里程/总里程"分配（长路段占时多），消除忽快忽慢——见 `cinematography.md`。

## 2. 缓动（真实验证）

真实导出无 `easing` 字段；缓动 = 关键帧上的 transitionIn/transitionOut 对象 [文档确认]:

```json
"transitionOut": {"x": 0.066,  "y": 0.0, "influence": 0.5, "type": "auto"}  // 离开该帧
"transitionIn":  {"x": -0.066, "y": 0.0, "influence": 0.5, "type": "auto"}  // 进入该帧
type ∈ "auto"（自动平滑）| "linear"（x:0,y:0）| "custom"
```

**组态纪律**：只在整段**首尾**关键帧叠加（首帧 transitionOut、末帧 transitionIn）；中间帧保持线性。
挨个加 = 每过路点减速一次 = 停顿感（与抽动感同病）。配合 `animationModel.roving: true`（平滑过弯）。

## 3. 环境参数清单（真实样例存在哪些就写哪些，空 `{}` = 用 GES 默认）

| 属性 | 状态 | 用法 |
|---|---|---|
| sunGroup.worldTime | 单值 `relative` 0..1 | 0.5≈正午顶光（平）→ **本项目统一 0.8（傍晚斜射，立体感）**；24h 昼夜映射为[推测]。可打关键帧做"黄昏飞到夜" |
| sunGroup.sunVisibility | value {} | 阴影无独立字段——阴影随 Time-of-Day 光照自动生效 [文档确认，真实样例无 shadows 节点] |
| cloudGroup (visibility/opacity/height/date) | date 必须 epoch ms 区间 | 云影加天气感 |
| starsPlanetsGroup.starsEnabled | value {} | 夜戏用 |
| seawaterGroup | value {} | 海面动画 |
| buildingsEnabled | value {} | **改史题材必须确认关闭**（现代 3D 城市穿帮）——用户 GES 里人工确认 |
| cameraLensGroup.fov | value {}（真实样例有 relative 值如 0.219…，绝对角度映射未标定 [推测]） | 可打关键帧做推拉变焦；先实测标定一次再用 |
| cameraLensGroup.exposure / aperture / minFocusLength | 空值 | DOF 浅景深；**默认不开**（虚化过头像对焦失败） |
| cameraTargetEffect（enabled 开关 + POI 三个坐标块） | 空值 | **注视点锁定**：镜头飞行始终盯一点 → 环绕镜头/回头看；`enabled.value.relative=1` 开启 |

## 4. 故障速查（症状 → 修法）

| 症状 | 修法 |
|---|---|
| 导入 GES 后镜头方向反/背对 | 全部方位角 +180° |
| 歪向一侧/镜像 | 方位角取值约定翻转 |
| 位置/高度乱飞 | 先 `verify` 看解码值，再查区间声明 |
| 导入失败/结构报错 | 时间轴重复点？区间声明缺失？——查 `verify` 的 strict 递增检查 |
| 画面灰白雾蒙蒙 | 高度过高+俯角过大（平视方向）→ 降高度、俯仰压到 25~35° |
| 忽快忽慢抽动 | 时间未按里程分配 / 中间关键帧加了缓动 —— 均查 |

## 5. GES 侧人工操作（AI 不能代做）

- 导入：空白项目 → 拖入 `XX.esp`（先）→ `XX.kml`（后）→ 播放。
- 渲染：Render 面板 → 分辨率 3840×2160、30fps、运动模糊=开、导出 PNG 图片序列（不是录预览；预览=浏览器低清放大）。
- 验收判定只能由用户做（Google 账号/人眼）。
