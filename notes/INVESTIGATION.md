# Porthole 汉化项目 · 技术调查报告

- 调查日期：2026-11-08
- 上游：https://github.com/tylerkaska112/Porthole ，本地克隆 `~/workspace/porthole-zh/upstream`，HEAD `0786a24fa97647491c942db6279ad3610dcbb48a`（= 标签 `v1.2.1`）
- 范围：只做调查与盘点，未开始翻译、未建仓/fork、未向 GitHub 推送任何东西
- 汉化标准（Grace 长期规则）：除日志与诊断内容外，所有用户可见文案全量译简体中文，包括全部报错、提示与硬编码文案；核验须用源码全量盘点比对，不能只数官方语言目录

---

## 结论先行

1. **上游没有任何本地化机制**：仓库与 IPA 内均无 `.lproj`/`.xcstrings`/`.strings`（0 个），源码中 `NSLocalizedString`/`LocalizedStringKey`/`String(localized:)` 为 **0 处**，全部文案是 Swift/ObjC 源码硬编码字面量（app+Packages 共 23,786 处字面量）。
2. **路线 A（只重打包注入语言包）只能覆盖约 5–7% 的用户可见文案，且对报错类文案覆盖率为 0**——因为绝大多数文案走的是 `String` 类型变量/自定义组件参数，运行时根本不查语言包；会查语言包的只有直接写进 SwiftUI 控件的字面量（约 396 处）和 3 个 `LocalizedStringResource`。
3. **推荐路线 B（源码原地翻译 + 云端 Mac 只编译 App 本体）**：它是唯一能让「所有报错、提示都汉化」真正达成的路线。但有一个必须先打通的前置关卡：App 链接的静态引擎库有一多半不在任何公开仓库里（是上游作者本机用 Madeira 的 build 脚本编译、被 .gitignore 排除的产物），需要在云端 Mac 上先做一次「只编译缺失静态库」的探针（spike）；运行时资源（DLL farm 等）则可从上游 IPA 里原样提取复用，已核验与工程的资源清单一一对应。
4. **路线 C（二进制字符串 patch）不可行**：Swift 字面量的长度/存储方式、中文 UTF-8 膨胀、插值碎片化、字面量去重共享，决定了它最多 patch 个别短串，无法全量。

---

## 一、上游 v1.2.1 IPA 核验

### 1.1 下载与校验

- 资产地址（GitHub API `repos/tylerkaska112/Porthole/releases/tags/v1.2.1` 查得）：
  - IPA：`https://github.com/tylerkaska112/Porthole/releases/download/v1.2.1/Porthole-1.2.1-688.ipa`
  - 校验文件：同目录 `Porthole-1.2.1-688.ipa.sha256`
- 本地副本：`~/workspace/porthole-zh/downloads/Porthole-1.2.1-688.ipa`，**199,771,062 字节**（与 API 报告的资产大小一致）
- SHA-256 实测：`5a6d06aa00cd05d76c5fab1a0a0380a38c43fcdd4790bf6f845744fb7e0dfaf7`
  - 与 v1.2.1 发行说明公布值 **一致**；与官方 `.sha256` 资产内容 **一致**（三方吻合）

### 1.2 ipa_inspect 结果

命令：`source ~/workspace/ipa-repack/env.sh && python3 ~/workspace/ipa-repack/scripts/ipa_inspect.py Porthole-1.2.1-688.ipa`（完整输出存 `~/workspace/porthole-zh/work/inspect.json`）

| 项 | 值 |
|---|---|
| Bundle ID | `site.portholehq.app` |
| 版本 | 1.2.1（build 688），最低系统 iOS 18.0 |
| 已有语言 | **无**（`languages: []`；Info.plist 无 `CFBundleLocalizations`，开发区域 `en`） |
| 签名状态 | 未签名（无 `_CodeSignature`、无描述文件），cryptid=0 |
| 主二进制 | `Porthole`，**69,502,848 字节**，arm64 单架构 |
| 框架 | 仅 `StikJIT.framework`（第三方 JIT/配对库，Rust 写的 idevice） |
| Assets.car | 4,533,960 字节 |
| 包内条目 | 1,481 个 |

