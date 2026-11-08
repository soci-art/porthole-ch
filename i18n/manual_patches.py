#!/usr/bin/env python3
"""Manual patches for misclassified visible strings (suspect review MUST items
+ Telemetry overlay siblings). Applies en->zh per (file, line) on zh-src."""
import json, sys, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/workspace/porthole-zh/zh-src')

P = [
 # EntitlementChecker long message fragments (join with already-translated L78)
 ("app/Runtime/EntitlementChecker.swift", 79,
  "(a distribution or enterprise certificate), so no debugger can attach to it. Install Madeira with a development ",
  "（属于分发或企业证书），因此没有调试器能附加到它。请使用开发"),
 ("app/Runtime/EntitlementChecker.swift", 80,
  "certificate (for example SideStore, AltStore or Xcode), then enable JIT again.",
  "证书（例如 SideStore、AltStore 或 Xcode）安装 Madeira，然后再次启用 JIT。"),
 # StikJITHelper noDebuggerMessage fragments (join with translated L120)
 ("app/Runtime/StikJITHelper.swift", 121,
  "be set up. This happens when JIT is enabled from StikDebug's own app list. Tap Enable JIT: StikDebug then ",
  "完成设置。出现这种情况，是因为 JIT 是从 StikDebug 自家的应用列表中启用的。点按 Enable JIT：StikDebug 随后会 "),
 ("app/Runtime/StikJITHelper.swift", 122,
  "reopens Madeira with Madeira's script, ready to play.",
  "用 Madeira 的脚本重新打开 Madeira，即可开始游戏。"),
 # Amazon
 ("app/Sources/Amazon/AmazonAuth.swift", 60, "Amazon account", "Amazon 账户"),
 ("app/Sources/Amazon/AmazonAuth.swift", 63, "Amazon account", "Amazon 账户"),
 ("app/Sources/Amazon/AmazonAuth.swift", 121, "Amazon account", "Amazon 账户"),
 ("app/Sources/Amazon/AmazonSignInView.swift", 29,
  "That address has no sign-in code in it.", "这个地址里没有登录代码。"),
 # CompatLog summary + labels (shown in report form)
 ("app/Sources/Compat/CompatLog.swift", 21,
  "\\(source): \\(size(textBytes)) of text, about \\(size(packed.count)) sent",
  "\\(source)：\\(size(textBytes)) 的文本，发送约 \\(size(packed.count))"),
 ("app/Sources/Compat/CompatLog.swift", 35, "this run", "本次运行"),
 ("app/Sources/Compat/CompatLog.swift", 35, "the run before", "上一次运行"),
 ("app/Sources/Compat/CompatLog.swift", 37,
  "the game's log (\\(newest.lastPathComponent))", "游戏日志（\\(newest.lastPathComponent)）"),
 # CompatViews pill
 ("app/Sources/Compat/CompatViews.swift", 51, "NOT YET TESTED", "尚未测试"),
 ("app/Sources/Compat/CompatViews.swift", 51, "Not yet tested", "尚未测试"),
 # BindSets fallback name
 ("app/Sources/Core/BindSets.swift", 188, "Imported set", "导入的绑定集"),
 # SteamBigPicture
 ("app/Sources/Core/SteamBigPicture.swift", 44, "Steam Big Picture", "Steam 大屏模式"),
 ("app/Sources/Core/SteamBigPicture.swift", 53,
  "Big Picture starts from the Steam client. Download it first (Settings \\u{203A} Stores \\u{203A} Steam \\u{203A} Steam client).",
  "大屏模式从 Steam 客户端启动。请先下载它（设置 \\u{203A} 商店 \\u{203A} Steam \\u{203A} Steam 客户端）。"),
 ("app/Sources/Core/SteamBigPicture.swift", 61,
  "Could not prepare Big Picture's folder: \\(error.localizedDescription)",
  "无法准备大屏模式的文件夹：\\(error.localizedDescription)"),
 ("app/Sources/Core/SteamBigPicture.swift", 84,
  "Could not write Big Picture's start file: \\(error.localizedDescription)",
  "无法写入大屏模式的启动文件：\\(error.localizedDescription)"),
 # Telemetry overlay (compact + full fragments; thermal/mode values stay as data)
 ("app/Sources/Core/Telemetry.swift", 31,
  "%.0f fps | %.0f%% cpu | %.1f GB | %@", "%.0f fps | CPU %.0f%% | %.1f GB | %@"),
 ("app/Sources/Core/Telemetry.swift", 36,
  "FPS %.0f (low %.0f)   frame %.1f ms", "FPS %.0f（最低 %.0f）   帧时间 %.1f ms"),
 ("app/Sources/Core/Telemetry.swift", 37,
  "CPU %.0f%% on %d threads", "CPU %.0f%%，%d 个线程"),
 ("app/Sources/Core/Telemetry.swift", 38,
  "App mem %.2f GB   free %.2f GB   GPU %.2f GB", "应用内存 %.2f GB   可用 %.2f GB   GPU %.2f GB"),
 ("app/Sources/Core/Telemetry.swift", 39, "Heat: \\(thermal)", "温度：\\(thermal)"),
 ("app/Sources/Core/Telemetry.swift", 41, "   Battery %.0f%%", "   电量 %.0f%%"),
 ("app/Sources/Core/Telemetry.swift", 42, " (%@%.0f%%/h)", " (%@%.0f%%/小时)"),
 ("app/Sources/Core/Telemetry.swift", 44, "   Low Power Mode", "   低电量模式"),
 ("app/Sources/Core/Telemetry.swift", 47, "GPU busy %.0f%%", "GPU 占用 %.0f%%"),
 ("app/Sources/Core/Telemetry.swift", 47, " (%.1f ms a frame)", "（每帧 %.1f ms）"),
 ("app/Sources/Core/Telemetry.swift", 47, "   busiest thread %.0f%%", "   最忙线程 %.0f%%"),
 ("app/Sources/Core/Telemetry.swift", 48, "Busiest thread %.0f%%", "最忙线程 %.0f%%"),
 ("app/Sources/Core/Telemetry.swift", 51,
  "Swap file %.2f of %.2f GB (%.0f%%)", "交换文件 %.2f / %.2f GB（%.0f%%）"),
 ("app/Sources/Core/Telemetry.swift", 52, "  FULL SOON", "  即将占满"),
 ("app/Sources/Core/Telemetry.swift", 63, "Compressed %.2f GB", "已压缩 %.2f GB"),
 ("app/Sources/Core/Telemetry.swift", 64, "%@file-backed %.2f GB", "%@文件后备 %.2f GB"),
 ("app/Sources/Core/Telemetry.swift", 65, "%@paging in %.1f MB/s", "%@调入 %.1f MB/s"),
 ("app/Sources/Core/Telemetry.swift", 68, "Mode: \\(mode)", "模式：\\(mode)"),
 ("app/Sources/Core/Telemetry.swift", 240,
  "Swap is almost full. If the game stutters or closes, raise Swap in this game's settings.",
  "交换空间即将占满。如果游戏卡顿或退出，请在本游戏的设置中调大交换空间。"),
 ("app/Sources/Core/Telemetry.swift", 242,
  "Memory is almost full. Close other apps, or raise Swap in this game's settings.",
  "内存即将占满。请关闭其它 App，或在本游戏的设置中调大交换空间。"),
 ("app/Sources/Core/Telemetry.swift", 243,
  "Memory is almost full. Close other apps. If this keeps happening, turn on Swap in this game's settings.",
  "内存即将占满。请关闭其它 App。如果这种情况反复出现，请在本游戏的设置中开启交换空间。"),
 # VPNGuard confirm button
 ("app/Sources/Core/VPNGuard.swift", 219, "Pause it", "暂停"),
 # EA / GOG account fallbacks
 ("app/Sources/EA/EALibrary.swift", 56, "EA account", "EA 账户"),
 ("app/Sources/Gog/GogAuth.swift", 45, "GOG account", "GOG 账户"),
 ("app/Sources/Gog/GogAuth.swift", 68, "GOG account", "GOG 账户"),
 ("app/Sources/Gog/GogAuth.swift", 83, "GOG account", "GOG 账户"),
 # RemotePairingHost traces (shown in pairing view)
 ("app/Sources/Pairing/RemotePairingHost.swift", 73,
  "connection from \\(conn.endpoint)", "来自 \\(conn.endpoint) 的连接"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 78, "connection ready", "连接已就绪"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 80, "handshake done", "握手完成"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 99,
  "conversation failed: \\(why)", "会话失败：\\(why)"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 143,
  "listening on port \\(port)", "正在监听端口 \\(port)"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 146,
  "listener failed: \\(error)", "监听器失败：\\(error)"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 150,
  "listener waiting: \\(error)", "监听器等待中：\\(error)"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 321,
  "pair-setup started; sending salt and public value", "配对设置已开始；正在发送盐值和公开值"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 331,
  "client proof received (A \\(clientPublic.count) bytes)", "已收到客户端证明（A 共 \\(clientPublic.count) 字节）"),
 ("app/Sources/Pairing/RemotePairingHost.swift", 354, "this iPhone", "这台 iPhone"),
 # Live Activity buttons
 ("app/Sources/Shared/DownloadActivityAttributes.swift", 41, "Pause downloads", "暂停下载"),
 ("app/Sources/Shared/DownloadActivityAttributes.swift", 53, "Resume downloads", "继续下载"),
 ("app/Sources/Shared/DownloadActivityAttributes.swift", 65, "Cancel download", "取消下载"),
 # SteamAuth error detail (shown on sign-in screen)
 ("app/Sources/Steam/SteamAuth.swift", 121, "The request could not be built.", "无法构建请求。"),
 # Library screens
 ("app/Sources/UI/EpicLibraryScreens.swift", 529, "Delete downloaded files", "删除已下载的文件"),
 ("app/Sources/UI/SteamPage.swift", 302, "Delete downloaded files", "删除已下载的文件"),
 ("app/Sources/UI/SteamPage.swift", 319, "See reports", "查看报告"),
 ("app/Sources/UI/SteamPage.swift", 319,
  "What other players say about running this game here, by device, with the settings that worked.",
  "其他玩家对在这里运行这款游戏的评价，按设备分类，并附上有效的设置。"),
 # GuideCenter
 ("app/Sources/UI/Guide/GuideCenter.swift", 67,
  "Reports are what other people found when they played a game. Open a game to see which settings people use when it works great, and how it does on each device.",
  "报告是其他玩家玩游戏时的发现。打开一款游戏，可以查看它运行良好时大家使用的设置，以及它在每台设备上的表现。"),
 ("app/Sources/UI/Guide/GuideCenter.swift", 69,
  "After you play, a report helps the next person. You can write one from a game's page or from here.",
  "你玩过之后，一份报告能帮到下一个人。你可以在游戏页面或这里撰写报告。"),
 # ReportsLayouts
 ("app/Sources/UI/Reports/ReportsLayouts.swift", 157, "No reports from your device yet.", "你的设备还没有报告。"),
 ("app/Sources/UI/Reports/ReportsLayouts.swift", 157, "No reports on this version yet.", "这个版本还没有报告。"),
 ("app/Sources/UI/Reports/ReportsLayouts.swift", 157, "No reports like that.", "没有符合的报告。"),
 ("app/Sources/UI/Reports/ReportsLayouts.swift", 164,
  "Sent from older versions of the game engine. They are kept for reference and do not count toward the verdict.",
  "由较早版本的游戏引擎发送。保留它们仅供参考，不计入判定结果。"),
 # SetupGuide store rows
 ("app/Sources/UI/SetupGuideView.swift", 365,
  "Download the games you own on Steam straight to this device. Your password is encrypted before it leaves the device and is never saved.",
  "将你在 Steam 上拥有的游戏直接下载到这台设备。你的密码在离开设备前会被加密，且永远不会保存。"),
 ("app/Sources/UI/SetupGuideView.swift", 366,
  "Download the games you own on Epic Games straight to this device. You sign in on Epic's own page; Porthole never sees your password.",
  "将你在 Epic Games 上拥有的游戏直接下载到这台设备。你在 Epic 自家的页面上登录；Porthole 永远不会看到你的密码。"),
 ("app/Sources/UI/SetupGuideView.swift", 367,
  "Download the games you own on GOG straight to this device. You sign in on GOG's own page; Porthole never sees your password.",
  "将你在 GOG 上拥有的游戏直接下载到这台设备。你在 GOG 自家的页面上登录；Porthole 永远不会看到你的密码。"),
 ("app/Sources/UI/SetupGuideView.swift", 368,
  "Download the games you bought, claimed or collected on itch.io. You make a personal API key on itch.io and paste it here; it stays in this device's Keychain.",
  "下载你在 itch.io 上购买、领取或收藏的游戏。你在 itch.io 上创建一个个人 API 密钥并粘贴到这里；它会保存在这台设备的钥匙串中。"),
 ("app/Sources/UI/SetupGuideView.swift", 369,
  "Download the games you bought on Amazon or claimed with Prime Gaming. You sign in on Amazon's own page; Porthole never sees your password.",
  "下载你在 Amazon 上购买或通过 Prime Gaming 领取的游戏。你在 Amazon 自家的页面上登录；Porthole 永远不会看到你的密码。"),
 ("app/Sources/UI/SetupGuideView.swift", 370,
  "Download the PC games on your EA account. You sign in on EA's own page; Porthole never sees your password. Games with EA's kernel anti-cheat cannot run.",
  "下载你 EA 账户中的 PC 游戏。你在 EA 自家的页面上登录；Porthole 永远不会看到你的密码。带 EA 内核级反作弊的游戏无法运行。"),
 ("app/Sources/UI/SetupGuideView.swift", 374,
  "Pick a game's folder in Files and it is copied into Porthole, or run a Windows installer.",
  "在「文件」中选择游戏的文件夹，它会被复制到 Porthole 中；也可以运行 Windows 安装程序。"),
 # Round 2: 'windows-or-engine-data' group sweep — visible info/notice strings
 ("app/Sources/UI/Game/GameEngineSection.swift", 35,
  "Which graphics card this game is told it has, everywhere it can ask: Direct3D 9, 10, 11 and 12, Windows' own adapter list and NVIDIA's NVAPI. For a game that refuses to start or picks poor settings because it does not know the card, or that needs an NVIDIA one. This changes only what the game reads; the device draws the same.",
  "游戏在所有能询问的地方都会被告知它拥有的显卡：Direct3D 9、10、11 和 12、Windows 自带的适配器列表以及 NVIDIA 的 NVAPI。适用于因不认识显卡而拒绝启动或选用了低画质设置的游戏，或需要 NVIDIA 显卡的游戏。这只改变游戏读到的信息；设备的实际绘制不变。"),
 ("app/Sources/UI/Game/GameEngineSection.swift", 70,
  "The folder the program starts in, as a Windows path such as C:\\\\Games\\\\Foo. Leave empty to start in the program's own folder. A batch file (.bat or .cmd) as the program runs through cmd.exe.",
  "程序启动时所在的文件夹，用 Windows 路径表示，例如 C:\\\\Games\\\\Foo。留空则从程序自己的文件夹启动。若程序是批处理文件（.bat 或 .cmd），会通过 cmd.exe 运行。"),
 ("app/Sources/UI/Game/GamePage.swift", 273,
  "Some Steam games bring installers for things they need (Rockstar's launcher, DirectX, Visual C++). Run at next start runs the ones that have not run yet before the game starts, with Windows' service manager available to them; after that the choice goes back to Skip, so they do not run every time. Skip starts the game without them. Use Run at next start again to retry an installer that failed.",
  "有些 Steam 游戏会自带它们所需组件的安装程序（Rockstar 启动器、DirectX、Visual C++）。「下次启动时运行」会在游戏开始前运行那些尚未运行过的安装程序，并让它们能用上 Windows 的服务管理器；运行之后该选项会回到「跳过」，不会每次都运行。「跳过」会直接启动游戏，不运行它们。某个安装程序失败时，再次使用「下次启动时运行」来重试。"),
 ("app/Sources/UI/Game/GamePage.swift", 279,
  "Forgets that this game's one-time installs ever ran, so the next start runs every one of them again (Rockstar's launcher, Social Club, DirectX, Visual C++). Use it after you deleted what they installed, or when an install stopped half way. It does not delete anything itself.",
  "忘记这款游戏的一次性安装曾经运行过，下次启动时会把它们全部重新运行一遍（Rockstar 启动器、Social Club、DirectX、Visual C++）。在你删除了它们安装的内容之后，或某次安装中途停下时使用。它本身不会删除任何东西。"),
 ("app/Sources/UI/Guide/GuideCenter.swift", 103,
  "If you know a program's path on the Windows drive, such as C:\\\\Games\\\\Foo\\\\foo.exe, use Add by path.",
  "如果你知道程序在 Windows 驱动器上的路径，例如 C:\\\\Games\\\\Foo\\\\foo.exe，请使用「按路径添加」。"),
 ("app/Sources/UI/Settings/SavesPage.swift", 27,
  "Restoring puts the backup's files back and overwrites files with the same names in C:\\\\users. Games' own folders are not part of a backup.",
  "恢复会把备份中的文件放回原处，并覆盖 C:\\\\users 中同名的文件。游戏自己的文件夹不包含在备份中。"),
 ("app/Sources/UI/Settings/SavesPage.swift", 37,
  "Files with the same names in C:\\\\users are overwritten.",
  "C:\\\\users 中同名的文件会被覆盖。"),
 ("app/Sources/UI/Settings/SavesPage.swift", 37, "the backup", "备份"),
 ("app/Sources/UI/AddGameFlow.swift", 74,
  "In Files, tap folders until you are inside the game's folder (the one with its .exe), then tap Open at the top right. Tapping a folder only goes into it; Open chooses the folder you are in. It is copied into the app, so it needs that much free space.",
  "在「文件」中逐层点开文件夹，直到进入游戏的文件夹（里面有它的 .exe），然后点右上角的「打开」。点文件夹只是进入它；「打开」选择的才是你当前所在的文件夹。文件夹会被复制到 App 中，因此需要同样大小的可用空间。"),
 ("app/Sources/UI/AddGameFlow.swift", 158,
  "The folder was copied, but there is no program (.exe) inside. You can add one by path.",
  "文件夹已复制，但里面没有程序（.exe）。你可以通过路径添加一个。"),
 ("app/Sources/Core/EngineOptions.swift", 132,
  "For games that expect the Agility SDK's file layout and look for d3d12core.dll. Off by default because it changes how every Direct3D 12 game starts.",
  "适用于期望 Agility SDK 文件布局并会查找 d3d12core.dll 的游戏。默认关闭，因为它会改变所有 Direct3D 12 游戏的启动方式。"),
 ("app/Sources/Core/SessionController.swift", 300,
  "File not found: \\(game.exe). Remove this entry and add the game again with +.",
  "找不到文件：\\(game.exe)。请删除此条目，再用 + 重新添加这款游戏。"),
 ("app/Activity/DownloadLiveActivity.swift", 51, "Done", "完成"),
 ("app/Activity/DownloadLiveActivity.swift", 67,
  " \\u{00B7} +\\(state.waiting) waiting", " \\u{00B7} +\\(state.waiting) 个等待中"),
 # Round 3: PerfOverlay metric/corner/row labels (display-only; rawValues stay)
 ("app/Sources/UI/InGame/PerfOverlay.swift", 14, "1% low", "1% 低帧"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 15, "Frame time", "帧时间"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 17, "Busiest thread", "最忙线程"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 18, "GPU busy", "GPU 占用"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 19, "GPU frame", "GPU 帧时间"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 20, "Memory", "内存"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 21, "Free memory", "可用内存"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 22, "GPU memory", "GPU 内存"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 23, "Heat", "温度"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 24, "Battery", "电量"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 25, "Power mode", "电源模式"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 26, "Swap file", "交换文件"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 56, "Top left", "左上角"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 57, "Top right", "右上角"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 58, "Bottom left", "左下角"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 59, "Bottom right", "右下角"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 177, "Low", "低帧"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 179, "Frame", "帧"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 183, "Top thread", "最忙线程"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 183, "Top thread", "最忙线程"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 187, "GPU frame", "GPU 帧"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 189, "Mem", "内存"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 191, "Free", "可用"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 193, "GPU mem", "GPU 内存"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 195, "Heat", "温度"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 200, "%.0f/h", "%.0f/小时"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 201, "Battery", "电量"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 203, "Battery", "电量"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 207, "Mode", "模式"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 212, "Swap", "交换"),
 ("app/Sources/UI/InGame/PerfOverlay.swift", 214, "Swap", "交换"),
 # EngineOptions choice labels missed as choice-value-data
 ("app/Sources/Core/EngineOptions.swift", 101, "Default (automatic)", "默认（自动）"),
 ("app/Sources/Core/EngineOptions.swift", 147, "Default (iOS's own)", "默认（iOS 自带）"),
]

