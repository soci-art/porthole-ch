#!/usr/bin/env python3
"""Close-game fix for the zh-Hans build (Porthole patch series, app side).

Why: upstream's in-game "Close game" is SessionController.requestClose()
alone — one injected Alt+F4 chord and nothing after it. Games that read
the keyboard through raw input never route that chord through
DefWindowProc, so it never becomes a close; both Steam and direct starts
look completely dead (verified on device, 2026-11-09).

What this script changes in the cloned tree ($SRC), after the zh-Hans
translation and manual_patches have run:

  1. copies i18n/0180-winios-close-window.patch into $SRC/patches/
     (the workflow applies it to vendor/Madeira: a new
     winios_drv_close_window_if_owner() next to close_desktop's,
     posting WM_CLOSE / WM_SYSCOMMAND-SC_CLOSE from the window's own
     thread via NtUserPostMessage);
  2. app/Runtime/Winios/Winios.h  — declares winios_request_close_window()
     and winios_game_layer_hwnd();
  3. app/Runtime/Winios/Winios.m  — stages close requests like
     g_close_desktop does and delivers them from winios_pProcessEvents;
     clears a staged request in winios_session_reset(); the game-layer
     HWND getter;
  4. app/Sources/Core/SessionController.swift — remembers the game
     window from the launch census, and gains closeGame(): graded
     normal-close tiers (WM_CLOSE -> SC_CLOSE -> Alt+F4 -> Dock
     desktop close), waiting after each, then a prompt whose default
     is "keep waiting"; force-ending (closeApp) is never automatic.
     requestClose() itself is unchanged (RestartCoordinator uses it);
  5. app/Sources/UI/SessionView.swift — the menu's onClose now calls
     session.closeGame();
  6. GameMenu.swift / HUD.swift — the Close row shows "正在关闭…"
     while the flow runs;
  7. app/Config/Engine.xcconfig — engine revision bumped (r1 -> r2)
     with the input digest recomputed using tools/engine.sh's own
     algorithm, because engine inputs (patches/, app/Runtime) changed.

Anchors are code lines without user-visible strings, identical in the
upstream and translated trees. Any anchor that does not match exactly
aborts the build step (exit 1) instead of silently shipping an
unpatched tree.

Usage: close_fix.py <src-tree>   (i18n dir = this script's directory)
"""
import hashlib
import os
import shutil
import subprocess
import sys

SRC = os.path.abspath(sys.argv[1])
HERE = os.path.dirname(os.path.abspath(__file__))
failures = []


def replace(path, old, new, count=1):
    full = os.path.join(SRC, path)
    txt = open(full, encoding="utf-8").read()
    if txt.count(old) != count:
        failures.append(f"{path}: anchor occurs {txt.count(old)}x (want {count}): {old[:70]!r}")
        return
    open(full, "w", encoding="utf-8").write(txt.replace(old, new, count))


# --- 1. the Madeira driver patch -------------------------------------------
shutil.copyfile(os.path.join(HERE, "0180-winios-close-window.patch"),
                os.path.join(SRC, "patches", "0180-winios-close-window.patch"))

# --- 2. Winios.h -------------------------------------------------------------
replace("app/Runtime/Winios/Winios.h",
"""/* Ends a Dock session: explorer's desktop is asked to close (its own thread posts WM_CLOSE). */
void winios_close_desktop(void);""",
"""/* Ends a Dock session: explorer's desktop is asked to close (its own thread posts WM_CLOSE). */
void winios_close_desktop(void);
/* Asks one game window to close normally (zh-Hans fix, patch 0180): the close is posted as
 * WM_CLOSE (syscmd=0) or WM_SYSCOMMAND/SC_CLOSE (syscmd=1) from the window's own Wine thread,
 * the way winios_close_desktop treats the desktop. hwnd is a value from the window census or
 * winios_game_layer_hwnd(). The request stays staged only briefly, so a recycled handle value
 * can never receive a stale close. */
void winios_request_close_window(unsigned long long hwnd, int syscmd);
/* Main thread. The window presenting the running game through the fullscreen game layer
 * (0 when none): for direct (non-desktop) starts, whose window the census is not fed. */
unsigned long long winios_game_layer_hwnd(void);""")

