# Porthole（简体中文版）

本仓库是 [tylerkaska112/Porthole](https://github.com/tylerkaska112/Porthole)（版本 v1.2.1）的**非官方简体中文汉化版**，与上游作者无关。相对上游的改动只有一项：把应用的全部用户可见文案翻译为简体中文——包括界面文字，以及一般汉化容易漏掉的**报错、提示、状态与进度文案**（运行日志与诊断内容保留英文）；功能与行为与上游 v1.2.1 一致。本仓库的全部翻译（应用文案、本 README 与发行说明）均由 **AI 完成**。

发行版提供未签名 IPA，需自行签名安装。

以下为上游 README 的全文中文翻译（[上游原文](https://github.com/tylerkaska112/Porthole)）：

---

Porthole 能在 iPhone 和 iPad 上运行 Windows PC 游戏。它是 [Madeira](https://github.com/willfaust/Madeira) 运行时（Wine、FEX 与 DXMT）的外壳应用，带有游戏库、Steam、Epic Games、GOG、itch.io、Amazon Games 与 EA app 的登录和下载、JIT 设置、设备端更新，以及可选的社区兼容性列表（[portholehq.site](https://portholehq.site)）。

**状态：早期阶段。** 它由一个人制作、在少数几台设备上测试。很多游戏跑不起来，有些能跑的也需要调整。花一晚上折腾之前，先读一读[预期情况](#预期情况)。

> **非官方。** Porthole 与 Valve、Steam、Microsoft、Apple、Epic、GOG 或任何游戏发行商均无关联，也未获其认可。它不绕过任何许可校验或复制保护：Steam 游戏通过 Valve 自己的 Steam 客户端文件启动，校验你的许可的方式与在 PC 上完全一样；Porthole 本身不包含任何游戏。游戏、商店与公司名称归其各自所有者所有。

## 你需要什么

- 一台运行 **iOS 18 或更高版本**（arm64）的 iPhone 或 iPad。它在 iOS 26 和 27 上开发与测试；iOS 18 到 25 应该也能工作，但未经测试。内存越大越好：游戏需要的内存超过设备所有时无法运行。
- 一种**自己签名并安装应用**的方法。Porthole 不在 App Store 上架，也不可能上架，因为它用私有 iOS 接口启动其辅助程序。可选路线，从优到次：
  - **付费 Apple Developer 账号**，或**第三方证书服务**：两者都能提供 Porthole 要求的全部能力（*Network Extension（数据包隧道）*、*Personal VPN*、*Increased Memory Limit*、*Extended Virtual Addressing* 与 *get-task-allow*）。推荐。
  - **免费 Apple ID** 也可以，能用应用的核心部分（游戏库、商店、下载、游戏），但承载不了其中一些能力：没有 Network Extension（私有链路改用 LocalDevVPN），也没有 Increased Memory Limit（吃内存的游戏更容易内存不足），且签名约一周后过期。较轻量的安装方式见上游文档 [Install](https://github.com/tylerkaska112/Porthole/blob/main/docs/INSTALL.md#fewer-app-ids-optional)。
- 一种为应用开启 **JIT** 的方法（见上游文档 [Install](https://github.com/tylerkaska112/Porthole/blob/main/docs/INSTALL.md)）。Porthole 在备好一次性的“配对文件”后可以自己开启 JIT：iOS 27 或更高版本上设备能自己生成该文件，更早的版本上需要在电脑上生成一次。
- 你拥有的游戏：来自 Steam、Epic Games、GOG、itch.io、Amazon Games 或 EA app（在应用内登录），或者你从“文件”应用拷入的游戏文件夹与安装程序。

分步说明：**[上游 docs/INSTALL.md](https://github.com/tylerkaska112/Porthole/blob/main/docs/INSTALL.md)**。

## Porthole 能做什么

- **游戏库：** 你的游戏，带封面图、游玩时长、每款游戏单独的设置，以及可选的屏幕控制器布局。
- **商店：** 登录 Steam（密码加 Steam Guard，或扫二维码）、Epic Games、GOG、Amazon Games 或 EA（在商店自己的页面上登录，Porthole 永远看不到你的密码），或 itch.io（用你在那边生成的个人 API 密钥），查看你拥有的游戏，并直接下载到设备上。下载会适应你的网络连接，中断后可以续传。一个统一的**「下载」页面**显示每个商店正在下载的内容，带暂停、继续与“立即下载”；它的圆形按钮常驻在“商店”页签的右下角。
- **控制器：** PlayStation、Xbox 以及 iOS 支持的其他控制器开箱即用。使用控制器时屏幕控件会自动隐藏，控制器可以当作键盘和鼠标用，每款游戏的控制器按键都可以重新映射。
- **键盘与鼠标：** 蓝牙或 USB 键盘、鼠标或触控板（iPad）在游戏中和在 PC 上一样工作：带全部修饰键的每个按键、五个鼠标按键、滚轮、菜单中游戏自己的光标，以及用于环视的锁定指针。Porthole 的菜单用你选定的按键打开（默认为 F10）。见上游文档 `docs/KEYBOARD_MOUSE.md`。
- **Windows 组件：** 许多游戏需要 Microsoft 的 Visual C++ 运行时。Porthole 从 Microsoft 官方下载其安装程序，按固定的指纹校验，然后自己解包文件。应用内不包含 Microsoft 的任何东西。
- **JIT：** iOS 的这项特性决定一切的速度。内置方法、StikDebug 或其他工具：在设置指南里由你选。
- **更新：** Porthole 可以在设备上自我更新（下载、用你自己的证书签名、安装），更新服务器地址在构建应用时设定；你也可以手动安装新 IPA。带维护者发行密钥的构建只会安装用匹配私钥签名的更新。本源码中没有服务器地址；带服务器地址的构建见“隐私”一节。
- **兼容性报告与共享按键绑定（可选）：** 游玩后你可以报告一款游戏的运行情况、查看它在与你相同机型的其他人那里的运行情况，并为一款游戏分享或下载按键绑定集。这些功能需要同一个构建时设定的服务器地址。

## 预期情况

- 有些游戏运行得很好：例如 Factorio 在 iPad Pro（M4）上以约 57 fps 运行。
- 有些则无望：比设备内存还大的游戏、带内核级反作弊的游戏、非常大的可执行文件（运行时会把程序复制到一块固定内存区域，因此约 450 MB 及以上的程序无法加载），以及一些需要尚未实现的 Windows 特性的游戏。一些 Unity 游戏只有通过 Steam 启动才能工作。
- 首次运行需要几分钟的设置；游戏库与设置是你的，留在设备上。
- [portholehq.site/compat.html](https://portholehq.site/compat.html) 上的社区列表展示了其他人报告的情况。

## 隐私

你设置的一切都留在设备上。商店登录信息（令牌，绝不是密码）保存在 iOS 钥匙串中，仅限本设备，且只发送给商店本身。Porthole 联网是为了下载你要求的东西（Microsoft 的组件、Valve 的客户端文件、你从已登录商店获得的游戏、更新）。带有社区服务器地址的构建（一个构建设置；本源码中没有）还会向该服务器询问最新更新、你的游戏适用哪些兼容性徽章、存在哪些共享按键绑定，并且只在你主动选择时发送内容：兼容性报告（一个每次安装随机生成的密钥、游戏、你的设备型号和你的回答），或你分享的按键绑定集（同一个随机密钥、游戏和绑定集本身）。绝不发送你的姓名、账号或任何设备标识。详情：[portholehq.site/privacy.html](https://portholehq.site/privacy.html)。你选择发送的问题报告会包含应用的日志，发送前会先清除其中的账号名、电子邮件地址和公网 IP 地址；发送前你可以先阅读它。没有数据分析，也没有 Porthole 账号。

## 从源码构建

该应用在 Mac 上用 Xcode 与 [XcodeGen](https://github.com/yonaskolb/XcodeGen) 构建。Madeira 运行时是一个 git 子模块（`vendor/Madeira`，锁定在构建所用的提交上），其原生库由 `tools/` 与 Madeira 的 `build/` 文件夹中的脚本构建。确切版本、应用的补丁、构建顺序，以及替换静态链接库的步骤，都在上游文档 **[docs/SOURCE.md](https://github.com/tylerkaska112/Porthole/blob/main/docs/SOURCE.md)** 中。该流程尚未在一台干净的机器上从零完整重复过；如果哪一步不对，那是文档的 bug。

```bash
cd Packages/LauncherCore && swift test        # 签名器、更新目录、保管库、传输（不需要设备）
app/Tests/Steam/run.sh                        # 用一个模拟 Steam 服务器的替身测试 Steam 客户端（STEAM_LIVE=1 时也用真实服务器）
cp app/Config/Local.xcconfig.example app/Config/Local.xcconfig     # 你的 bundle id，以及可选的你自己的服务器
```

`app/Config/Local.xcconfig` 与 `tools/local.env` 保存你自己的身份与机器路径，永远不会被提交。

## 由 AI 协助构建

Porthole 是在 AI 的帮助下构建的。代码、文档、网站和美术作品的很大一部分由 AI 编程助手（Anthropic 的 Claude）编写，它与维护者协作，由维护者主导项目、审查改动并在真实设备上测试。因此代码中包含 AI 编写的代码，并且和任何软件一样，可能包含错误。

## 许可证与致谢

Porthole 自身的代码是自由软件，采用 **GNU 通用公共许可证第 3 版或（由你选择）任何更高版本**（[LICENSE](https://github.com/tylerkaska112/Porthole/blob/main/LICENSE)），并附带对 Apple Metal Shader Converter 的额外许可（[LICENSE-EXCEPTION.md](https://github.com/tylerkaska112/Porthole/blob/main/LICENSE-EXCEPTION.md)）。取自其他项目的部分保留其各自的许可证；[CREDITS.md](https://github.com/tylerkaska112/Porthole/blob/main/CREDITS.md) 说明了各部分的作者，[docs/COMPLIANCE.md](https://github.com/tylerkaska112/Porthole/blob/main/docs/COMPLIANCE.md) 列出了每部分的要求，应用内在“设置 ▸ 关于”与致谢 ▸ 许可证中展示这些许可证。不提供任何担保。

Porthole 站在它所基于的项目的工作之上：Madeira（Wine、FEX-Emu、DXMT 与 Madeira Dock）、StikDebug 与 idevice，以及致谢中列出的其他项目。

---

*本汉化版说明：翻译由 AI 完成。本仓库为非官方汉化修改版，应用功能问题请以英文原版对照；上游项目地址：https://github.com/tylerkaska112/Porthole*
