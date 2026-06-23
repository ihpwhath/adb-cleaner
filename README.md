# ADB Cleaner - Android 手机深度清理助手

<div align="center">

![ADB Cleaner](https://img.shields.io/badge/ADB-Cleaner-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Android-blue?style=for-the-badge)
![Root](https://img.shields.io/badge/Requires-Root-red?style=for-the-badge)

**通过 ADB + Root 权限深度清理安卓手机垃圾文件**

[功能特性](#功能特性) • [安装使用](#安装使用) • [垃圾类型](#垃圾类型) • [命令参考](#命令参考)

</div>

---

## 功能特性

- ✅ **全面扫描** - 应用缓存、系统日志、应用日志、下载残留、临时文件、空目录
- ✅ **三级分类** - 🟢可自动清理 / 🟡需人工判断 / 🔴谨慎清理
- ✅ **安全清理** - 清理前确认、分步执行、保留重要文件
- ✅ **详细报告** - 生成 Markdown 清理报告
- ✅ **零依赖** - 纯 Python 3 标准库，无需 pip install

---

## 前置要求

- ✅ **ADB 工具** - 已安装 adb 并在 PATH 中
- ✅ **USB 调试** - 手机已开启 USB 调试模式
- ✅ **Root 权限** - 手机已 root（KernelSu/Magisk）
- ✅ **USB 连接** - 手机已通过 USB 连接电脑

---

## 安装使用

### 1. 克隆仓库

\\\ash
git clone https://github.com/YOUR_USERNAME/adb-cleaner.git
cd adb-cleaner
\\\

### 2. 连接手机

\\\ash
# 检查设备连接
adb devices

# 检查 root 权限
adb shell "su -c 'id'"
\\\

### 3. 扫描手机

\\\ash
python scripts/scan.py
\\\

### 4. 执行清理

\\\ash
# 模拟清理（仅查看会删除什么）
python scripts/clean.py --dry-run

# 实际执行清理
python scripts/clean.py --work-dir ./output
\\\

---

## 垃圾类型

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

| 类型 | 位置 | 说明 |
|------|------|------|
| 云盘缓存 | /sdcard/Android/data/*/files | 可能包含下载的文件 |
| 微信/QQ缓存 | /tencent, /sdcard/Android/data/com.tencent.* | 建议应用内清理 |

### 🔴 谨慎清理（建议保留）

| 类型 | 位置 | 说明 |
|------|------|------|
| 备份镜像 | /sdcard/Download/*.img | 刷机备份 |
| 通话录音 | /sdcard/MIUI/sound_recorder/call_rec | 重要记录 |
| 用户数据 | /sdcard/DCIM, /sdcard/Pictures | 照片视频 |

---

## 命令参考

### 扫描命令

\\\ash
# 应用缓存
adb shell "su -c 'du -sh /data/data/*/cache 2>/dev/null | sort -rh | head -20'"

# 系统日志
adb shell "su -c 'du -sh /data/anr/'"
adb shell "su -c 'du -sh /data/tombstones/'"

# 下载残留
adb shell "su -c 'ls -lh /sdcard/Download/.* 2>/dev/null'"
\\\

### 清理命令

\\\ash
# 清理应用缓存
adb shell "su -c 'rm -rf /data/data/<包名>/cache/*'"

# 清理系统日志
adb shell "su -c 'rm -rf /data/anr/*'"
adb shell "su -c 'rm -rf /data/tombstones/*'"

# 清理下载残留
adb shell "su -c 'rm -f /sdcard/Download/.pending-*'"

# 清理空目录
adb shell "su -c 'find /sdcard -type d -empty -delete'"
\\\

---

## 注意事项

1. **备份重要数据** - 清理前建议备份重要文件
2. **应用内清理** - 微信、抖音等建议在应用内清理更安全
3. **保留备份镜像** - 原厂 boot/init_boot 镜像建议保留
4. **定期清理** - 建议每月清理一次缓存和日志

---

## 常见问题

<details>
<summary><b>Q: 清理后应用需要重新登录吗？</b></summary>
<br>
不会。清理的是缓存和日志，不触碰应用数据。
</details>

<details>
<summary><b>Q: 清理后照片会丢失吗？</b></summary>
<br>
不会。照片在 /sdcard/DCIM，不在清理范围内。
</details>

<details>
<summary><b>Q: 清理后微信聊天记录会丢失吗？</b></summary>
<br>
不会。聊天记录在应用数据目录，清理的是缓存和临时文件。
</details>

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 致谢

灵感来源于 [storage-analyzer](https://github.com/openclaw/skills/tree/main/storage-analyzer)

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ Star！**

Made with ❤️ by QClaw

</div>