# --- 3. Winios.m --------------------------------------------------------------
replace("app/Runtime/Winios/Winios.m",
"""extern int winios_drv_close_desktop_if_owner(void);""",
"""extern int winios_drv_close_desktop_if_owner(void);
extern int winios_drv_close_window_if_owner(HWND hwnd, int syscmd);""")

replace("app/Runtime/Winios/Winios.m",
"""static atomic_int g_close_desktop;
void winios_close_desktop(void) { atomic_store(&g_close_desktop, 1); }""",
"""static atomic_int g_close_desktop;
void winios_close_desktop(void) { atomic_store(&g_close_desktop, 1); }

/* winios_request_close_window: the app asks one game window to close
 * normally (zh-Hans fix, patch 0180). Staged here like g_close_desktop
 * and posted by the window's own thread out of its event pump
 * (winios_pProcessEvents). Staged for a few seconds only, so a handle
 * value the session has since recycled can never receive a stale
 * close. syscmd picks the message: 0 = WM_CLOSE, 1 = WM_SYSCOMMAND /
 * SC_CLOSE. */
static atomic_ullong g_close_window_hwnd;
static atomic_int g_close_window_syscmd;
static atomic_llong g_close_window_deadline_ms;
void winios_request_close_window(unsigned long long hwnd, int syscmd) {
    atomic_store(&g_close_window_syscmd, syscmd);
    atomic_store(&g_close_window_deadline_ms, (long long)(CACurrentMediaTime() * 1000.0) + 5000);
    atomic_store(&g_close_window_hwnd, hwnd);   /* stored last: it arms the request */
}""")

replace("app/Runtime/Winios/Winios.m",
"""    if (atomic_load_explicit(&g_close_desktop, memory_order_relaxed)) {
        int r = winios_drv_close_desktop_if_owner();
        int expected = 1;
        if (r && atomic_compare_exchange_strong(&g_close_desktop, &expected, 0)) {
            fprintf(stderr, "[winios] desktop close posted=%d (the Dock session ends)\\n", r);
            fflush(stderr);
        }
    }""",
"""    if (atomic_load_explicit(&g_close_desktop, memory_order_relaxed)) {
        int r = winios_drv_close_desktop_if_owner();
        int expected = 1;
        if (r && atomic_compare_exchange_strong(&g_close_desktop, &expected, 0)) {
            fprintf(stderr, "[winios] desktop close posted=%d (the Dock session ends)\\n", r);
            fflush(stderr);
        }
    }
    unsigned long long close_hwnd = atomic_load_explicit(&g_close_window_hwnd, memory_order_relaxed);
    if (close_hwnd) {
        if (CACurrentMediaTime() * 1000.0 > (double)atomic_load_explicit(&g_close_window_deadline_ms, memory_order_relaxed)) {
            unsigned long long expected_h = close_hwnd;
            atomic_compare_exchange_strong(&g_close_window_hwnd, &expected_h, 0);   /* expired unposted; never chase a recycled handle */
        } else {
            int r = winios_drv_close_window_if_owner((HWND)(uintptr_t)close_hwnd, atomic_load_explicit(&g_close_window_syscmd, memory_order_relaxed));
            if (r) {
                unsigned long long expected_h = close_hwnd;
                if (atomic_compare_exchange_strong(&g_close_window_hwnd, &expected_h, 0)) {
                    fprintf(stderr, "[winios] game window close posted=%d (hwnd=0x%llx)\\n", r, close_hwnd);
                    fflush(stderr);
                }
            }
        }
    }""")

replace("app/Runtime/Winios/Winios.m",
"""    atomic_store(&g_size_game_hwnd, 0);
    atomic_store(&g_close_desktop, 0);""",
"""    atomic_store(&g_size_game_hwnd, 0);
    atomic_store(&g_close_desktop, 0);
    atomic_store(&g_close_window_hwnd, 0);""")

replace("app/Runtime/Winios/Winios.m",
"""        if (g_comp_game) (void)winios_game_window_shown(key);
    });
}""",
"""        if (g_comp_game) (void)winios_game_window_shown(key);
    });
}

/* The window presenting the running game through the fullscreen game
 * layer (0 when none). Main thread, like winios_game_client_rect. */
unsigned long long winios_game_layer_hwnd(void) {
    return g_game_input_key ? [g_game_input_key unsignedLongLongValue] : 0;
}""")