### 1.3 扩展清单（4 个，解包核对 Info.plist）

| 扩展 | Bundle ID | 扩展点 |
|---|---|---|
| F4Activity | site.portholehq.app.activity | WidgetKit（下载进度 Live Activity） |
| F4JITHelper | site.portholehq.app.jithelper | com.apple.ar.viewer（借道启动的 JIT 助手） |
| F4MemoryHost | site.portholehq.app.MemoryHost | com.apple.ar.viewer（借道启动的内存捐赠） |
| F4Tunnel | site.portholehq.app.tunnel | com.apple.networkextension.packet-tunnel |

### 1.4 包内可改文本资产：几乎没有

- 全包检索 `.strings`/`.lproj`/`.xcstrings`/`Localizable`/`InfoPlist.strings`：**0 命中**
- inspect 报出的「可改文本资产」只有：`StikJIT.framework` 的 `legacy.js`/`universal.js`（第三方 JIT 脚本）、主程序与 JIT 助手的 `madeira-jit.js`（JIT 注入脚本）、`Metadata.appintents/version.json`（系统生成的元数据）——**没有一个是 App 界面文案**
- 包体构成（未压缩）：Windows DLL farm 三套 `arm64ec-windows` 377.7 MB + `i386-windows` 194.5 MB + `aarch64-windows` 120.8 MB，其次主二进制 69.5 MB、`d3d12/` 30.2 MB、`gl/` 19.4 MB、扩展 18.9 MB、框架 18.3 MB。即 IPA 的绝大部分是运行时资源，界面文案全部编译在 5 个 Mach-O 二进制里（主程序 + 4 扩展，其中 F4JITHelper 还内嵌一份 StikJIT）

### 1.5 IPA 内 Info.plist 里的构建期配置（对路线 B 重要）

解包主 Info.plist 读到上游正式包的构建参数（源码构建时若留空会丢失对应功能）：

- `PortholeEngine = 3af3467-r1`、`PortholeEngineMadeira = 3af3467`（兼容性徽章按引擎 ID 计数，汉化版应沿用）
- `PortholeHubURL = https://hub.portholehq.site:2053`、`PortholeHubAppID = porthole-stable`（更新/兼容报告服务器；`app/Config/Local.xcconfig.example` 明说留空即无此功能）
- `PortholeReleaseKey = tPrTYtmPzMGC6Q3hvAhRDPPDgMekqkrP7qVy8TZAir4=`（带此公钥的包只接受对应私钥签名的自更新）

---

## 二、文案盘点（源码全量提取）

### 2.1 提取方法

- 脚本：`~/workspace/porthole-zh/work/inventory.py`（结果 `work/inventory.json`）
- 范围：`upstream/app` + `upstream/Packages` 下全部 Swift/ObjC 源码（`.swift/.m/.mm/.h/.c`），共 **383 个文件**（其中 Swift 341 个、ObjC 实现 10 个，其余为头文件/C）
- 方法：正则词法提取 `"..."` 与 `"""..."""` 字面量（含转义与 `\(...)` 插值），再按所在行上下文做启发式分类；关键类别另用 grep 严格口径（控件名后紧跟 `"`）复核一遍
- 注意：第一轮分类是**初步盘点**，残余类里混有需逐条人工判定的条目；精确的「必译清单」要在翻译阶段逐条审定（符合既定标准的做法），本报告给量级与构成。
### 2.2 总量与分布

- 全部字面量：**23,786 处 / 13,220 条不重复文本**
- 按区域：`app/Sources`（界面+各商店+核心）13,955 处；`app/Runtime`（引擎胶水，多为日志与给 Windows 程序用的数据）5,235 处；`Packages/LauncherCore` 384 处；扩展等其它 48 处；**测试代码 4,122 处（不进产品，排除）**；`launcher-sign` 命令行工具 42 处（macOS 工具，非 iOS 界面，排除）
- 产品代码（排除测试与 CLI）约 **19,622 处**

### 2.3 分类统计（第一轮，含测试代码在内的全量口径）

