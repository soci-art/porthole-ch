#!/bin/bash
# extract_runtime_resources.sh — 从上游正式 IPA 中提取 RuntimeStage/Resources 所需的运行时资源。
#
# 为什么从 IPA 提取（调查报告 INVESTIGATION.md B-2 定案）：
#   Madeira 快照（vendor/Madeira/app/Madeira）并不完整——i386-windows/* 不提交（由 build 生成）、
#   gl/*.dylib 是 mesa-ios/moltenvk 构建产物、个别 DLL 是构建产物。IPA 里的资源则与
#   app/project.yml 的资源清单逐项对应，且字节级等于上游 1.2.1 出厂状态（含上游重编的 DLL）。
#
# 清单来源（逐项核对过）：
#   - app/project.yml 中 Porthole target 的 RuntimeStage/Resources/* 条目（10 个文件夹 + 3 个文件）
#   - tools/stage_runtime.sh 向 $STAGE/Resources 放的同名条目
#   x86_64-vcruntime 在 IPA 里是空目录（package_app.sh 打包时删光 VC 运行时 DLL，App 运行时自行
#   从微软下载），project.yml 仍要求该文件夹存在，故这里建一个空目录占位。
#   arm64ec-windows 在 IPA 中已含 patches/0001 的 gdiplus.dll（本地核验在包内），无需再叠加。
#
# 用法：
#   extract_runtime_resources.sh <ipa路径> <输出目录> [--manifest <清单文件>] [--sha256 <期望值>]
# 输出目录将得到与 RuntimeStage/Resources 相同的布局（可直接拷/链为 stage 的 Resources）。
# 退出码：0 = 清单 13 项齐全且全部提取成功；非 0 = 缺项或校验失败（缺项会逐条打印）。
set -euo pipefail

IPA="${1:?用法: extract_runtime_resources.sh <ipa> <outdir> [--manifest f] [--sha256 hex]}"
OUT="${2:?用法: extract_runtime_resources.sh <ipa> <outdir> [--manifest f] [--sha256 hex]}"
shift 2
MANIFEST=""
EXPECT_SHA=""
while [ $# -gt 0 ]; do
  case "$1" in
    --manifest) MANIFEST="$2"; shift 2 ;;
    --sha256)   EXPECT_SHA="$2"; shift 2 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
done

[ -f "$IPA" ] || { echo "✗ IPA 不存在: $IPA" >&2; exit 1; }
mkdir -p "$OUT"

# 提取用内嵌 python3（Linux/macOS 通用；带 zip-slip 防护，拒绝 ../ 与绝对路径条目）。
IPA="$IPA" OUT="$OUT" MANIFEST="$MANIFEST" EXPECT_SHA="$EXPECT_SHA" python3 - <<'PYEOF'
import hashlib, os, sys, zipfile
from pathlib import Path

ipa = Path(os.environ["IPA"]); out = Path(os.environ["OUT"])
manifest = os.environ.get("MANIFEST") or None
expect_sha = (os.environ.get("EXPECT_SHA") or "").lower()

if expect_sha:
    h = hashlib.sha256(ipa.read_bytes()).hexdigest()
    print(f"IPA sha256: {h}")
    if h != expect_sha:
        print(f"✗ sha256 不符，期望 {expect_sha}", file=sys.stderr); sys.exit(1)
    print("✓ sha256 校验通过")

# 清单：(条目名, 类型) —— 与 app/project.yml 的 RuntimeStage/Resources 条目逐项一致
DIRS  = ["nls", "aarch64-windows", "arm64ec-windows", "i386-windows", "d3d12",
         "gl", "compat", "legal", "licenses"]
FILES = ["prefix-template.tar.gz", "cacert.pem", "madeira-jit.js"]
EMPTY_DIRS = ["x86_64-vcruntime"]          # IPA 内为空目录，仅占位
APP_PREFIX = "Payload/Porthole.app/"

z = zipfile.ZipFile(ipa)
names = set(z.namelist())
missing, rows, manifest_lines = [], [], []
total_files = total_bytes = 0

def emit(relpath, data):
    dest = out / relpath
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    manifest_lines.append(f"{len(data):>12}  {relpath}")

for d in DIRS:
    prefix = f"{APP_PREFIX}{d}/"
    entries = [i for i in z.infolist() if i.filename.startswith(prefix) and not i.is_dir()]
    if not entries:
        missing.append(d); continue
    b = 0
    for i in entries:
        rel = i.filename[len(APP_PREFIX):]
        # zip-slip 防护：条目必须落在输出目录内
        if ".." in Path(rel).parts or rel.startswith("/"):
            print(f"✗ 拒绝不安全条目: {i.filename}", file=sys.stderr); sys.exit(1)
        data = z.read(i); emit(rel, data); b += len(data)
    rows.append((d, len(entries), b)); total_files += len(entries); total_bytes += b

for f in FILES:
    key = f"{APP_PREFIX}{f}"
    if key not in names:
        missing.append(f); continue
    data = z.read(key); emit(f, data)
    rows.append((f, 1, len(data))); total_files += 1; total_bytes += len(data)

for d in EMPTY_DIRS:
    (out / d).mkdir(parents=True, exist_ok=True)
    rows.append((d + " (空目录占位)", 0, 0))

print(f"\n{'条目':<24}{'文件数':>8}{'字节':>16}")
for name, c, b in rows:
    print(f"{name:<24}{c:>8}{b:>16,}")
print(f"{'合计':<24}{total_files:>8}{total_bytes:>16,}  ({total_bytes/1048576:.1f} MiB)")

if manifest:
    Path(manifest).parent.mkdir(parents=True, exist_ok=True)
    Path(manifest).write_text("\n".join(sorted(manifest_lines)) + "\n")
    print(f"清单已写: {manifest}（{len(manifest_lines)} 条）")

if missing:
    print("✗ IPA 中缺以下资源条目: " + ", ".join(missing), file=sys.stderr); sys.exit(1)
print(f"✓ 清单 {len(DIRS)+len(FILES)+len(EMPTY_DIRS)} 项齐全，提取到 {out}")
PYEOF