# --- 4. SessionController.swift ------------------------------------------------
replace("app/Sources/Core/SessionController.swift",
"""import SwiftUI""",
"""import SwiftUI
import UIKit""")

replace("app/Sources/Core/SessionController.swift",
"""    fileprivate func startLaunchWatch(for game: Game, steam: Bool) {
        launchWatch?.invalidate()""",
"""    fileprivate func startLaunchWatch(for game: Game, steam: Bool) {
        launchWatch?.invalidate()
        gameWindowHWND = 0; gameWindowPID = 0""")

replace("app/Sources/Core/SessionController.swift",
"""            if image.hasPrefix(folder), w.visible != 0, w.w >= 160, w.h >= 120, w.metal != 0 || w.presents > 0 { found = true; break }""",
"""            if image.hasPrefix(folder), w.visible != 0, w.w >= 160, w.h >= 120, w.metal != 0 || w.presents > 0 {
                found = true
                if gameWindowHWND == 0 { gameWindowHWND = w.hwnd; gameWindowPID = w.pid }
                break
            }""")

replace("app/Sources/Core/SessionController.swift",
"""    /// Ask the game to close (Alt+F4). The runtime cannot be restarted reliably in-process, so after a game ends the app should be relaunched.
    func requestClose() {
        winios_post_key(0x12, 1); winios_post_key(0x73, 1); winios_post_key(0x73, 0); winios_post_key(0x12, 0)
    }""",
"""    /// Ask the game to close (Alt+F4). The runtime cannot be restarted reliably in-process, so after a game ends the app should be relaunched.
    func requestClose() {
        winios_post_key(0x12, 1); winios_post_key(0x73, 1); winios_post_key(0x73, 0); winios_post_key(0x12, 0)
    }

    // MARK: - Closing the game normally (zh-Hans fix)
    //
    // The in-game menu's Close game used to be requestClose() alone: one
    // Alt+F4 chord and nothing after it. A game that reads the keyboard
    // through raw input never routes that chord through DefWindowProc,
    // so it never becomes a close and the menu item looked dead (both
    // Steam and direct starts). This flow instead asks the game's own
    // window to close the way Windows programs expect — a posted
    // WM_CLOSE, then SC_CLOSE, then the old Alt+F4, then (Dock sessions)
    // the desktop close — waiting after each step. If none of that
    // closes it, the person is asked; force-ending is never automatic
    // and "keep waiting" is the prompt's default way out.

    /// The game's main window as the launch watch found it in the window census (0 = not seen there).
    private var gameWindowHWND: UInt64 = 0
    private var gameWindowPID: UInt32 = 0
    /// True while closeGame() is working; the in-game menu shows it on the Close row.
    private(set) var closeInProgress = false
    private var closeTask: Task<Void, Never>?
    private var closePromptAnswer: ClosePromptAnswer?
    private weak var closePrompt: UIAlertController?
    private enum ClosePromptAnswer { case wait, stop }

    /// The in-game menu's Close game action: try to close the game normally, in graded steps.
    func closeGame() {
        guard state == .running, !closeInProgress else { return }
        closeInProgress = true
        LogStore.shared.log("[close] close requested from the in-game menu; asking the game to close normally")
        closeTask = Task { @MainActor [weak self] in await self?.runCloseFlow() }
    }

    private func runCloseFlow() async {
        // The windows worth asking: the one the launch watch found, the
        // one presenting the game layer (direct starts, whose window the
        // census is not fed), or — when neither named one — the running
        // game's windows from one fresh census sweep.
        var targets: [UInt64] = []
        if gameWindowHWND != 0 { targets.append(gameWindowHWND) }
        let layer = winios_game_layer_hwnd()
        if layer != 0, !targets.contains(layer) { targets.append(layer) }
        if targets.isEmpty { targets = await censusGameWindows() }

        if !targets.isEmpty {
            for hwnd in targets { winios_request_close_window(hwnd, 0) }
            LogStore.shared.log("[close] WM_CLOSE posted to \\(targets.count) game window(s); waiting")
            if await waitForSessionEnd(seconds: 6) { finishCloseFlow(); return }
            for hwnd in targets { winios_request_close_window(hwnd, 1) }
            LogStore.shared.log("[close] game still running; SC_CLOSE posted; waiting")
            if await waitForSessionEnd(seconds: 6) { finishCloseFlow(); return }
        }
        requestClose()
        LogStore.shared.log("[close] game still running; Alt+F4 sent; waiting")
        if await waitForSessionEnd(seconds: 6) { finishCloseFlow(); return }
        if dockGame != nil {
            winios_close_desktop()
            LogStore.shared.log("[close] game still running; desktop close asked (Dock session); waiting")
            if await waitForSessionEnd(seconds: 6) { finishCloseFlow(); return }
        }
        // None of the normal ways closed it. Ask the person; never force.
        while !Task.isCancelled {
            let answer = await promptWhetherToStop()
            if Task.isCancelled { break }
            switch answer {
            case .stop:
                LogStore.shared.log("[close] the person chose to stop the game after it did not close normally")
                closeInProgress = false
                closeApp()
                return
            case .wait:
                LogStore.shared.log("[close] the person chose to keep waiting for the game to close")
                if await waitForSessionEnd(seconds: 20) { finishCloseFlow(); return }
            }
        }
        finishCloseFlow()
    }

    private func finishCloseFlow() {
        if state == .ended || state == .idle { LogStore.shared.log("[close] the game closed") }
        closeInProgress = false
        closeTask = nil
    }

    /// Polls until the session reports the game over (or the time runs out).
    private func waitForSessionEnd(seconds: Double) async -> Bool {
        let deadline = Date().addingTimeInterval(seconds)
        while true {
            if state == .ended || state == .idle { return true }
            if Task.isCancelled || Date() >= deadline { return state == .ended || state == .idle }
            try? await Task.sleep(for: .milliseconds(400))
        }
    }

    /// One fresh census sweep for the running game's top-level windows.
    private func censusGameWindows() async -> [UInt64] {
        guard let g = game else { return [] }
        let folder = Self.folderPrefix(ofWindowsPath: g.exe)
        winios_window_census_enable(1)
        var found: [UInt64] = []
        for _ in 0..<4 {
            var windows = [winios_census_window](repeating: winios_census_window(), count: Int(WINIOS_CENSUS_MAX))
            let count = Int(winios_window_census(&windows, Int32(windows.count)))
            for var w in windows.prefix(count) {
                let image = withUnsafePointer(to: &w.image) { $0.withMemoryRebound(to: CChar.self, capacity: Int(WINIOS_CENSUS_IMAGE)) { String(cString: $0) } }
                let mine = (gameWindowPID != 0 && w.pid == gameWindowPID) || image.hasPrefix(folder)
                if mine, w.visible != 0, !found.contains(w.hwnd) { found.append(w.hwnd) }
            }
            if !found.isEmpty { break }
            try? await Task.sleep(for: .milliseconds(300))
        }
        winios_window_census_enable(dockGame != nil ? 2 : 0)
        return found
    }

    /// Asks what to do now that the game has not closed the normal ways.
    /// Resolves when the person answers, or with .wait if the session
    /// ends on its own meanwhile.
    private func promptWhetherToStop() async -> ClosePromptAnswer {
        closePromptAnswer = nil
        presentClosePrompt()
        while closePromptAnswer == nil {
            if state == .ended || state == .idle { dismissClosePrompt(); return .wait }
            if Task.isCancelled { dismissClosePrompt(); return .wait }
            try? await Task.sleep(for: .milliseconds(300))
        }
        return closePromptAnswer ?? .wait
    }

    private func presentClosePrompt() {
        guard let scene = UIApplication.shared.connectedScenes.compactMap({ $0 as? UIWindowScene }).first(where: { $0.activationState != .unattached }),
              let root = scene.windows.first(where: \\.isKeyWindow)?.rootViewController else { closePromptAnswer = .wait; return }
        var top = root
        while let presented = top.presentedViewController { top = presented }
        let name = game?.name ?? "游戏"
        let alert = UIAlertController(title: "\\(name) 还没有关闭", message: "已经用正常方式请它关闭，它还没有退出。可以继续等它自己关闭；强制结束会丢失未保存的进度。", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "继续等待", style: .cancel) { [weak self] _ in self?.closePromptAnswer = .wait })
        alert.addAction(UIAlertAction(title: "强制结束", style: .destructive) { [weak self] _ in self?.closePromptAnswer = .stop })
        closePrompt = alert
        top.present(alert, animated: true)
    }

    private func dismissClosePrompt() {
        closePrompt?.dismiss(animated: true)
        closePrompt = nil
    }""")