| 类 | 出现 | 不重复 | 说明 |
|---|---|---|---|
| (a) 行上下文含 SwiftUI 控件/命名参数 | 2,510 | 1,840 | 含 `title:"…"` 等命名参数——其中只有一小部分真走 `LocalizedStringKey`（见 2.4） |
| (b1) throw / NSError 行内字面量 | 369 | 344 | grep 复核：含字面量的 `throw` 行 372 行 |
| (b2) errorDescription 作用域内句子 | 74 | 74 | 分布在 25 个文件；全仓 `errorDescription` 出现 41 处、`LocalizedError` 37 处（36 个文件） |
| (b3) 其它句子式字面量（残余） | 4,903 | 4,351 | 状态串、进度串、错误详情、数据模板混合，抽样见 2.5 |
| (b4) 其它短语式字面量（残余） | 2,906 | 1,780 | 同上 |
| (d) 日志上下文（LogStore/print/NSLog 等） | 957 | 796 | 自定义日志 `LogStore.shared.log(...)` 遍布全仓（`LogStore` 全仓出现 521 次） |
| (d) 单 token 标识/键名/文件名/SF Symbol | 7,168 | 3,339 | 如 `site.portholehq.app`、`shippingbox.fill`、UserDefaults 键 |
| (d) 纯符号/数字/格式符 | 3,270 + 13 | 642 + 7 | OID、路径分隔、颜色值、`%lld` 等 |
| (d) 空串/常量名/URL | 804 + 779 + 106 | — | — |

**用户可见文案量级估计：约 6,000–7,500 处出现 / 约 4,500–5,500 条不重复文本**（(a)+(b1)+(b2) 加残余类抽样校准后的可见部分）。

### 2.4 关键结构事实（决定路线 A 上限）

- **严格口径的 SwiftUI 直接字面量只有约 396 处**：`Text("` 248、`Label("` 55、`Button("` 46、`.alert("` 6、`navigationTitle("` 6、`ProgressView("` 5、`TextField("` 4、`Picker("` 3、`Section("` 3、`SecureField("` 2、`Toggle("` 1、`accessibilityLabel("` 14、`accessibilityHint("` 3
- 而 `Text(` 总共 646 处——**其余约 400 处喂的是变量**（如 `Text(context.state.title)`、`Text(state.line)`，见 `app/Activity/DownloadLiveActivity.swift:27-73`），字符串在别处以 `String` 属性构造
- 命名参数字面量（`title:/message:/subtitle:/placeholder:` 等）共 **1,552 处**，大多传给自定义组件：全仓有 **62 处 `let title: String` 形式的组件定义**、60 处 `var title: String` 计算属性——参数是 `String` 不是 `LocalizedStringKey`，**运行时不查语言包**
- **报错呈现方式**：`.alert(` 全仓只有 6 处；错误靠 `catch { self.error = error.localizedDescription }` 写进状态串再由自定义界面显示（`localizedDescription` 全仓 192 处；样例 `app/Sources/UI/AddGameFlow.swift:303-304`、`app/Sources/UI/Reports/ReportsScreen.swift:181`）。错误文本源头 = `LocalizedError.errorDescription` 实现（41 处提及）+ 自定义错误结构体的 message 字段 + throw 点字面量（369 处）
- 唯一真正的本地化类型：`LocalizedStringResource` **仅 3 处**（`app/Sources/Shared/DownloadActivityAttributes.swift:41/53/65`，Live Activity 的 Pause/Resume/Cancel downloads）
- `Text(verbatim:` 0 处

### 2.5 样例（每类摘录，路径:行号）

(a) SwiftUI 直接字面量（节选自盘点 A 类与严格 grep）：

- `Text("Games you own")` 类标题、按钮与导航标题等（严格口径清单见 2.4 计数）

(b) 目录机制够不着的文案：

