---
name: adb-cleaner
version: 2.0.0
description: >
  Android 手机 ADB 深度清理助手。通过 ADB + Root 权限扫描并清理安卓手机垃圾文件，
  包括应用缓存、系统日志、应用日志、下载残留、临时文件、空目录等。
  自动检测设备连接，智能分类垃圾，生成详细报告。
  触发词：清理手机、手机空间不够、手机满了、ADB清理、深度清理手机、手机垃圾清理。
  需要：USB 调试 + Root 权限（KernelSu/Magisk）。
---

# ADB Cleaner v2.0 - Android 手机深度清理助手

## 前置检查（自动执行）

Agent 会自动检查：
1. ADB 是否已安装
2. 设备是否已连接
3. Root 权限是否可用

如果任何一项不满足，Agent 会提示用户并提供解决方案。

---

## 执行流程

### Step 1: 检查环境

``bash
# 检查 ADB 连接
adb devices

# 检查 Root 权限
adb shell "su -c 'id'"
``

确认：
- 设备已连接（显示序列号）
- Root 权限可用（uid=0）

---

### Step 2: 扫描存储空间

``bash
adb shell "df -h /data"
``

记录：总容量、已用、可用、使用率

---

### Step 3: 扫描垃圾文件

#### 3.1 应用缓存

``bash
adb shell "su -c 'du -sh /data/data/*/cache 2>/dev/null | sort -rh | head -20'"
``

#### 3.2 系统日志

``bash
adb shell "su -c 'du -sh /data/anr/'"
adb shell "su -c 'du -sh /data/tombstones/'"
adb shell "su -c 'du -sh /data/system/dropbox/'"
``

#### 3.3 应用日志

``bash
adb shell "su -c 'find /data/data -type d -name debug_log 2>/dev/null'"
adb shell "su -c 'find /data/data -name *.log -type f 2>/dev/null | wc -l'"
``

#### 3.4 下载残留

``bash
adb shell "su -c 'ls -lh /sdcard/Download/.* 2>/dev/null'"
``

#### 3.5 临时文件

``bash
adb shell "su -c 'find /sdcard -name \"*.tmp\" 2>/dev/null | wc -l'"
``

#### 3.6 空目录

``bash
adb shell "su -c 'find /sdcard -type d -empty 2>/dev/null | wc -l'"
``

---

### Step 4: 分类与确认

将扫描结果分为三级：

**可自动清理（安全）：**
- 应用缓存
- 系统日志（ANR、Tombstone、Dropbox）
- 应用日志（debug_log、*.log、*.xlog）
- 下载残留
- 临时文件
- 空目录

**需人工判断：**
- 云盘缓存
- 微信/QQ 缓存

**建议保留：**
- 备份镜像
- 通话录音
- 用户数据

---

### Step 5: 执行清理

#### 5.1 应用缓存

``bash
adb shell "su -c 'rm -rf /data/data/<包名>/cache/*'"
``

#### 5.2 系统日志

``bash
adb shell "su -c 'rm -rf /data/anr/*'"
adb shell "su -c 'rm -rf /data/tombstones/*'"
adb shell "su -c 'rm -rf /data/system/dropbox/*'"
``

#### 5.3 应用日志

``bash
adb shell "su -c 'find /data/data -type d -name debug_log -exec rm -rf {}/* \\;'"
adb shell "su -c 'find /data/data -name *.log -type f -delete'"
``

#### 5.4 下载残留

``bash
adb shell "su -c 'rm -f /sdcard/Download/.pending-*'"
``

#### 5.5 临时文件

``bash
adb shell "su -c 'find /sdcard -name \"*.tmp\" -delete'"
``

#### 5.6 空目录

``bash
adb shell "su -c 'find /sdcard -type d -empty -delete'"
``

---

### Step 6: 生成报告

生成 Markdown 报告，包含：
- 清理前后对比
- 清理详情
- 清理命令汇总

保存到工作目录：phone_cleanup_YYYYMMDD.md

---

## 常见问题

**Q: 清理后应用需要重新登录吗？**
A: 不会。清理的是缓存和日志。

**Q: 清理后照片会丢失吗？**
A: 不会。照片不在清理范围内。

**Q: 备份镜像可以删除吗？**
A: 可以，但建议保留以便恢复系统。

---

## 版本历史

- v2.0.0 (2026-06-23): 添加自动检测、智能分类、详细报告
- v1.0.0 (2026-06-23): 初始版本