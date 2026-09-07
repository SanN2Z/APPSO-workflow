# APPSO Logo 乐园

把用户提供的 APPSO Logo 变成一座可以玩的 3D 滚球关卡。原图轮廓、字母顺序、A 与独立圆点的关系均保留；开场和游戏共用同一 Three.js 场景。

## 启动

当前目录已安装依赖，直接运行：

```powershell
npm run dev
```

浏览器打开 **http://127.0.0.1:5174/**。初次复制项目到其他电脑时，先执行 `npm ci`。需要 Node.js 22.12+ 或 24+，以及支持 WebGL 2 的现代浏览器。

生产构建与本地预览：

```powershell
npm run build
npm run preview
```

预览地址为 http://127.0.0.1:4174/。项目使用本地依赖，游戏运行时不请求外部字体、CDN、账户或服务。

## 怎么玩

- `WASD` / 方向键：沿屏幕方向推动小球，松手后会继续滑行。
- `Space`：刹车。窄桥和转弯处适合轻推、减速。
- `Esc` / `P`：暂停或继续；切到其他窗口会自动暂停。
- `R`：重新开始本局；`M`：静音；`V`：切换俯视全景与立体视角。
- 开场可直接点击「跳过开场，开始玩」。手机提供方向按钮，游戏中镜头跟随，俯视按钮可查看整关。

从 A 左下角的圆点出发，沿红色小圆点走过白色字面与透明桥。依次经过 A、两个 P 和 S 的圆环，再绕到 O 左侧，从斜坡滚入圆心。两个 P 弧线尽头会保存检查点；掉到红色底板上会自动重生。红色撞柱会反弹小球，第二个 P 的横杆会旋转。

## 实现

- `src/logo-contours.json`：从原始 PNG 提取的 6 个轮廓，包含两个 P 和 O 的洞，不依赖字体重绘。
- `src/main.js`：倒角挤出、材质、灯光、同场景开场、镜头、音效、触屏与界面。
- `src/level.js`：共享的关卡几何与固定 120 Hz 物理；惯性、坡面重力、圆柱 / 胶囊碰撞、落地、重生、按顺序通关。
- `scripts/trace_logo.py`：可选的原图轮廓重建脚本，需要 Python、OpenCV 和 NumPy。正常运行无需 Python。

这是定制的滚球物理，支持本关卡所需的静态台面、坡道和活动障碍，不是通用刚体模拟器。透明桥两侧的细线是边缘提示，并非阻止掉落的护栏。

## 验证与截图

```powershell
npm test
node scripts/keyboard-run.mjs
```

自动测试使用本机 Microsoft Edge；没有 Edge 的环境可安装 Playwright Chromium 并把配置中的 `channel: 'msedge'` 去掉。`npm test` 会自动启动或复用本地开发服务器。键盘通关脚本需先运行 `npm run dev`。

截图与测试结果位于 `artifacts/`：

- `01-flat-logo.png`：平面开场。
- `02-opening.png`：升起后的关卡全景。
- `03-gameplay.png`：到达第一个检查点。
- `04-completion.png`：通关与拉远镜头。
- `05-mobile.png`：手机尺寸布局。
- `06-keyboard-completion.png`：实时键盘事件通关。
- `course-result.json`、`keyboard-result.json`：实际测试数据。

`npm test` 对完整路线采用相同物理引擎的加速反馈驾驶，不修改位置或进度；独立的键盘通关脚本通过真实帧循环和浏览器键盘事件驾驶，不开放物理修改入口。碰撞与高处落地的定向测试会使用仅 `?test=1` 开启的测试入口布置初始条件。

本轮浏览器验证环境为 Windows 上的无头 Microsoft Edge。手机为浏览器视口与触屏事件验证，尚未在实体手机或 Safari 上实测。音效节点与静音状态已检查，未进行扬声器听感验收。

## 资产与边界

这是当前任务授权的 APPSO 品牌创意测试，不是官方 Logo 改版或公开发布。原始 `appso-logo.png` 保持不变；衍生轮廓、场景和截图分别保存。来源、权利与使用范围见 `asset-manifest.yml`。2026 年 9 月 7 日，用户授权将源码、任务输入和资产登记同步到本项目私有仓库；构建产物、依赖和测试截图继续只在本地保存。该备份授权不改变公开发布与品牌使用范围。

建模参考：[Three.js ExtrudeGeometry 官方文档](https://threejs.org/docs/pages/ExtrudeGeometry.html)、[Shape 洞轮廓文档](https://threejs.org/docs/pages/Shape.html)。浏览器验证参考：[Playwright 浏览器支持文档](https://playwright.dev/docs/browsers)。
