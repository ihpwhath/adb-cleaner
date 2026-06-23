# ADB Cleaner - OpenClaw Skill

<div align="center">

![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Android-green?style=for-the-badge)
![Requires](https://img.shields.io/badge/Requires-Root-red?style=for-the-badge)

**Android 手机深度清理助手 - OpenClaw Agent Skill**

通过 ADB + Root 权限深度清理安卓手机垃圾文件

</div>

---

## 🤖 这是什么？

这是一个 **OpenClaw Skill**，用于扩展 OpenClaw Agent 的能力。

当用户说以下关键词时，OpenClaw 会自动加载此 skill：
- "清理手机"
- "手机空间不够"
- "手机满了"
- "ADB清理"
- "深度清理手机"

---

## 📦 文件结构

`
adb-cleaner/
├── SKILL.md                           # Skill 主文档（Agent 读取）
├── scripts/
│   ├── scan.py                        # 扫描脚本
│   └── clean.py                       # 清理脚本
└── references/
    └── android_junk_types.md          # 垃圾类型参考文档
`

---

## 🚀 使用方法

### 作为 OpenClaw Skill 使用

1. **安装到 OpenClaw**：
   \\\ash
   # 复制到 OpenClaw skills 目录
   cp -r adb-cleaner ~/.qclaw/skills/
   \\\

2. **触发使用**：
   - 直接在 OpenClaw 对话中说："帮我清理手机"
   - Agent 会自动加载此 skill 并执行清理

### 作为独立工具使用

\\\ash
# 扫描手机
python scripts/scan.py

# 清理手机（模拟）
python scripts/clean.py --dry-run

# 实际清理
python scripts/clean.py --work-dir ./output
\\\

---

## ⚙️ 前置要求

- ✅ **ADB 工具** - 已安装 adb 并在 PATH 中
- ✅ **USB 调试** - 手机已开启 USB 调试模式
- ✅ **Root 权限** - 手机已 root（KernelSu/Magisk）
- ✅ **USB 连接** - 手机已通过 USB 连接电脑

---

## 🗂️ 支持的垃圾类型

### 🟢 可自动清理（安全）

| 类型 | 位置 | 典型大小 |
|------|------|----------|
| 应用缓存 | /data/data/*/cache | 1-3 GB |
| 系统日志 | /data/anr, /data/tombstones | 50-100 MB |
| 应用日志 | debug_log, *.log, *.xlog | 100-300 MB |
| 下载残留 | /sdcard/Download/.pending-* | 100-500 MB |
| 临时文件 | *.tmp, *.temp, *.part | 10-50 MB |
| 空目录 | - | - |

### 🟡 需人工判断

- 云盘缓存（可能包含下载的文件）
- 微信/QQ缓存（建议应用内清理）

### 🔴 谨慎清理（建议保留）

- 备份镜像（刷机备份）
- 通话录音
- 用户数据（照片、视频、文档）

---

## 📖 SKILL.md 说明

SKILL.md 是此 skill 的核心文件，定义了：

1. **触发条件** - 什么关键词会触发此 skill
2. **执行流程** - Agent 执行清理的完整流程
3. **扫描命令** - 各类垃圾文件的扫描方法
4. **清理命令** - 各类垃圾文件的清理方法
5. **安全规则** - 清理时的注意事项

---

## 🛡️ 安全机制

- ✅ **只读扫描** - 扫描阶段不修改任何文件
- ✅ **分步确认** - 清理前展示详细计划
- ✅ **保留重要文件** - 默认保留备份镜像、通话录音
- ✅ **生成报告** - 清理后生成详细的 Markdown 报告

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- 灵感来源于 [storage-analyzer](https://github.com/openclaw/skills/tree/main/storage-analyzer)
- 为 [OpenClaw](https://github.com/openclaw/openclaw) 设计

---

<div align="center">

**如果这个 skill 对你有帮助，请给一个 ⭐️ Star！**

Made with ❤️ for OpenClaw Agent

</div>
