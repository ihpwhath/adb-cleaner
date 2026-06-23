# ADB Cleaner - OpenClaw Skill

Android 手机深度清理助手，通过 ADB + Root 权限深度清理安卓手机垃圾文件。

---

## 一键安装

在 OpenClaw 中说：

`
安装这个 skill：https://github.com/ihpwhath/adb-cleaner
`

或者：

`
帮我安装 adb-cleaner skill
`

OpenClaw 会自动安装此 skill。

---

## 这是什么？

这是一个 OpenClaw Skill，用于扩展 OpenClaw Agent 的能力。

当用户说以下关键词时，OpenClaw 会自动加载此 skill：
- 清理手机
- 手机空间不够
- 手机满了
- ADB清理
- 深度清理手机
- 手机垃圾清理

---

## 功能特性

- 全面扫描 - 应用缓存、系统日志、应用日志、下载残留、临时文件、空目录
- 三级分类 - 可自动清理 / 需人工判断 / 谨慎清理
- 安全清理 - 清理前确认、分步执行、保留重要文件
- 详细报告 - 生成 Markdown 清理报告
- 零依赖 - 纯 Python 3 标准库

---

## 前置要求

- ADB 工具 - 已安装 adb 并在 PATH 中
- USB 调试 - 手机已开启 USB 调试模式
- Root 权限 - 手机已 root（KernelSu/Magisk）
- USB 连接 - 手机已通过 USB 连接电脑

---

## 使用方法

### 方法一：通过 OpenClaw 使用（推荐）

安装后，直接对 OpenClaw 说：

`
帮我清理手机
`

Agent 会自动：
1. 检查 ADB 连接和 Root 权限
2. 扫描手机存储空间
3. 列出可清理的垃圾文件
4. 征得你同意后执行清理
5. 生成清理报告

### 方法二：作为独立工具使用

扫描手机：

`
python scripts/scan.py
`

清理手机（模拟，不实际执行）：

`
python scripts/clean.py --dry-run
`

实际清理：

`
python scripts/clean.py --work-dir ./output
`

---

## 支持的垃圾类型

### 可自动清理（安全）

- 应用缓存：/data/data/*/cache（1-3 GB）
- 系统日志：/data/anr, /data/tombstones（50-100 MB）
- 应用日志：debug_log, *.log, *.xlog（100-300 MB）
- 下载残留：/sdcard/Download/.pending-*（100-500 MB）
- 临时文件：*.tmp, *.temp, *.part（10-50 MB）
- 空目录

### 需人工判断

- 云盘缓存（可能包含下载的文件）
- 微信/QQ 缓存（建议应用内清理）

### 建议保留

- 备份镜像（刷机备份）
- 通话录音
- 用户数据（照片、视频、文档）

---

## 文件结构

`
adb-cleaner/
├── SKILL.md                      # Skill 主文档（Agent 读取）
├── scripts/
│   ├── scan.py                   # 扫描脚本
│   └── clean.py                  # 清理脚本
└── references/
    └── android_junk_types.md     # 垃圾类型参考
`

---

## 安全机制

- 只读扫描 - 扫描阶段不修改任何文件
- 分步确认 - 清理前展示详细计划
- 保留重要文件 - 默认保留备份镜像、通话录音
- 生成报告 - 清理后生成详细的 Markdown 报告

---

## 许可证

MIT License

---

如果这个 skill 对你有帮助，请给一个 Star！

Made for OpenClaw Agent