---
name: adb-cleaner
description: >
  Android 手机 ADB 清理助手。通过 ADB + root 权限深度清理安卓手机垃圾文件，包括：
  应用缓存、系统日志、应用日志、下载残留、临时文件、空目录等。扫描手机存储，
  按类型分类垃圾文件，给出可执行的清理命令，支持一键清理和选择性清理。
  适用场景：用户说"清理手机""手机空间不够""手机满了""清理安卓""ADB清理"
  "手机垃圾清理""深度清理手机""清理手机缓存""手机存储空间不足"；
  或用户想清理手机存储、释放手机空间、查看手机垃圾时。需要 ADB 调试开启和
  root 权限（KernelSu/Magisk）。
---

# ADB Cleaner - Android 手机深度清理助手

通过 ADB + root 权限对安卓手机进行深度清理，扫描并分类垃圾文件，提供可执行的清理方案。

## 前置要求

- ✅ **ADB 工具**：已安装 adb.exe 并在 PATH 中，或指定路径
- ✅ **USB 调试**：手机已开启 USB 调试模式
- ✅ **Root 权限**：手机已 root（KernelSu/Magisk），ADB shell 可获取 root
- ✅ **连接状态**：手机已通过 USB 连接，ADB 可识别

## 铁律

- **谨慎操作**：只清理明确的垃圾文件（缓存、日志、临时文件），不触碰用户数据
- **备份优先**：清理前提醒用户重要数据已备份
- **分步确认**：清理操作前先展示将删除的内容，让用户确认
- **保留选项**：某些清理项（如备份镜像、通话录音）默认保留，需用户明确要求才删除
- **估算标注**：涉及"可释放空间"一律说明是估算值

## 执行流程

### Step 0 检查环境

```bash
# 检查 ADB 连接
adb devices

# 检查 root 权限
adb shell "su -c 'id'"
```

确认：
- 设备已连接（序列号显示）
- root 权限可用（uid=0）

---

### Step 1 扫描存储空间

```bash
# 获取存储空间概览
adb shell "df -h /data"

# 获取主要分区大小
adb shell "df -h | grep -E '/data|/sdcard|/cache'"
```

记录：
- 总容量、已用、可用、使用率
- 作为清理前后对比的基准

---

### Step 2 扫描垃圾文件

按以下类型依次扫描：

#### 2.1 应用缓存

```bash
# 扫描 /data/data 下各应用缓存大小
adb shell "su -c 'du -sh /data/data/*/cache 2>/dev/null | sort -rh | head -20'"

# 扫描 /sdcard/Android/data 下缓存
adb shell "su -c 'du -sh /sdcard/Android/data/*/cache 2>/dev/null | sort -rh | head -15'"
```

#### 2.2 系统日志

```bash
# ANR 日志
adb shell "su -c 'du -sh /data/anr/'"

# Tombstone 崩溃日志
adb shell "su -c 'du -sh /data/tombstones/'"

# Dropbox 错误日志
adb shell "su -c 'du -sh /data/system/dropbox/'"

# 临时文件
adb shell "su -c 'du -sh /data/local/tmp/'"
```

#### 2.3 应用日志

```bash
# debug_log 目录
adb shell "su -c 'find /data/data -type d -name debug_log 2>/dev/null'"

# 日志文件统计
adb shell "su -c 'find /data/data -name *.log -type f 2>/dev/null | wc -l'"

# xlog 文件
adb shell "su -c 'find /data/data -name *.xlog -type f 2>/dev/null | head -20'"
```

#### 2.4 下载残留

```bash
# Download 目录隐藏文件
adb shell "su -c 'ls -lh /sdcard/Download/.* 2>/dev/null'"

# Download 目录大小
adb shell "su -c 'du -sh /sdcard/Download/'"

# 查找 .pending 文件
adb shell "su -c 'find /sdcard/Download -name \".pending*\" 2>/dev/null'"
```

#### 2.5 临时文件

```bash
# 查找临时文件
adb shell "su -c 'find /sdcard -name \"*.tmp\" -o -name \"*.temp\" -o -name \"*.part\" 2>/dev/null'"

# 微信临时文件
adb shell "su -c 'du -sh /sdcard/Android/data/com.tencent.mm/MicroMsg/.tmp 2>/dev/null'"
```

