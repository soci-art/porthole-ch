# Porthole 简体中文汉化版

本仓库是 [tylerkaska112/Porthole](https://github.com/tylerkaska112/Porthole)（版本 v1.2.1）的**非官方修改版**，与上游作者无关。改动范围只有一项：把应用的全部用户可见文案翻译为简体中文——包括界面文字，以及一般汉化容易漏掉的**报错、提示、状态与进度文案**（全量汉化，不留英文；运行日志与诊断内容不在翻译范围）。功能与上游保持一致，成品为**未签名 IPA**，发布在本仓库的发行版（Release）中，供使用者自行签名安装。

> 本仓库的简体中文翻译（应用内文案与文档）由 AI 完成。

## 当前状态

🚧 **构建路线探针阶段，暂无可下载的 IPA。**

原因：上游没有任何本地化机制（全部文案写死在源码里），唯一能全量汉化的路线是「源码原地翻译后重新编译」。而 App 链接的部分引擎静态库不在任何公开仓库中，需要先在云端 Mac 上验证能否按上游锁定的引擎源码补建这些库、并重建出与官方包结构一致的未签名 IPA。探针方案见 [`probe-ci/PROBE-PLAN.md`](probe-ci/PROBE-PLAN.md)，技术调查报告见 [`notes/INVESTIGATION.md`](notes/INVESTIGATION.md)。探针通过后进入全量翻译与正式交付阶段，届时本 README 会换成上游 README 的完整中文版。

仓库保持精简（说明、探针文件、调查笔记），上游源码由构建流程在云端按 v1.2.1 标签自动拉取组装，不在本仓库内保存副本。

## 许可证

沿用上游许可证：GPL-3.0-or-later，及上游对 Apple Metal Shader Converter 的附加许可（见上游仓库的 `LICENSE` 与 `LICENSE-EXCEPTION.md`）。Porthole 基于 Madeira 运行时（Wine、FEX、DXMT），各组件保留其各自许可证。