- `Packages/LauncherCore/Sources/LauncherCore/Network/Transport.swift:23` `"The server sent something unexpected."`（错误枚举）
- `Packages/LauncherCore/Sources/LauncherCore/Network/Transport.swift:26` `"The download was damaged (its checksum doesn't match). Try again."`
- `Packages/LauncherCore/Sources/LauncherCore/Stores/CredentialVault.swift:173` `"The certificate has expired."`
- `Packages/LauncherCore/Sources/LauncherCore/Signing/IPAInspector.swift:41` `"no .app in Payload"`（throw 点）
- `app/Sources/.../IPASigner.swift:230` `"Signing the app…"`、`:225` `"Sealing the app's files…"`（进度提示，走状态串）
- `app/Sources/UI/Game/SharedBindsViews.swift:156` `"Reported. Thank you."`（成功提示赋值给 message 状态）

(d) 应排除：

- 日志：`"[import] failed: \(e.localizedDescription)"`（`AddGameFlow.swift:303`，同行还把同一错误赋给状态——日志串本身不译，错误源头译）
- 内部标识：`'PortholeKeychainService'`、`'CFBundleExecutable'`、注册表路径 `'Software\\Wow6432Node\\Ubisoft\\Launcher'`、Windows 路径 `'C:\\Program Files (x86)\\...'`（给模拟环境的数据）
- 数据而非文案：GPU 型号 `'Intel(R) UHD Graphics 630'`（`GPUCards.swift`，呈现给 Windows 游戏的硬件名）、颜色 `'#4C8DFF'`

### 2.6 Info.plist 用户可见项（c 类）

源码 5 个 plist（`app/Info.plist`、`app/Activity|Helper|MemoryHost|Tunnel/Info.plist`），IPA 解包复核一致：

- **权限说明只有 1 条**：主程序 `NSLocalNetworkUsageDescription = "Porthole uses the local network to pair this iPhone with itself so JIT can be switched on without a computer."`（4 个扩展的 plist 均无 UsageDescription）
- 显示名：主程序 `Porthole`（专有名词不译）；扩展 `Downloads` / `JIT Helper` / `JIT Tunnel` / `Memory Host`（在 `app/project.yml:186/214/242/271` 定义；只有 Downloads 会出现在锁屏 Live Activity 上）
- 另有 2 个打包的快捷指令文件 `Porthole Cellular On/Off.shortcut`（`app/Shortcuts/`），其内部名称属用户可见小项

---

## 三、路线评估

### 路线 A：只重打包——注入 zh-Hans.lproj/Localizable.strings + InfoPlist.strings

做法：解包上游 IPA，在 `Porthole.app` 下加 `zh-Hans.lproj/Localizable.strings`（键=英文原文）与 `InfoPlist.strings`，在 Info.plist 的 `CFBundleLocalizations` 登记 zh-Hans，去签名重打包（现有流水线 `ipa_localize.py`/`ipa_repack_unsigned.py` 直接支持）。

**能覆盖（约 400 处，占可见文案约 5–7%）：**

- SwiftUI 直接字面量约 396 处：这类字面量在编译后以 `LocalizedStringKey` 运行时查主包 `Localizable.strings`，键就是英文原文（带插值的键要用格式符对齐，对不上就静默回退英文）
- 3 个 `LocalizedStringResource`（灵动岛/锁屏的 Pause/Resume/Cancel downloads）
- `InfoPlist.strings`：本地网络权限弹窗那 1 条 + 扩展显示名

**覆盖不了（约 93–95%，且含全部报错）：**

- 全部错误文案：`errorDescription` 与 NSError 的文本是**逐字使用**的，Foundation 不拿它当键去查表；throw 点、自定义错误结构体的 message 同理 → **报错覆盖率 0**
- 全部状态/进度/提示串（`String` 属性与状态变量，如「Signing the app…」）
- 1,552 处命名参数字面量中的绝大部分（自定义组件的 `String` 参数不查表）
- `Text(变量)` 的约 400 处、拼接/三元构造的文案
- 扩展二进制内的同类文案同理（语言包只作用于主包查找，扩展需各自放包且同样受上述机制限制）

**判定：不达标。** 与 Grace 的标准（报错提示一个不留）直接冲突，只能作为临时体验版，不能作为交付路线。

### 路线 C：二进制字符串 patch

对解包主二进制实测：`strings` 可见 419,648 条，其中句子式英文约 1,629 条（窄口径）——文案确实以明文片段存在。但不可行，原因：

