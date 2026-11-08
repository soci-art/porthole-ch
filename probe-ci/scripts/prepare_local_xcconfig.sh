#!/bin/bash
# prepare_local_xcconfig.sh — 生成 app/Config/Local.xcconfig，填上游正式包的构建身份值。
#
# 为什么要填（调查报告 INVESTIGATION.md B-1 / 1.5）：Local.xcconfig 若留空/用 example 的占位值，
# 重建包会丢官方兼容列表与自更新通道、兼容徽章清零，且 Bundle ID 变成 com.example.porthole。
# 下列值全部来自上游 v1.2.1 正式 IPA 的 Info.plist 实读（work/unpacked/Payload/Porthole.app/
# Info.plist，2026-11-08 本地核验），不是 example 的示例值：
#   PortholeBuiltBundleID = site.portholehq.app        → PORTHOLE_BUNDLE_ID
#   PortholeHubURL        = https://hub.portholehq.site:2053 → PORTHOLE_HUB_URL
#   PortholeHubAppID      = porthole-stable            → PORTHOLE_HUB_APP_ID
#     （注意：app/Config/Porthole.xcconfig 的默认是 porthole、example 也是 porthole，
#       正式包用的是 porthole-stable，必须在 Local 里覆盖）
#   PortholeReleaseKey    = tPrTYtmPzMGC6Q3hvAhRDPPDgMekqkrP7qVy8TZAir4= → PORTHOLE_RELEASE_KEY
#     （这是发行“公钥”，随公开 IPA 分发、任何人可读；对应私钥不在任何仓库里）
#   PortholeSourceURL     = https://github.com/tylerkaska112/PortHole → PORTHOLE_SOURCE_URL
#   PortholeKeychainService / PortholeStorageFolder 在正式包里均为空 → 本文件同样留空（走默认）
#
# 引擎 ID 不写在本文件里：PORTHOLE_ENGINE_ID / PORTHOLE_ENGINE_MADEIRA 由 app/Config/
# Engine.xcconfig 提供（已入库，值 3af3467-r1 / 3af3467），Porthole.xcconfig 先 include 它、
# 再 include 本文件。本脚本只校验 Engine.xcconfig 的值无误，不对它做任何修改。
#
# xcconfig 语法注意：值里的 "//" 会被当注释，故 URL 一律写成 https:/$()/... 形式（与 example 同法）。
#
# 用法：prepare_local_xcconfig.sh [仓库根目录]   （默认：脚本所在 probe-ci/scripts 的上两级）
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
CFG_DIR="$ROOT/app/Config"
[ -d "$CFG_DIR" ] || { echo "✗ 找不到 $CFG_DIR（仓库根目录传错了？）" >&2; exit 1; }
[ -f "$CFG_DIR/Local.xcconfig.example" ] || { echo "✗ 缺 Local.xcconfig.example" >&2; exit 1; }

# 先校验引擎 ID（报告 1.5：正式包 PortholeEngine = 3af3467-r1）
grep -qE '^PORTHOLE_ENGINE_ID[[:space:]]*=[[:space:]]*3af3467-r1([[:space:]]|$)' "$CFG_DIR/Engine.xcconfig" \
  || { echo "✗ Engine.xcconfig 的 PORTHOLE_ENGINE_ID 不是 3af3467-r1，先核对再构建" >&2; exit 1; }
grep -qE '^PORTHOLE_ENGINE_MADEIRA[[:space:]]*=[[:space:]]*3af3467([[:space:]]|$)' "$CFG_DIR/Engine.xcconfig" \
  || { echo "✗ Engine.xcconfig 的 PORTHOLE_ENGINE_MADEIRA 不是 3af3467" >&2; exit 1; }
echo "✓ Engine.xcconfig 引擎 ID = 3af3467-r1（Madeira 3af3467），与正式包一致"

cat > "$CFG_DIR/Local.xcconfig" <<'EOF'
// 由 probe-ci/scripts/prepare_local_xcconfig.sh 生成（勿手改；改值请改脚本）。
// 值来自上游 v1.2.1 正式 IPA 的 Info.plist 实读（调查报告 INVESTIGATION.md 1.5），
// 目的是让重建包与正式包的构建身份一致：同一 Bundle ID、同一 Hub、同一发行公钥。
PORTHOLE_BUNDLE_ID = site.portholehq.app
// 正式包里这两项为空（走 App 默认），保持留空，不要填 example 的 com.example 占位值。
PORTHOLE_KEYCHAIN_SERVICE =
PORTHOLE_STORAGE_FOLDER =
// xcconfig 里 "//" 是注释，URL 必须写成 https:/$()/... 形式。
PORTHOLE_HUB_URL = https:/$()/hub.portholehq.site:2053
PORTHOLE_HUB_APP_ID = porthole-stable
PORTHOLE_SOURCE_URL = https:/$()/github.com/tylerkaska112/PortHole
// 发行公钥（base64，随公开 IPA 分发）：带此公钥的包只接受对应私钥签名的自更新。
PORTHOLE_RELEASE_KEY = tPrTYtmPzMGC6Q3hvAhRDPPDgMekqkrP7qVy8TZAir4=
EOF

echo "✓ 已生成 $CFG_DIR/Local.xcconfig:"
cat "$CFG_DIR/Local.xcconfig"
