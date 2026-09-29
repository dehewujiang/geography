# 抽屉3：呈现生成（第3步细节）

> 目标：把分镜变成GES能播的素材。只改脚本 `CLIPS` 表，永远不手改 `.esp`。

## 1. 参数唯一来源

- 镜头（路点/高度/俯角/时长）和 `.kml` 剪取规格只在 `make_video_assets.py` 的 `CLIPS` 表里改。
- `.kml` 重剪用 `python make_video_assets.py generate-kml`，与成品逐字节一致才算正常。

## 2. 命令三件套（根目录执行）

```powershell
python make_video_assets.py generate
python make_video_assets.py generate-kml
python make_video_assets.py verify
```

- 中文乱码时前缀：`$env:PYTHONIOENCODING='utf-8'`
- 只装标准库，别装 numpy 等依赖。

## 3. 编码禁区（血泪教训）

- `.esp` 数值是归一化值，区间固定（经度-180~180、纬度-89.9999~89.9999、高度-500~65117481、朝向0~360、俯仰0~180），每个块同时声明 min+max，不写负方位角。
- 骨架（modelVersion 17 属性树）不动，只动数值。依据见脚本头部 [PROTOCOL]，不要重新调研。

## 产出验收

- `视频制作/XX_*.esp` + `XX_*.kml` 成对生成，`verify` 退出码0，才许进第4步。