1. **长度**：Swift 字面量带长度元数据（小串内联、大串 {指针,长度}），中文 UTF-8 每字 3 字节，译文的字节长度普遍不等于英文原长；原位 patch 只能等长或更短，挪动数据会破坏全二进制的相对偏移引用
2. **插值碎片化**：带 `\(...)` 的句子在二进制里是碎片（实测 `strings` 输出含 `The@`、`Your sets` 这类被元数据截断的片段），patch 后还要逐个修正拼接逻辑，不现实
3. **去重共享**：同一字面量存储被界面、日志、字符串比较逻辑共用，改一处可能改变逻辑判断（如按状态标题比较的代码）
4. **范围**：主程序 + 4 个扩展共 5 个二进制要逐个处理，每版上游更新全部重做，且无法在无真机情况下验证不崩

**判定：不可行**，最多给个别短串打补丁，不构成路线。（与此前 Seal 项目二进制 patch 的经验一致：只适合极少量、等长可控的点位。）

### 路线 B：源码原地翻译 + 云端 Mac 只编译 App 本体（推荐，含前置探针）

做法：把源码字面量原地改成中文（不引入本地化机制，改的是文本本身）→ 云端 Mac（GitHub Actions）用 XcodeGen 生成工程、xcodebuild 编 App + 4 扩展 → `tools/package_app.sh` 打成未签名 IPA。逐项核查结果：

**B-1 工程侧：干净，没有远程依赖**

- `app/project.yml`（295 行）：5 个 target；唯一的包依赖是本地 `Packages/LauncherCore`（path 引用），**无任何远程 SPM 依赖**
- 框架依赖 `app/Vendor/StikJIT.xcframework` 不在仓库（`.gitignore: app/Vendor/`），但 `tools/prepare_stikjit.py` 会从 StikJIT 官方 Release 下载并按固定 SHA-256（`444b8d43…7e85`）校验，CI 里可自动完成；也可从上游 IPA 的 `Frameworks/` 里取同一框架
- 配置 `app/Config/Local.xcconfig` 照 example 生成即可；**为与上游正式包行为一致，应把 1.5 节从 IPA 读到的值填回去**（Bundle ID `site.portholehq.app`、Hub 地址/AppID、Release 公钥、引擎 ID `3af3467-r1`），否则汉化版会失去官方兼容列表/自更新通道且兼容徽章清零

**B-2 运行时资源（Resources）：可从上游 IPA 完整复用 ✔**

- `tools/stage_runtime.sh` 的产物 `app/RuntimeStage/Resources/` 与 `app/project.yml` 的资源清单，就是 IPA 里现成的目录：`nls / aarch64-windows / arm64ec-windows / i386-windows / d3d12 / gl / compat / legal / licenses / prefix-template.tar.gz / cacert.pem / madeira-jit.js`——逐项与 1.4 的 IPA 清单对上，**从 IPA 提取即字节级等于上游 1.2.1 出厂状态**（含上游重编的 90 个 DLL）
- 反观 Madeira 快照：**资源并不完整**。经 GitHub API 核查 `willfaust/Madeira@5fda6a0`（Porthole 的 `.gitmodules` 锁定提交，见 `docs/SOURCE.md`）的 `app/Madeira/` 目录与 Madeira 仓库 `.gitignore` 原文：
  - `i386-windows/*` 明确「不提交，由 build/wine-i386/build.sh 生成」（快照里只有 .gitkeep）
  - `gl/*.dylib` 是 mesa-ios/moltenvk 构建产物，不提交
  - `arm64ec-windows/dockhost.exe` 等个别文件是构建产物
  - 结论：**资源必须走 IPA 提取，不能指望快照**（这也解释了 stage_runtime 为何把 stage 放在作者的外置硬盘上）

**B-3 静态库（RuntimeStage/lib）：路线的唯一硬关卡 ⚠**