fails = []
applied = 0
byfile = {}
for path, ln, en, zh in P:
    byfile.setdefault(path, []).append((ln, en, zh))
for path, items in byfile.items():
    full = os.path.join(ROOT, path)
    lines = open(full, encoding='utf-8').read().split('\n')
    for ln, en, zh in items:
        line = lines[ln - 1]
        q = '"' + en + '"'
        if q in line:
            lines[ln - 1] = line.replace(q, '"' + zh + '"', 1); applied += 1; continue
        if en in line:
            lines[ln - 1] = line.replace(en, zh, 1); applied += 1; continue
        fails.append((path, ln, en[:60]))
    open(full, 'w', encoding='utf-8').write('\n'.join(lines))
print(f"applied {applied}/{len(P)}")
for f in fails: print("FAIL:", f)

# --- Fixups: applied after the patches above, on the post-apply tree ---
# (a) revert log-only strings that were translated as units (LogStore/EALog only)
# (b) sentence-join fixes (dangling English suffix, reason token shown in UI)
# (c) switchSummary coherence inside GameRecommendations
FIX = [
 ("app/Runtime/StikJITHelper.swift", None,
  " + [0x%lx,0x%lx) %luMB，作为单个 %luMB 区间；池偏移量",
  " + [0x%lx,0x%lx) %luMB as one %luMB span; pool offsets"),
 ("app/Runtime/StikJITHelper.swift", None,
  " [0x%lx,0x%lx)（%luMB，第三个区域下方的映射）",
  " [0x%lx,0x%lx) (%luMB, the mapping below the third region)"),
 ("app/Runtime/StikJITHelper.swift", None,
  " 以及 [0x%lx,0x%lx)（%luMB，主线程的栈）",
  " and [0x%lx,0x%lx) (%luMB, the main thread's stack)"),
 ("app/Runtime/StikJITHelper.swift", None, " 从不分配出去", " are never handed out"),
 ("app/Sources/UI/SessionView.swift", None,
  "按下 \\(b)，位置 \\(desktopPoint(p))", "press \\(b) at \\(desktopPoint(p))"),
 ("app/Sources/UI/SessionView.swift", None, "松开 \\(b)", "release \\(b)"),
 ("app/Sources/UI/SessionView.swift", None,
  "点击 \\(b)，位置 \\(desktopPoint(p))", "click \\(b) at \\(desktopPoint(p))"),
 ("app/Sources/UI/SessionView.swift", None, "滚轮 \\(delta)", "wheel \\(delta)"),
 ("app/Runtime/VCRedist.swift", None, ' + " only"', ' + ""'),
 ("app/Runtime/SwiftEA/EAAPI.swift", None, '"no signature"', '"无签名"'),
]
# swap-coverage label unification (line-scoped; same mode, five surfaces)
FIX += [
 ("app/Sources/UI/Game/GamePage.swift", 298, '"大块（8 MB 以上）"', '"大块（8 MB+）"'),
 ("app/Sources/UI/Game/GamePage.swift", 298, '"全部 1 MB 以上"', '"全部 1 MB+"'),
 ("app/Sources/UI/Game/GamePage.swift", 298, '"1 MB 以上及溢出部分"', '"1 MB+ 及溢出部分"'),
 ("app/Sources/UI/Game/GameInfo.swift", 13, '"大块（8 MB 以上）"', '"大块（8 MB+）"'),
 ("app/Sources/UI/Game/GameInfo.swift", 13, '"全部 1 MB 以上"', '"全部 1 MB+"'),
 ("app/Sources/UI/Game/GameInfo.swift", 13, '"1 MB 以上及溢出部分"', '"1 MB+ 及溢出部分"'),
 ("app/Sources/UI/Settings/SettingsPages.swift", 124, '"广泛"', '"宽泛"'),
 ("app/Sources/Core/RecommendedSettings.swift", 44, '"大（8 MB+）"', '"大块（8 MB+）"'),
 ("app/Sources/Core/RecommendedSettings.swift", 44, '"广泛"', '"宽泛"'),
 ("app/Sources/Core/RecommendedSettings.swift", 44, '"1 MB+ 及溢出"', '"1 MB+ 及溢出部分"'),
 ("app/Sources/UI/Reports/ReportsScreen.swift", 436, '"大块（8 MB 及以上）"', '"大块（8 MB+）"'),
 ("app/Sources/UI/Reports/ReportsScreen.swift", 436, '"所有 1 MB 及以上的块"', '"全部 1 MB+"'),
 ("app/Sources/UI/Reports/ReportsScreen.swift", 436, '"1 MB 及以上，以及溢出部分"', '"1 MB+ 及溢出部分"'),
]
# batch-003 log()-only lines: revert to English (pure log calls)
FIX += [
 # OverlaySize title is computed from rawValue; give it real Chinese titles
 ("app/Sources/UI/InGame/PerfOverlay.swift", None,
  "    var title: String { rawValue.capitalized }",
  "    var title: String {\n        switch self {\n        case .tiny: return \"极小\"\n        case .small: return \"小\"\n        case .medium: return \"中\"\n        case .large: return \"大\"\n        }\n    }"),
 ("app/Runtime/VCRedist.swift", None,
  "\\(VCRedistPin.version)，\\(VCRedistPin.totalMegabytes) MB，来自 Microsoft",
  "\\(VCRedistPin.version), \\(VCRedistPin.totalMegabytes) MB from Microsoft"),
 ("app/Runtime/VCRedist.swift", None,
  "\\(package.fileName)：已下载并验证", "\\(package.fileName): already downloaded and verified"),
 ("app/Runtime/VCRedist.swift", None,
  "\\(package.fileName)：\\(package.bytes) 字节，SHA-256 已验证",
  "\\(package.fileName): \\(package.bytes) bytes, SHA-256 verified"),
 ("app/Runtime/WineGecko.swift", None,
  "自动下载未完成：\\(message)", "automatic download not done: \\(message)"),
 ("app/Runtime/WineGecko.swift", None, "失败：\\(message)", "failed: \\(message)"),
 ("app/Runtime/WineMono.swift", None,
  "下载 \\(WineMonoPin.url.absoluteString)", "download \\(WineMonoPin.url.absoluteString)"),
 ("app/Runtime/WineMono.swift", None, "失败：\\(message)", "failed: \\(message)"),
]
ffail = []
# plural-s ternary cleanup: on these lines the noun phrase was translated,
# so the English plural branch must become empty (line-scoped, all occurrences)
PLURAL_LINES = [
 ("app/Sources/Core/ExecutableWindow.swift", 72), ("app/Sources/Core/GameStores.swift", 204),
 ("app/Sources/Core/InstallCheck.swift", 104), ("app/Sources/Core/InstallCheck.swift", 240),
 ("app/Sources/UI/AmazonLibraryScreens.swift", 114), ("app/Sources/UI/EALibraryScreens.swift", 96),
 ("app/Sources/UI/Game/GameBindsSection.swift", 193), ("app/Sources/UI/Game/GameEngineSection.swift", 106),
 ("app/Sources/UI/Game/GameEngineSection.swift", 260), ("app/Sources/UI/Game/GamePage.swift", 196),
 ("app/Sources/UI/Game/GamePage.swift", 340), ("app/Sources/UI/Game/GamePage.swift", 343),
 ("app/Sources/UI/Game/GamePage.swift", 347), ("app/Sources/UI/Game/RecommendedSettingsGroup.swift", 52),
 ("app/Sources/UI/GogLibraryScreens.swift", 116), ("app/Sources/UI/InGame/WorkshopTab.swift", 81),
 ("app/Sources/UI/ItchLibraryScreens.swift", 123), ("app/Sources/UI/Reports/ReportsScreen.swift", 73),
 ("app/Sources/UI/Reports/ReportsScreen.swift", 77), ("app/Sources/UI/Reports/ReportsScreen.swift", 212),
 ("app/Sources/UI/Reports/ReportsScreen.swift", 215), ("app/Sources/UI/Reports/ReportsScreen.swift", 325),
 ("app/Sources/UI/Reports/ReportsScreen.swift", 328), ("app/Sources/UI/Reports/ReportsScreen.swift", 331),
 ("app/Sources/UI/Settings/AdvancedSettingsPages.swift", 222),
 ("app/Sources/UI/Settings/ReleaseNotesSheet.swift", 143), ("app/Sources/UI/SetupGuideView.swift", 373),
 ("app/Sources/UI/SteamPage.swift", 310), ("app/Sources/UI/SteamPage.swift", 312),
 ("app/Sources/UI/SteamWorkshopPage.swift", 242), ("app/Sources/UI/StoresScreen.swift", 257),
]
for path, ln in PLURAL_LINES:
    full = os.path.join(ROOT, path)
    lines = open(full, encoding='utf-8').read().split('\n')
    if '? "" : "s"' not in lines[ln - 1]:
        ffail.append((path, ln, 'plural')); continue
    lines[ln - 1] = lines[ln - 1].replace('? "" : "s"', '? "" : ""')
    open(full, 'w', encoding='utf-8').write('\n'.join(lines))
