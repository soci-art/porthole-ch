# Porthole 探针计划（路线 B spike）

- 制定日期：2026-11-08
- 依据：`notes/INVESTIGATION.md`（路线 B 定案）、上游 `docs/SOURCE.md` / `docs/REBUILD.md`
- 本目录内容：`workflows/probe-build.yml`（Actions 工作流草案）、`scripts/extract_runtime_resources.sh`、`scripts/prepare_local_xcconfig.sh`、`verification/resources-manifest.txt`（本地提取验证清单）
- 本阶段不做：翻译、建仓、向 GitHub 推送。探针只回答一个问题——**在 GitHub Actions 的干净 macOS 上，能否按锁定提交补建缺失静态库并重建出一个结构与上游一致的未签名英文 IPA**。探针不过，不进入翻译阶段（避免约 5,000 条翻译白做）。

## 一、仓库就绪后的摆放与触发

新仓库根目录 = upstream v1.2.1 源码（含 `.gitmodules` 的 Madeira 子模块定义），外加：

| 本地文件 | 推送位置 |
|---|---|
| `probe-ci/workflows/probe-build.yml` | `.github/workflows/probe-build.yml` |
| `probe-ci/`（scripts、PROBE-PLAN、verification） | 仓库根目录同名 `probe-ci/` |

触发：GitHub 网页 Actions 页选 `probe-build (Porthole rebuild spike)` → Run workflow（工作流只设了 `workflow_dispatch`，push 不自动跑）。产物在该次运行的 Artifacts 区：`porthole-probe-build`（含重建 IPA、`probe-output/` 报告与 `probe-logs/` 全部编号日志，保留 14 天）。

## 二、阶段顺序与成功判据

工作流共 27 步，按阶段分组如下。每步 `set -euxo pipefail`、失败即停，日志以 `tee` 落到 `probe-logs/NN-*.log` 并随 artifact 上传。

| 阶段 | 步骤（工作流名） | 做什么 | 成功判据 |
|---|---|---|---|
| 0 环境 | Checkout / Toolchain report / Install build tools | 递归拉子模块；列出镜像内全部 Xcode 并选最新；brew 装 xcodegen/cmake/ninja/meson 等 | toolchain 日志打印出 `xcodebuild -version`；这是确认 Xcode 版本（未知项 2）的第一现场 |
| 1 锁定核对 | Verify pinned commits | 核对 Madeira `5fda6a0…` 及 Wine/FEX/DXMT/dock 四个锁定提交 | 五个 SHA 全部命中 `docs/SOURCE.md` 表 |
| 2 IPA 锚点 | Download upstream IPA and verify sha256 | 下载上游 1.2.1 IPA 并校验 `5a6d06aa…af7` | `shasum -c` 输出 OK，文件 199,771,062 字节 |
| 3 引擎源码 | Apply engine patches 0172-0176 | 按 `docs/SOURCE.md` 原样命令给五个树打补丁 | 五条 `git apply` 均无报错；`tools/engine.sh show` 诊断输出留档 |
| 4 资源与配置 | Extract runtime Resources / Prepare Local.xcconfig / Prepare StikJIT | IPA 提取 13 项资源；生成正式身份的 Local.xcconfig（脚本内先验 Engine.xcconfig 的 `3af3467-r1`）；下载校验 StikJIT 1.5.0 | 提取清单 13 项齐全（见第四节本地实测数）；`app/Vendor/StikJIT.xcframework` 存在 |
| 5 补建静态库 | wineserver base → dxmt headers+patch → madeira patch → FEX → Madeira build/ 下 ntdll-unix、win32u-unix、wineserver、dxmt-ios、ffmpeg、freetype-ios、gnutls-ios（顺序照 SOURCE.md） | 逐个脚本独立步骤、独立日志 | 每步退出码 0；win32u 步骤额外报告 `libwin32u_unix.a` 成员数（应为 89，见未知项 6） |
| 6 集库 | Collect and audit static libraries | 全盘搜集 `project.yml` 链接所需的 13 个库：自建优先、快照 4 库（gmp/gnutls/hogweed/nettle）兜底；专门全盘定位 `liblzma.a` | 13 个库全部落入 `build/probe-stage/lib`，缺任何一个即红并打印 MISSING 清单 |
| 7 组装 stage | Assemble RuntimeStage | lib（第 6 阶段）+ Resources（第 4 阶段提取物，符号链接）组 `probe-stage`，链为 `app/RuntimeStage`；断言 arm64ec farm 内有 `gdiplus.dll` | 上游自带 `tools/check_stage.sh` 通过（防用错 stage 出旧引擎包） |
| 8 编 App 与打包 | xcodegen / xcodebuild / package_app.sh / Structure diff | 生成工程、无签名 Release 构建、打未签名 IPA、与上游 IPA 出结构 diff 报告 | 产出 `probe-output/Porthole-1.2.1-probe-unsigned.ipa`；diff 报告生成（内容按第五节人工判读） |