- `app/project.yml` 的 `OTHER_LDFLAGS` 要求链接 12 个静态库：`dxmt_combined, gmp, lzma, gnutls, hogweed, nettle, ntdll_unix, win32u_unix, wineserver, avcodec, avformat, avutil, swresample`（节选，另有系统库）
- Madeira 快照 `app/Madeira/` 里**实际跟踪的只有 4 个**：`libgmp.a`(0.91 MB)、`libgnutls.a`(4.4 MB)、`libhogweed.a`、`libnettle.a`（GitHub API 目录核查）；外加 `app/libdxmt_unix.a`（Porthole 并不链接它，链接的是 `_combined` 版）
- 其余全部是构建产物，证据是 Madeira 仓库 `.gitignore` 原文逐条列明：`app/Madeira/libntdll_unix.a`、`libwineserver.a`、`libdxmt_combined.a`、`libwin32u_unix.a`、`libavformat/libavcodec/libswresample/libavutil.a` 均属「Compiled libraries (rebuilt from build scripts)」
- 这些库**无法从 IPA 回收**：静态库已链进 69.5 MB 主二进制，不可拆回
- Porthole 的 `docs/REBUILT_BINARIES.sha256`（93 条）还表明：其中 `libdxmt_combined.a`、`libntdll_unix.a`、`libwin32u_unix.a` 是被 Porthole 打过补丁（patches 0172–0176）的版本——即便用快照旁路也对不上，必须按「锁定提交 + 五个补丁」构建
- 要补建的库与脚本（都在 Madeira `build/` 与 Porthole `tools/` 里，有据可查）：`build/ntdll-unix`、`build/win32u-unix`、`build/wineserver`（+ Porthole `tools/build_wineserver_base.sh`）、`build/dxmt-ios`（+ `tools/build_dxmt_shader_headers.sh`、`apply_dxmt_patch.sh`、`apply_madeira_patch.sh`）、`build/ffmpeg`；`liblzma.a` 的来源脚本要在探针时确认。子模块需拉 Wine/FEX/DXMT 锁定提交并打 0172–0176 补丁
- **量级判断**：这只是引擎的「库」部分（Wine unix 侧 + wineserver + DXMT + FFmpeg 的交叉编译），不含 DLL farm、i386 farm、Mesa 等最重的部分（那些已由 IPA 提取绕开）；但上游 `docs/SOURCE.md` 自承「干净机器从零重建从未做过」，脚本里有作者本机路径（`tools/local.env` 不入库），所以**必须先做探针（spike）：在 GitHub Actions macOS 上只跑「补建缺失静态库 + stage + 编 App」一遍，通了路线 B 才算成立**。风险点：脚本对本机环境的隐含假设、Xcode 版本（文档要求 Xcode 27）、单个 Actions 作业时长上限

**B-4 打包：现成**

- `tools/package_app.sh`（17 行）：把 .app 拷进 Payload、删签名残留与 VC 运行时 DLL、跑 `tools/scrub_paths.py` 去除构建者路径、zip 成 IPA——CI 里原样可用；上游 IPA 本身就是未签名的，流程与 Grace 的自签交付方式吻合

**B-5 在路线 B 下「所有报错提示都汉化」能否达成：能，且方式彻底**

- 因为文案没有任何间接层：把源码里的字面量逐条换成中文，编译产物里就是中文——错误（errorDescription 74+ 条、throw 369 处、错误结构体 message）、提示与状态串、自定义组件标题、拼接/三元文案，**全部同等可达**，这是路线 A/C 做不到的
- Info.plist 权限文案在 `project.yml`/plist 里直接改；扩展显示名同理
- 核验按既定标准执行：以第二部分的全量盘点为清单逐条销账；构建后从成品 IPA 的 5 个二进制提取字符串与清单比对（本次实测 `strings` 对主二进制可提出句子式文案，可作自动核验的基础）
- 天然除外（与标准一致或非本 App 文案）：日志/诊断串（LogStore 等）、引擎运行时内部消息与游戏内 Windows 程序自身文本、Hub 服务器下发的内容、StikJIT 第三方框架内部的 Rust 错误串（其配对流程若弹错，文本来自框架二进制，属残余风险，要单独评估）

### 其它考虑过并排除的变体