# --- 5. SessionView.swift -------------------------------------------------------
replace("app/Sources/UI/SessionView.swift",
"""                        onClose: { session.requestClose() },""",
"""                        onClose: { session.closeGame() },""")

# --- 6. GameMenu.swift / HUD.swift ----------------------------------------------
replace("app/Sources/UI/InGame/GameMenu.swift",
"""    @Published var gameName: String?""",
"""    @Published var gameName: String?
    /// True while the graded close flow is working; the Session card shows it on the Close row.
    @Published var closingGame = false""")

replace("app/Sources/UI/InGame/GameMenu.swift",
"""            MenuActionRow(title: "关闭游戏", symbol: "power", destructive: true) { model.closeGame() }""",
"""            MenuActionRow(title: "关闭游戏", symbol: "power", detail: model.closingGame ? "正在关闭…" : nil, destructive: true) { model.closeGame() }""")

replace("app/Sources/UI/HUD.swift",
"""        menuModel.gameName = gameName""",
"""        menuModel.gameName = gameName
        menuModel.closingGame = AppModel.shared.session.closeInProgress""")

if failures:
    print("close_fix FAILED:")
    for f in failures:
        print("  -", f)
    sys.exit(1)

# --- 7. Engine.xcconfig bump ------------------------------------------------------
# tools/engine.sh's digest: sha256 over the Madeira pin (full gitlink SHA),
# then for every file in patches/ and app/Runtime/ (sorted, LC_ALL=C):
# the path line and the file's sha256 line. Recomputed over the final tree
# (this script has already placed patch 0180 and edited app/Runtime).
def tree_files(root, exclude_names=()):
    out = []
    for dirpath, dirs, files in os.walk(root):
        dirs.sort()
        for name in files:
            if name in exclude_names:
                continue
            out.append(os.path.relpath(os.path.join(dirpath, name), SRC))
    return sorted(out)