**探针通过的总判据**：工作流全绿 **且** 第五节结构核对清单全部 OK（或差异有明确无害解释并记录）。全绿但结构不符（例如扩展缺失、引擎 ID 不对）不算通过。

## 三、本地已验证（2026-11-08，Linux 本机）

1. **资源提取脚本实跑通过**：对本地上游 IPA（sha256 校验先行）提取到临时目录，结果与报告 1.4/B-2 清单逐项一致——**13 项齐全、1,420 个文件、755,108,176 字节（720.1 MiB）**，分项如下；抽查 6 个文件（gdiplus.dll、cacert.pem、madeira-jit.js、prefix-template.tar.gz、gl/libMoltenVK.dylib、compat/love/lua51.dll）与 IPA 内字节哈希一致。完整文件清单存 `verification/resources-manifest.txt`（1,420 条）。验证后提取物已删除，只留清单。

| 条目 | 文件数 | 字节 |
|---|---:|---:|
| nls | 76 | 10,326,434 |
| aarch64-windows | 136 | 120,759,808 |
| arm64ec-windows | 422 | 377,735,174 |
| i386-windows | 728 | 194,460,160 |
| d3d12 | 8 | 30,196,689 |
| gl | 5 | 19,434,128 |
| compat | 3 | 335,800 |
| legal | 25 | 766,786 |
| licenses | 14 | 101,558 |
| prefix-template.tar.gz | 1 | 787,600 |
| cacert.pem | 1 | 189,462 |
| madeira-jit.js | 1 | 14,577 |
| x86_64-vcruntime（空目录占位） | 0 | 0 |
| **合计** | **1,420** | **755,108,176** |

注：本机 `/tmp` 是 512 MB 的 tmpfs，装不下 720 MiB 提取物，实跑目录用的是工作区磁盘；CI 运行器无此限制。
2. **xcconfig 脚本实跑通过**：在 upstream 的 Config 副本上生成 Local.xcconfig，值与 IPA 实读一致（Bundle ID `site.portholehq.app`、Hub `https://hub.portholehq.site:2053`、HubAppID `porthole-stable`、ReleaseKey `tPrTYtmPzMGC6Q3hvAhRDPPDgMekqkrP7qVy8TZAir4=`、SourceURL `https://github.com/tylerkaska112/PortHole`、Keychain/Storage 留空），且脚本对 Engine.xcconfig 的引擎 ID 校验生效。upstream 克隆未被修改。
3. **工作流校验通过**：`probe-build.yml` 经 python `yaml.safe_load` 解析成功（27 步）；全部 25 个 `run` 块经 `bash -n` 语法检查通过；结构 diff 步内嵌的 Python 已编译并以「上游 IPA 自比」实跑，8 个 Info.plist 键与 4 个扩展全部输出 OK。
4. 两个脚本均通过 `bash -n`；提取脚本带 zip-slip 防护与可选 sha256 校验。

## 四、已知未知项

