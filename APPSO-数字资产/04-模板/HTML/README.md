# 图像与视频 HTML 审阅模板

图像模板用于比较候选图、查看原图和下载素材。视频模板用于播放成片、查看规格和浏览全局制作截图。输出为独立 HTML 与相对路径素材，可打包后离线审阅。

正文 Markdown 的图文预览继续使用现有 Wenyan／公众号工具；这两份模板只整理作品与过程素材。

## 直接生成示例

在仓库根目录运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 media-review docs/appso-workflow/examples/image-review.json --output output/image-review --zip
```

输出 `output/image-review/index.html`、`assets/` 和 `output/image-review.zip`。完整解压 ZIP 后打开 `index.html`。

## 视频清单

复制 [视频审阅清单](../../../docs/appso-workflow/examples/video-review.json)，相对路径以清单文件所在目录为基准：

```json
{
  "kind": "video",
  "title": "产品体验｜视频审阅",
  "items": [
    {
      "file": "assets/scene-01.mp4",
      "poster": "assets/scene-01.jpg",
      "title": "案例名称",
      "caption": "具体展示的动作、运镜或反转",
      "model": "实际模型",
      "spec": "18 秒 · 1080P · 16:9",
      "credits": 100
    }
  ],
  "process_images": [
    {"file": "assets/workspace.png", "title": "制作过程", "caption": "完整工作台截图"}
  ]
}
```

示例积分仅用于说明字段，替换为实际任务记录；`poster`、`model`、`spec`、`credits` 均可省略。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/workflow.ps1 media-review <本次审阅清单.json> --output <本次输出目录> --zip
```

模板保留视频原文件，不转码、不补帧、不修改原音轨；规格由审阅清单提供，生成页不代替媒体质检与素材权利确认。对外阅读版只填写读者需要的作品说明，内部审稿意见另列。
