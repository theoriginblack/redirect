import ssl
import urllib.error
import urllib.request

BASE = "https://xn--psszg58c6d346v9y1a.work"
CTX = ssl.create_default_context()


def get(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("User-Agent", "Mozilla/5.0 (verification)")
    try:
        with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception as e:
        return None, {}, str(e).encode()


print("=== 指纹测试：区分 旧版本(root 输出) / 新版本(public 输出) ===")
print()

st, hd, body = get("/")
txt = body.decode("utf-8", "replace")
print(f"/                 status={st}  {len(body)} bytes")
print(f"   含动画页标记      : {'是' if '正在前往' in txt else '否'}")

st, hd, body = get("/README.md")
rm = body.decode("utf-8", "replace")
# 新版 README 独有的句子（旧版没有"为什么要分 public"这段）
new_marker = "为什么要分 `public/`"
old_marker = "一次配置：让改动自动上线"
print(f"/README.md        status={st}  {len(body)} bytes")
print(f"   是新版 README     : {'是' if new_marker in rm else '否'}")
print(f"   是旧版 README     : {'是' if old_marker in rm else '否'}")
print(f"   首行              : {rm.splitlines()[0][:60] if rm.strip() else '(空/非文本)'!r}")

st, hd, body = get("/wrangler.toml")
wt = body.decode("utf-8", "replace")
print(f"/wrangler.toml    status={st}  {len(body)} bytes")
print(f"   含 ./public       : {'是' if './public' in wt else '否'}")
print(f"   含 directory = \".\" : {'是' if 'directory = \".\"' in wt else '否'}")

st, hd, body = get("/source-photo.jpg")
print(f"/source-photo.jpg status={st}  {len(body)} bytes  type={hd.get('Content-Type')}")

print()
print("=== 素材仍应正常 ===")
for p in ["/spin.webp", "/spin-small.webp"]:
    st, hd, body = get(p)
    print(f"{p:18s} status={st}  type={hd.get('Content-Type')}  {len(body)} bytes")

print()
print("=== 部署元信息 ===")
st, hd, body = get("/")
for k in ("CF-RAY", "Last-Modified", "ETag", "Age", "CF-Cache-Status", "Server"):
    if hd.get(k):
        print(f"   {k}: {hd[k]}")