pin = None
try:
    pin = subprocess.run(["git", "-C", SRC, "ls-tree", "HEAD", "vendor/Madeira"],
                         capture_output=True, text=True, timeout=30).stdout.split()[2]
except Exception:
    pass
if not pin:
    pin = "5fda6a0e9543e5de1df010aff35748ab913fd0d9"   # v1.2.1's recorded submodule pin

lines = [pin]
for rel in tree_files(os.path.join(SRC, "patches")):
    lines.append(rel)
    lines.append(hashlib.sha256(open(os.path.join(SRC, rel), "rb").read()).hexdigest())
for rel in tree_files(os.path.join(SRC, "app", "Runtime"), exclude_names=(".DS_Store", "PROVENANCE.md")):
    lines.append(rel)
    lines.append(hashlib.sha256(open(os.path.join(SRC, rel), "rb").read()).hexdigest())
digest = hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()

conf_path = os.path.join(SRC, "app", "Config", "Engine.xcconfig")
conf = open(conf_path, encoding="utf-8").read()
base = None
rev = None
for line in conf.splitlines():
    if line.startswith("PORTHOLE_ENGINE_MADEIRA"):
        base = line.split("=", 1)[1].strip()
    if line.startswith("PORTHOLE_ENGINE_REVISION"):
        rev = int(line.split("=", 1)[1].strip())
if base is None or rev is None:
    print("close_fix FAILED: Engine.xcconfig lacks MADEIRA/REVISION lines")
    sys.exit(1)
new_rev = rev + 1
open(conf_path, "w", encoding="utf-8").write(
    "// The game engine this source builds (see tools/engine.sh). Compatibility badges belong to an engine, not to an app version.\n"
    "// Do not edit by hand: run  tools/engine.sh bump  after a change that affects how games run (a new Madeira pin, a patch, the runtime glue).\n"
    f"PORTHOLE_ENGINE_MADEIRA = {base}\n"
    f"PORTHOLE_ENGINE_REVISION = {new_rev}\n"
    f"PORTHOLE_ENGINE_ID = {base}-r{new_rev}\n"
    "// The inputs this engine was recorded from; tools/engine.sh check compares against them.\n"
    f"PORTHOLE_ENGINE_INPUTS = {digest}\n")

print(f"close_fix done: patch 0180 placed, Winios + closeGame flow applied, engine -> {base}-r{new_rev} (inputs {digest[:12]}...)")