- **B 变体「资源+库都从 Madeira 快照 stage」**：被 B-2/B-3 证据否定——快照缺 i386 farm、gl 动态库与 8+ 个静态库
- **从 Madeira 官方 IPA 取库**：willfaust/Madeira 的 Release 只有它自己的整包 IPA（`Madeira-1.2.1-688.ipa`，GitHub API 核查），静态库同样链在二进制里，取不出
- **A+B 混搭先行**：先发 A 的语言包版让 Grace 试装不解决问题（九成英文含全部报错），且容易造成「已汉化」的误判；不建议。若 Grace 想先看效果，可低成本出一个 A 版试装包，但必须明示其覆盖率

---

## 四、推荐路线

**路线 B：源码原地全量翻译 + 运行时资源从上游 IPA 提取 + 云端 Mac 补建缺失静态库后只编译 App 本体 + package_app.sh 打包。**

执行顺序建议：

1. **探针（先行，决定路线生死）**：GitHub Actions macOS 上按锁定提交拉 Madeira 及 Wine/FEX/DXMT 子模块、打 0172–0176 补丁，只构建 B-3 列出的缺失静态库；再 stage（lib 用自建+快照 4 库，Resources 用 IPA 提取）、xcodegen、xcodebuild、package_app，产出一个未翻译的英文重建 IPA，与上游 IPA 做结构 diff（文件清单、扩展、引擎 ID、大小量级）。探针不过，不进入翻译（避免 5,000 条翻译白做）
2. 探针通过后，按第二部分盘点逐条翻译（app/Sources 与 LauncherCore 优先，Runtime 里的用户可见串单独审定），构建、开包核验、按清单销账
3. 交付仍走既定标准：未签名 IPA 发布到为本项目新建的仓库发行版（标签加 `-zh-Hans` 后缀）、README 全译、发行说明照上游 1.2.1 日志译中文并注明 AI 翻译（建仓/发布不在本次调查范围内）

---

## 五、未决事项与风险清单

1. **静态库补建探针未做**——路线 B 成立的前提；失败模式未知（脚本本机假设/Xcode 27/Actions 时长），需预留多次迭代
2. `liblzma.a` 的确切来源（快照与 .gitignore 均未直接点名）——探针时确认
3. GitHub 托管 macOS 运行器的 Xcode 版本是否满足文档的 Xcode 27 要求——探针时确认（本机无法预验）
4. 引擎补丁 0172–0176 的具体应用顺序以 `docs/SOURCE.md` 为准，探针时按其步骤执行并记录偏差
5. StikJIT 框架内部文案（配对/JIT 流程的框架级报错）不在源码翻译范围，是否需要处理待探针后单独评估
6. 本报告的分类数字为第一轮启发式盘点（方法与脚本在 `work/`），翻译阶段须逐条人工审定成最终清单；残余类 (b3/b4) 的可见比例是抽样估计（各抽 30 条），不是精确值

## 附录：证据来源索引

- 上游仓库：`~/workspace/porthole-zh/upstream`（HEAD 0786a24 = v1.2.1）；关键文件 `app/project.yml`、`tools/stage_runtime.sh`、`tools/package_app.sh`、`tools/prepare_stikjit.py`、`docs/SOURCE.md`、`docs/REBUILD.md`、`docs/REBUILT_BINARIES.sha256`、`app/Config/Local.xcconfig.example`
- IPA：`~/workspace/porthole-zh/downloads/Porthole-1.2.1-688.ipa`（SHA-256 见 1.1）；inspect 输出 `~/workspace/porthole-zh/work/inspect.json`；解包目录 `~/workspace/porthole-zh/work/unpacked/`
- 盘点：`~/workspace/porthole-zh/work/inventory.py` / `inventory.json`
- GitHub API 核查：`repos/tylerkaska112/Porthole/releases/tags/v1.2.1`（资产与大小）；`repos/willfaust/Madeira/git/trees/5fda6a0…`（快照目录结构与 lib 清单）；`raw.githubusercontent.com/willfaust/Madeira/5fda6a0…/.gitignore`（构建产物清单）；`repos/willfaust/Madeira/releases`（只有整包 IPA）；Release 页面 v1.2.1 发行说明（IPA 哈希）
