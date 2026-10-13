import ssl
import time
import urllib.error
import urllib.request

BASE = "https://xn--psszg58c6d346v9y1a.work"
CTX = ssl.create_default_context()


def get(path):
    req = urllib.request.Request(BASE + path)
    req.add_header("User-Agent", "Mozilla/5.0 (verification)")
    try:
        with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return None, str(e).encode()


print("轮询线上状态，观察 public/ 重构是否已生效…")
print("期望：/ 仍是动画页；/README.md 与 /wrangler.toml 变成 404 或回退页")
print()
for i in range(1, 13):
    root_st, root = get("/")
    rm_st, rm = get("/README.md")
    wt_st, wt = get("/wrangler.toml")

    is_anim = "正在前往" in root.decode("utf-8", "replace")
    leak_readme = rm.startswith(b"# ") or b"Cloudflare Pages" in rm
    leak_toml = b'name = "redirect"' in wt

    print(f"[{i:2d}] /={root_st} 动画页={'是' if is_anim else '否'} | "
          f"README={rm_st} 泄露={'是' if leak_readme else '否'} | "
          f"wrangler.toml={wt_st} 泄露={'是' if leak_toml else '否'}")

    if is_anim and not leak_readme and not leak_toml:
        print("\n=> 已生效：动画页正常，且仓库文件不再泄露。")
        break
    time.sleep(10)
else:
    print("\n=> 12 次轮询内未达到期望状态，见上表。")
