# 跳转动画页 · 旋转奶龙

Cloudflare Pages 静态跳转页：源域名进来自动播放动画，然后跳到目标站点。

**目标**：`https://www.xidian.edu.cn/`
**源域名**：`xn--psszg58c6d346v9y1a.work`（`西安奶龙大学.work`）

---

## 目录结构

```
index.html          动画页本体（要改的只有这一个文件）
_headers            禁止缓存 + noindex
spin.webp/.png      760×760 透明旋转素材
spin-small.webp/.png 420px 小图，≤600px 视口用
```

---

## 一次配置：让改动自动上线

配好之后，**再也不需要手动往 Cloudflare 上传**。改完推上去，Cloudflare 自动重新部署，
自定义域名也跟着项目走，不用重新绑定。

1. 在 GitHub 建一个空仓库（Private 也可以），比如 `xdu-splash`。
2. 本地关联并推上去：
   ```bash
   git remote add origin https://github.com/<你的用户名>/xdu-splash.git
   git push -u origin main
   ```
3. Cloudflare Dashboard → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**，
   选这个仓库。
4. 构建设置（纯静态，全部留空/按下表填）：

   | 项 | 值 |
   |---|---|
   | Framework preset | `None` |
   | Build command | 留空 |
   | Build output directory | `/` |

5. 部署完，进项目 → **Custom domains** → 绑定 `xn--psszg58c6d346v9y1a.work`（只需一次）。
6. 到 **Rules → Redirect Rules**，把原来那条"源域名 → xidian.edu.cn"的规则**删掉**。
   它工作在 HTTP 层，优先级高于页面，留着就永远看不到动画。

### 日常改动的两种方式

**方式 A：直接在 GitHub 网页改**（不用装任何东西）
打开仓库里的 `index.html` → 点铅笔图标 → 改 → `Commit changes` → Cloudflare 自动部署。

**方式 B：本地改**
```bash
git add -A && git commit -m "调整跳转时长" && git push
```

> 每次 push 还会额外生成一个预览域名（形如 `<hash>.xdu-splash.pages.dev`），
> 可以先用它确认效果，再决定是否推到生产分支。

### 不想用 GitHub 的话

本地装一次 wrangler，之后一条命令就更新，不用进 Cloudflare 网页：

```bash
npx wrangler pages deploy . --project-name=xdu-splash
```

自定义域名同样保留，只需在最后一次 setup 里绑一次。

---

## 常用调整（都只改 index.html）

### 跳转等待时长 —— 三处必须一致

| 位置 | 当前值 |
|---|---|
| `<meta http-equiv="refresh" content="5;url=...">` | `5`（秒，无 JS 兜底） |
| CSS 变量 `--wait` | `5s`（底部进度条时长） |
| JS `var wait` | `5000`（毫秒） |

改成 7 秒就是：`content="7;url=..."`、`--wait: 7s`、`var wait = 7000`。
若 meta 的秒数小于实际动画时长，无 JS 环境会提前跳走、动画被截断。

### 旋转速度 / 方向

```css
--spin-duration: 6s;      /* 转一圈的时长，3s 会明显更快 */
--spin-direction: normal; /* reverse = 逆时针 */
```

### 目标地址

改三处：`<meta http-equiv="refresh">`、`<a id="go" href="...">`、JS 里的 `var target`。

---

## 素材说明

原始照片是白底，直接旋转会在浅色背景上露出白色方块，所以做了抠图：角色是饱和暖黄绿
（饱和度 0.2~0.6），背景是几乎无饱和的白墙灰影（<0.05），用饱和度阈值配合
**从画面边缘的连通性**判定背景，再取最大连通块作为角色本体，边缘 1px 羽化。
右下角的贴吧水印已通过裁掉底部约 4.5% 去除。

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

## 验证情况

- 页面在 1440×900 与 390×844 下用无头 Edge 实际渲染通过。
- **旋转动画无法用无头截图验证**：注入探针读 `getComputedStyle` 得到
  `playState=running` 但 `currentTime=0ms`，说明无头模式的动画时钟不推进。
  已人工核对 CSS：单一 `transform: rotate()`、`linear infinite`、素材正方形且四角留 3% 余量。