1. **`liblzma.a` 来源**：全仓只有 `project.yml` 的 `-llzma` 一处提及，无脚本点名其出处（报告未决项 2）。可能来源：Madeira 某个 build 脚本的副产物、或 iOS SDK 自带。Collect 步会全盘 `find` 并顺带查 SDK 的 `usr/lib/liblzma*`，第一次运行即见分晓；若皆无，下一步考虑从 xz 源码交叉编译一个（独立小步，不难）。
2. **Xcode 版本**：`docs/SOURCE.md` 要求 Xcode 27 + Metal 工具链 32023（`build_dxmt_shader_headers.sh` 的注释提到 Metal 32023 的内建函数签名变化，是硬依赖线索）。GitHub 托管镜像是否已带 Xcode 27 无法预验；工作流选最新镜像 `macos-26` 并在 toolchain 步列全/选最新 Xcode。DXMT shader headers 步是版本不够时最可能先红的地方。
3. **脚本的本机路径假设（`tools/local.env`）**：`local.env` 不入库，作者机上放的是外置盘路径（`F4_BUILD_ROOT`、`STAGE`、`VCRUNTIME_DIR`、`GL_ASSETS`、`OVERRIDES*`）。工作流的对策：不跑原版 `stage_runtime.sh`（它的 Resources 来自快照、不完整），改为自组 stage，并显式设 `F4_BUILD_ROOT=<workspace>/build` 让 `check_stage.sh` 的「链接须落在 checkout 或构建根内」检查可过。但 Madeira `build/` 下各脚本内部是否还有写死的本机路径，只能逐个从日志里发现。
4. **Actions 时长**：从零编译 Wine unix 侧 + DXMT + FFmpeg + FEX 的总时长无先例数据；作业上限已设 360 分钟（托管上限）。超时对策（下一轮）：按库拆作业 + `actions/cache` 缓存 build 目录。
5. **宿主工具集**：Madeira 各 build 脚本需要的 brew 工具没有权威清单，工作流先装常见全集；缺失会以 `command not found` 在对应步暴露。
6. **win32u 成员数陷阱**：`docs/REBUILD.md` 载明 `build/win32u-unix/build.sh` 每跑一次就把 FreeType 再并进 `libwin32u_unix.a`，正常应 89 个成员（131/173 即有重复，需手工去重）。工作流只报告成员数、不自动改，判读后再决定。
7. **build 脚本间顺序**：工作流照 `docs/SOURCE.md` 的列举顺序（ntdll-unix、win32u-unix、wineserver、dxmt-ios、ffmpeg、freetype-ios、gnutls-ios），但该顺序未必是依赖顺序（如 win32u 需要 freetype 先行）。某步报缺前置产物时，按日志把顺序调前即可，脚本本身不用改。
8. **`apply_madeira_patch.sh` 的定位**：其主体补丁 0006 已 RETIRED，脚本可能直接走「already applied」分支，也可能小错退出；工作流此步做了容错记录（失败只留痕不拦路），是否真无害需看 `12-madeira-patch.log` 判读。
9. **`macos-26` 标签可用性**：若仓库启用 Actions 时该标签尚不可用，改 `macos-15` 并在此文档记录与 Xcode 27 的实际差距。

## 五、失败定位表

先下 artifact `porthole-probe-build`，按失败步名找同号日志：