# ReportsLayouts:165 Hide/Show row (was EXCLUDE-misclassified; translated in review)
FIX += [
 ("app/Sources/UI/Reports/ReportsLayouts.swift", 165,
  'Hide \\(earlier.count) earlier report\\(earlier.count == 1 ? "" : "s")',
  '隐藏 \\(earlier.count) 份较早的报告\\(earlier.count == 1 ? "" : "")'),
 ("app/Sources/UI/Reports/ReportsLayouts.swift", 165,
  'Show \\(earlier.count) earlier report\\(earlier.count == 1 ? "" : "s")',
  '显示 \\(earlier.count) 份较早的报告\\(earlier.count == 1 ? "" : "")'),
 # AdvancedSettingsPages:186 pattern must match translated info strings
 ("app/Sources/UI/Settings/AdvancedSettingsPages.swift", 186,
  'localizedCaseInsensitiveContains("experimental")', 'localizedCaseInsensitiveContains("实验")'),
]
for path, ln, old, new in FIX:
    full = os.path.join(ROOT, path)
    if ln is not None:
        lines = open(full, encoding='utf-8').read().split('\n')
        if old not in lines[ln - 1]:
            ffail.append((path, ln, old[:50])); continue
        lines[ln - 1] = lines[ln - 1].replace(old, new, 1)
        open(full, 'w', encoding='utf-8').write('\n'.join(lines))
        continue
    txt = open(full, encoding='utf-8').read()
    if old not in txt:
        ffail.append((path, old[:50])); continue
    open(full, 'w', encoding='utf-8').write(txt.replace(old, new, 1))
# switchSummary coherence (line-scoped, GameRecommendations.swift lines 99-112)
p = os.path.join(ROOT, "app/Runtime/GameRecommendations.swift")
lines = open(p, encoding='utf-8').read().split('\n')
for i in range(98, 112):
    l = lines[i]
    l = l.replace('older NVIDIA card ', '较老的 NVIDIA 显卡 ')
    l = l.replace('? "on" : "off"', '? "开" : "关"')
    l = l.replace('"uncapped"', '"无上限"')
    lines[i] = l
open(p, 'w', encoding='utf-8').write('\n'.join(lines))
print(f"fixups done, failures: {ffail}")