#### 2.6 空目录

```bash
# 统计空目录数量
adb shell "su -c 'find /sdcard -type d -empty 2>/dev/null | wc -l'"
```

---

### Step 3 分类与分级

将扫描结果按以下三级分类：

#### 🟢 可自动清理（安全）

| 类型 | 位置 | 说明 |
|------|------|------|
| 应用缓存 | /data/data/*/cache | 应用自动生成，可安全清理 |
| 系统日志 | /data/anr, /data/tombstones, /data/system/dropbox | 系统自动生成，清理不影响运行 |
| 应用日志 | /data/data/*/debug_log, *.log, *.xlog | 调试日志，清理不影响功能 |
| 下载残留 | /sdcard/Download/.pending-* | 下载失败/中断的残留文件 |
| 临时文件 | *.tmp, *.temp, *.part | 临时文件，通常可安全删除 |
| 空目录 | - | 空目录，清理无害 |

每个 🟢 项提供：
- 预估释放空间
- 清理命令（可复制执行）
- 清理后影响说明

#### 🟡 需人工判断

| 类型 | 位置 | 说明 |
|------|------|------|
| 应用数据缓存 | /sdcard/Android/data/*/files | 可能包含下载的文件 |
| 微信/QQ缓存 | /tencent, /sdcard/Android/data/com.tencent.* | 可能包含聊天文件 |
| 相册缩略图 | /sdcard/DCIM/.thumbnails | 可重建，但需时间 |
| 云盘缓存 | /sdcard/Android/data/com.quark.clouddrive 等 | 可能包含离线文件 |

每个 🟡 项提供：
- 内容画像（里面大概是什么）
- 处置路径（应用内清理 / 手动审查）
- 风险提示

#### 🔴 谨慎清理（建议保留）

| 类型 | 位置 | 说明 |
|------|------|------|
| 备份镜像 | /sdcard/Download/*.img | 刷机备份，删除后无法恢复系统 |
| 通话录音 | /sdcard/MIUI/sound_recorder/call_rec | 重要记录，不建议删除 |
| 用户文档 | /sdcard/Documents, /sdcard/Download | 用户自己的文件 |
| 照片视频 | /sdcard/DCIM, /sdcard/Pictures | 个人回忆，需用户决定 |

每个 🔴 项提供：
- 为什么建议保留
- 如果确定要删除的步骤

---

### Step 4 执行清理

#### 4.1 确认清理计划

在执行清理前，向用户展示：

```
📋 清理计划
================================
🟢 可自动清理：
  ✅ 应用缓存 (~3 GB)
  ✅ 系统日志 (~60 MB)
  ✅ 应用日志 (~250 MB)
  ✅ 下载残留 (~180 MB)
  ✅ 临时文件 (~10 MB)

🟡 需人工判断：
  ⚠️ 夸克云盘缓存 (~500 MB) - 可能包含下载文件
  
🔴 建议保留：
  📌 备份镜像 (112 MB)
  📌 通话录音 (1.5 MB)

预计释放：约 3.5 GB
是否执行清理？
```

#### 4.2 分步执行

```bash
# 1. 清理应用缓存
adb shell "su -c 'rm -rf /data/data/com.google.android.youtube/cache/*'"
adb shell "su -c 'rm -rf /data/data/com.tencent.mm/cache/*'"
# ... 逐个清理

# 2. 清理系统日志
adb shell "su -c 'rm -rf /data/anr/*'"
adb shell "su -c 'rm -rf /data/tombstones/*'"
adb shell "su -c 'rm -rf /data/system/dropbox/*'"
adb shell "su -c 'rm -rf /data/local/tmp/*'"

# 3. 清理应用日志
adb shell "su -c 'find /data/data -type d -name debug_log -exec rm -rf {}/* \\;'"
adb shell "su -c 'find /data/data -name *.log -type f -delete'"
adb shell "su -c 'find /data/data -name *.xlog -type f -delete'"

# 4. 清理下载残留
adb shell "su -c 'rm -f /sdcard/Download/.pending-*'"
adb shell "su -c 'rm -rf /sdcard/Download/.[!.]*'"

# 5. 清理临时文件
adb shell "su -c 'find /sdcard -name \"*.tmp\" -delete'"
adb shell "su -c 'find /sdcard -name \"*.temp\" -delete'"

# 6. 清理空目录
adb shell "su -c 'find /sdcard -type d -empty -delete'"
```

#### 4.3 验证清理效果

```bash
# 对比清理前后
adb shell "df -h /data"
```

---

### Step 5 生成报告

清理完成后生成 Markdown 报告，包含：

1. **清理前后对比**：已用/可用/使用率变化
2. **清理详情**：每类垃圾的大小、清理命令
3. **保留内容**：列出保留的文件及原因
4. **清理命令汇总**：方便以后重复使用
5. **长期建议**：定期清理、应用内清理等

报告保存到工作目录：`phone_cleanup_YYYYMMDD.md`

---

## 清理命令速查表

### 应用缓存

```bash
# 列出缓存大户
adb shell "su -c 'du -sh /data/data/*/cache 2>/dev/null | sort -rh | head -20'"