| 失败步 | 日志 | 先看什么 |
|---|---|---|
| Toolchain report | `01-toolchain.log` | 镜像里到底有哪些 Xcode、metal 是否存在——决定未知项 2 |
| Verify pinned commits | `02-pinned-commits.log` | 哪个 SHA 没命中；多为子模块没拉全或新仓库推送时 gitlink 丢失 |
| Download upstream IPA | 作业日志 | 网络/资产改名；对照 `UPSTREAM_IPA_URL` 与发行页资产名 |
| Apply patches 0172-0176 | `03-patches.log` | 哪个补丁在哪棵树冲突；先确认第 1 阶段的 SHA 核对是通过的 |
| Extract runtime Resources | `04-extract-resources.log` | sha 不符或缺项清单（脚本会逐条打印缺的条目名） |
| Prepare Local.xcconfig | `05-local-xcconfig.log` | 多为 Engine.xcconfig 校验失败（引擎 ID 被改动过） |
| Prepare StikJIT | `06-stikjit.log` | digest mismatch = StikJIT 资产变更或下载不全 |
| wineserver base | `10-wineserver-base.log` | 哪些 server/*.c 编译失败（脚本逐个记录 err-*.txt 的汇总行） |
| DXMT shader headers | `11-dxmt-headers.log` | metal 编译报错 ≈ Xcode/Metal 版本问题（未知项 2 的主战场） |
| FEX iOS | `13-fex.log` | cmake 配置/编译错误；脚本注释自承其 configure 是「重建」的，先看 CMakeCache 相关行 |
| ntdll/win32u/wineserver/dxmt/ffmpeg/freetype/gnutls | `14`–`20` 号日志 | 缺前置库/工具时看未知项 5、7；win32u 另看成员数报告 |
| Collect libraries | `21-collect-libs.log` | MISSING 清单 + liblzma 全盘搜索结果（未知项 1 的答案在此） |
| Assemble RuntimeStage | `22-stage.log` | `check_stage.sh` 的 ✗ 行会直指哪个链接出了构建根 |
| xcodegen / xcodebuild | `23` / `24` 号日志 | 链接错误先回看第 6 阶段集的库是否齐、架构是否为 arm64 |
| Package | `25-package.log` | `scrub_paths.py` 的报错（路径清洗对构建者用户名的假设） |
| Structure diff | `26-diff.log` + `probe-output/structure-diff.txt` | 报告本身，红的不在这步、在内容里（见第六节） |

## 六、探针通过后：与上游 IPA 的结构核对清单

对 `structure-diff.txt` 与成品 IPA 逐项核（上游参照值均为 2026-11-08 本地实测）：

- [ ] **主 Info.plist 键全 OK**：Bundle ID `site.portholehq.app`；版本 `1.2.1` / build `688`；`PortholeEngine=3af3467-r1`、`PortholeEngineMadeira=3af3467`；`PortholeHubURL=https://hub.portholehq.site:2053`、`PortholeHubAppID=porthole-stable`；`PortholeReleaseKey` 与上游一致
- [ ] **4 个扩展齐全且身份一致**：`F4Activity.appex`（`site.portholehq.app.activity`，`com.apple.widgetkit-extension`）、`F4JITHelper.appex`（`.jithelper`，`com.apple.ar.viewer`）、`F4MemoryHost.appex`（`.MemoryHost`，`com.apple.ar.viewer`）、`F4Tunnel.appex`（`.tunnel`，`com.apple.networkextension.packet-tunnel`）
- [ ] **文件清单同构**：顶层条目集合与上游一致（diff 报告逐项列出）；Resources 部分与 `verification/resources-manifest.txt` 的 1,420 条对得上（提取复用，天然字节一致，重点看有没有漏装/错位）
- [ ] **框架**：`Frameworks/StikJIT.framework` 在包内（上游 Frameworks 共 4 个条目、18,348,366 字节）
- [ ] **大小量级**：主二进制 ≈ 69,502,848 字节（同量级即可，重建不要求字节相同）；未压缩总量 ≈ 866,927,101 字节；IPA 文件 ≈ 199,771,062 字节（200 MB 量级，偏差超过 ±20% 要查原因）
- [ ] **未签名形态**：无 `_CodeSignature`、无 `embedded.mobileprovision`，主二进制 cryptid=0（`package_app.sh` + 本地 `ipa_inspect.py` 复核）
- [ ] **Assets.car 在包内** ≈ 4,533,960 字节（图标/资源目录编译产物）
- [ ] 抽查引擎面：`arm64ec-windows` 422 个文件、`i386-windows` 728 个、`aarch64-windows` 136 个（与第三节表一致即资源无损）

全项通过 → 路线 B 成立，进入翻译阶段（按 `notes/INVESTIGATION.md` 第二部分的盘点逐条翻译、构建、开包销账，交付仍走既定发行版标准）。任一项不过 → 回到第五节定位表迭代工作流，不动翻译。

---

## 附记：运行 #1 结果与迭代 2（2026-11-08）

- 运行 #1（42448532585）失败于第 12 步 wineserver base：23 个 Wine server 对象 0 成功、约 5 秒全灭。根因已确证：`wine/build-macos/` 不在干净克隆里，而每个 `server/*.c` 第一行 `#include "config.h"` 只能由该目录的 `include/` 提供——它是作者本机用 Madeira `build/wine-macos/configure.sh` 生成的主机配置树，`docs/SOURCE.md` 漏写了这一步。完整证据链见 `notes/PROBE-RUN1-DIAGNOSIS.md`。
- 迭代 2 工作流改动：Homebrew 增 freetype/gnutls；补库前新增「Prepare wine/build-macos」步（Madeira `setup-llvm-mingw.sh` → `build/wine-macos/configure.sh` → Porthole `tools/fix_macos_config.sh` 对齐 config.h 三行）；全部补库步加失败时 err-*.txt 回显；新增 always() 的 err 文件收集步进 artifact。
- 另记：运行器最高 Xcode 为 26.6（文档要求 27），与本次失败无关（失败在预处理阶段），留待后续构建步验证。
