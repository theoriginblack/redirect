# 跳转动画页 · 旋转奶龙

Cloudflare Pages 静态跳转页：源域名进来自动播放动画，然后跳到目标站点。

**源域名**：`xn--psszg58c6d346v9y1a.work`（`西安奶龙大学.work`）
**目标**：`https://www.xidian.edu.cn/`
**仓库**：`https://github.com/theoriginblack/redirect`

---

## 目录结构

```
public/                    ← 只有这里面的东西会被发布
  index.html               动画页本体（要改的就是这个）
  _headers                 禁止缓存 + noindex
  spin.webp / spin.png     760×760 透明旋转素材
  spin-small.webp/.png     420px 小图，≤600px 视口用

README.md                  ← 以下都不发布
wrangler.toml
.assetsignore
preview.png               渲染预览图（本机）
source-photo.jpg          原始带水印照片（本机）
```

**为什么要分 `public/`**：Pages 会把"构建输出目录"里的所有文件原样公开。
早期把仓库根目录当输出目录，导致 `README.md`、`wrangler.toml`、原始照片都能被直接下载
（`https://你的域名/README.md` 能读到域名和部署细节）。收进 `public/` 后从结构上杜绝。

---

## 部署状态与关键设置

已通过 Git 集成自动部署。**每次 push 到 `main` 会自动重新部署，不用再手动上传。**

Pages 项目里必须确认这一项：

| 设置项 | 值 |
|---|---|
| Build command | 留空 |
| **Build output directory** | **`public`** |
| Framework preset | `None` |

> ⚠️ 如果 Build output directory 还是 `/`（仓库根），Pages 会重新把整个仓库公开出去。
> 改成 `public` 后重新部署一次即可（Deployments 页面点 Retry deployment 也行）。

另外两项一次性的：

- **Custom domains**：绑定 `xn--psszg58c6d346v9y1a.work`
- **Rules → Redirect Rules**：删掉原来那条"源域名 → xidian.edu.cn"的规则。
  它工作在 HTTP 层、优先级高于页面，留着就永远看不到动画。

### 日常改动

**方式 A：GitHub 网页改**（不用装东西）
打开 `public/index.html` → 铅笔图标 → 改 → `Commit changes` → 自动部署。

**方式 B：本地改**
```bash
git add -A && git commit -m "调整跳转时长" && git push
```

---

## 常用调整（都只改 public/index.html）

### 跳转等待时长 —— 三处必须一致

| 位置 | 当前值 |
|---|---|
| `<meta http-equiv="refresh" content="5;url=...">` | `5`（秒，无 JS 兜底） |
| CSS 变量 `--wait` | `5s`（底部进度条时长） |
| JS `var wait` | `5000`（毫秒） |

改成 7 秒就是：`content="7;url=..."`、`--wait: 7s`、`var wait = 7000`。
若 meta 的秒数小于动画时长，无 JS 环境会提前跳走、动画被截断。

### 旋转速度 / 方向

```css
--spin-duration: 6s;      /* 转一圈的时长，3s 会明显更快 */
--spin-direction: normal; /* reverse = 逆时针 */
```

### 目标地址

改三处：`<meta http-equiv="refresh">`、`<a id="go" href="...">`、JS 里的 `var target`。

### 未知路径的行为

Pages 默认会把未命中的路径回退到 `index.html`（所以 `/任意路径` 也是动画页，不是 404）。
这是可接受的行为；若要改成一律 302 到目标站，可在 `public/` 放一个 `_redirects`：

```
/:path+  https://www.xidian.edu.cn/  302
```

---

## 素材说明

原始照片是白底，直接旋转会在浅色背景上露出白色方块，所以做了抠图：角色是饱和暖黄绿
（饱和度 0.2~0.6），背景是几乎无饱和的白墙灰影（<0.05），用饱和度阈值配合
**从画面边缘的连通性**判定背景，再取最大连通块作为角色本体，边缘 1px 羽化。
右下角贴吧水印已通过裁掉底部约 4.5% 去除。

换图时：主体同样是"高饱和 + 纯色背景"的话，同思路可用；若主体是白/浅色（白玩偶、
文字 logo），饱和度法会失效，改用圆形裁切（`border-radius:50%` + `object-fit:cover`）旋转最省事。

> ⚠️ 该图来自网络（贴吧表情包），**个人自用可以，不适合用于学校官方页面或任何商业、公开宣传场景**。

---

## 注意事项

- **SEO**：这是 `200` + 延迟跳转，权重传递弱于 `301`。域名若有搜索权重或大量外链，
  应继续用 Redirect Rules 的 `301`；动画页更适合品牌短域名/名片域。
- **不要做开放重定向**：目标地址写死在页面里，别改成 `?to=` 参数拼接跳转目标，
  否则域名会成为钓鱼跳板，被浏览器和搜索方标记。
- **无障碍**：`prefers-reduced-motion: reduce` 时停转，但页面照常跳转。
- **中文域名**：分享时给 Unicode 形式（`西安奶龙大学.work`）或完整可点链接。

---

## 验证记录

**线上实测（`https://xn--psszg58c6d346v9y1a.work`）：**

| 项目 | 结果 |
|---|---|
| `/` | `200`，`text/html`，动画页内容齐全（文案、meta refresh、`location.replace`、`@keyframes spin`、素材引用、reduced-motion 分支全部命中） |
| 4 个素材 | 全部 `200`，`image/webp` / `image/png` 正确 |
| 旧 Redirect Rule | 已让路（否则 `/` 会是 302） |
| 未知路径 | `200` 回退到动画页（Pages 默认行为） |
| 仓库文件暴露 | **修复前** `/README.md`、`/wrangler.toml`、`/source-photo.jpg` 可被直接下载；已通过 `public/` 结构调整解决 |

**本地验证：**
- 页面在 1440×900 与 390×844 下用无头 Edge 渲染通过。
- **旋转动画无法用无头截图验证**：注入探针读 `getComputedStyle` 得到
  `playState=running` 但 `currentTime=0ms`，说明无头模式动画时钟不推进。
  已人工核对 CSS：单一 `transform: rotate()`、`linear infinite`、素材正方形且四角留 3% 余量。
- 本地 `wrangler dev` 的 HTTP 请求在本机环境超时（同环境 Python http.server 正常），
  故未能本地实测请求响应，改用线上实测替代。