# 清理指定应用缓存
adb shell "su -c 'rm -rf /data/data/<包名>/cache/*'"

# 清理所有应用缓存（谨慎）
adb shell "su -c 'find /data/data -type d -name cache -exec rm -rf {}/* \\;'"
```

### 系统日志

```bash
# ANR 日志
adb shell "su -c 'rm -rf /data/anr/*'"

# Tombstone 崩溃日志
adb shell "su -c 'rm -rf /data/tombstones/*'"

# Dropbox 错误日志
adb shell "su -c 'rm -rf /data/system/dropbox/*'"

# 临时文件
adb shell "su -c 'rm -rf /data/local/tmp/*'"
```

### 应用日志

```bash
# debug_log 目录
adb shell "su -c 'find /data/data -type d -name debug_log -exec rm -rf {}/* \\;'"

# 日志文件
adb shell "su -c 'find /data/data -name *.log -type f ! -path \"*/leveldb/*\" -delete'"

# xlog 文件
adb shell "su -c 'find /data/data -name *.xlog -type f -delete'"
```

### 下载残留

```bash
# 清理 .pending 文件
adb shell "su -c 'rm -f /sdcard/Download/.pending-*'"

# 清理隐藏目录
adb shell "su -c 'rm -rf /sdcard/Download/.[!.]*'"
```

### 临时文件

```bash
# 清理临时文件
adb shell "su -c 'find /sdcard -name \"*.tmp\" -delete'"
adb shell "su -c 'find /sdcard -name \"*.temp\" -delete'"
adb shell "su -c 'find /sdcard -name \"*.part\" -delete'"

# 微信临时文件
adb shell "su -c 'rm -rf /sdcard/Android/data/com.tencent.mm/MicroMsg/.tmp/*'"
```

### 空目录

```bash
# 统计空目录
adb shell "su -c 'find /sdcard -type d -empty | wc -l'"

# 删除空目录
adb shell "su -c 'find /sdcard -type d -empty -delete'"
```

---

## 注意事项

1. **备份重要数据**：清理前建议备份重要文件
2. **应用内清理**：微信、抖音等建议在应用内清理更安全
3. **保留备份镜像**：原厂 boot/init_boot 镜像建议保留，以便恢复系统
4. **定期清理**：建议每月清理一次缓存和日志
5. **监控下载**：定期检查 Download 目录是否有残留文件

---

## 常见问题

### Q: 清理后应用需要重新登录吗？

A: 不会。清理的是缓存和日志，不触碰应用数据。

### Q: 清理后照片会丢失吗？

A: 不会。照片在 /sdcard/DCIM，不在清理范围内。

### Q: 清理后微信聊天记录会丢失吗？

A: 不会。聊天记录在应用数据目录，清理的是缓存和临时文件。

### Q: 备份镜像可以删除吗？

A: 可以，但建议保留。如果系统出现问题，可以用镜像恢复。

### Q: 清理后手机会变快吗？

A: 可能会有轻微改善，但主要目的是释放存储空间。性能提升主要来自系统优化的清理。

---

## 版本历史

- v1.0.0 (2026-06-23): 初始版本，支持应用缓存、系统日志、应用日志、下载残留清理
