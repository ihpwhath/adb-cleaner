# Android 垃圾文件类型参考

本文档列出 Android 手机上常见的垃圾文件类型、位置和清理建议。

---

## 1. 应用缓存

### 位置

- `/data/data/<包名>/cache/` - 应用内部缓存
- `/sdcard/Android/data/<包名>/cache/` - 应用外部缓存
- `/data/data/<包名>/code_cache/` - 代码缓存

### 说明

- 应用自动生成的临时数据
- 图片缓存、视频缓存、下载缓存等
- 清理后应用会自动重新生成
- **可安全清理**

### 常见大户

| 应用 | 包名 | 典型大小 |
|------|------|----------|
| YouTube | com.google.android.youtube | 500 MB - 2 GB |
| TikTok | com.zhiliaoapp.musically | 300 MB - 1 GB |
| 微信 | com.tencent.mm | 200 MB - 500 MB |
| 抖音 | com.ss.android.ugc.aweme | 300 MB - 1 GB |
| 小爱同学 | com.miui.voiceassist | 100 MB - 500 MB |
| Chrome | com.android.chrome | 100 MB - 500 MB |

### 清理命令

```bash
# 清理指定应用缓存
adb shell "su -c 'rm -rf /data/data/<包名>/cache/*'"

# 清理所有应用缓存
adb shell "su -c 'find /data/data -type d -name cache -exec rm -rf {}/* \\;'"
```

---

## 2. 系统日志

### 位置

| 类型 | 位置 | 说明 |
|------|------|------|
| ANR 日志 | `/data/anr/` | 应用无响应日志 |
| Tombstone | `/data/tombstones/` | 应用崩溃日志 |
| Dropbox | `/data/system/dropbox/` | 系统错误日志 |
| 临时文件 | `/data/local/tmp/` | 临时文件 |
| Logger | `/data/misc/logd/` | 日志守护进程数据 |

### 说明

- 系统和应用崩溃时自动生成
- 用于调试和故障排查
- 普通用户不需要这些日志
- **可安全清理**

### 清理命令

```bash
adb shell "su -c 'rm -rf /data/anr/*'"
adb shell "su -c 'rm -rf /data/tombstones/*'"
adb shell "su -c 'rm -rf /data/system/dropbox/*'"
adb shell "su -c 'rm -rf /data/local/tmp/*'"
```

---

## 3. 应用日志

### 位置

| 类型 | 位置 | 说明 |
|------|------|------|
| debug_log | `/data/data/*/cache/debug_log/` | 调试日志 |
| log 文件 | `/data/data/*/files/*.log` | 应用日志 |
| xlog 文件 | `/data/data/*/files/*.xlog` | 微信/xlog 日志 |
| 日志目录 | `/data/data/*/files/logs/` | 日志目录 |

### 常见应用日志

| 应用 | 日志位置 | 典型大小 |
|------|----------|----------|
| 小米连接服务 | `/data/data/com.xiaomi.mi_connect_service/release_log/` | 30-100 MB |
| 小红书 | `/data/data/com.xingin.xhs/app_xylog_v2/logs/` | 50-200 MB |
| 高德地图 | `/sdcard/Android/data/com.autonavi.minimap/files/logs/` | 20-100 MB |
| 微信 | `/data/data/com.tencent.mm/files/xlog/` | 10-50 MB |
| TikTok | `/data/data/com.zhiliaoapp.musically/files/logs/` | 10-50 MB |

### 说明

- 应用调试和行为日志
- 清理不影响应用功能
- **可安全清理**

### 清理命令

```bash
# 清理 debug_log 目录
adb shell "su -c 'find /data/data -type d -name debug_log -exec rm -rf {}/* \\;'"

# 清理日志文件（排除数据库日志）
adb shell "su -c 'find /data/data -name *.log -type f ! -path \"*/leveldb/*\" -delete'"

# 清理 xlog 文件
adb shell "su -c 'find /data/data -name *.xlog -type f -delete'"
```

---

## 4. 下载残留

### 位置

| 类型 | 位置 | 说明 |
|------|------|------|
| .pending 文件 | `/sdcard/Download/.pending-*` | 下载失败残留 |
| 隐藏目录 | `/sdcard/Download/.xxx/` | 下载器临时目录 |
| APK 文件 | `/sdcard/Download/*.apk` | 已安装的 APK |

### 说明

- 浏览器或下载器下载失败后的残留
- 隐藏文件以 `.` 开头
- **可安全清理**

### 清理命令

```bash
# 清理 .pending 文件
adb shell "su -c 'rm -f /sdcard/Download/.pending-*'"

# 清理隐藏目录
adb shell "su -c 'rm -rf /sdcard/Download/.[!.]*'"
```

---

## 5. 临时文件

### 位置

| 类型 | 位置 | 说明 |
|------|------|------|
| .tmp 文件 | `/sdcard/**/*.tmp` | 临时文件 |
| .temp 文件 | `/sdcard/**/*.temp` | 临时文件 |
| .part 文件 | `/sdcard/**/*.part` | 部分下载文件 |
| 微信临时文件 | `/sdcard/Android/data/com.tencent.mm/MicroMsg/.tmp/` | 微信临时文件 |

### 说明

- 应用生成的临时文件
- 通常在任务完成后应被删除
- 但有时会残留
- **可安全清理**

### 清理命令

```bash
adb shell "su -c 'find /sdcard -name \"*.tmp\" -type f -delete'"
adb shell "su -c 'find /sdcard -name \"*.temp\" -type f -delete'"
adb shell "su -c 'find /sdcard -name \"*.part\" -type f -delete'"
adb shell "su -c 'rm -rf /sdcard/Android/data/com.tencent.mm/MicroMsg/.tmp/*'"
```

---

## 6. 空目录

### 位置

- `/sdcard/` 及其子目录下的空目录

### 说明

- 应用卸载后残留的空目录
- 清理无害
- **可安全清理**

### 清理命令

```bash
# 统计空目录数量
adb shell "su -c 'find /sdcard -type d -empty | wc -l'"

# 删除空目录
adb shell "su -c 'find /sdcard -type d -empty -delete'"
```

---

## 7. 缩略图缓存

### 位置

- `/sdcard/DCIM/.thumbnails/` - 相册缩略图

### 说明

- 系统自动生成的图片缩略图
- 清理后相册会重新生成
- 可能有几百 MB
- **可清理，但会重新生成**

### 清理命令

```bash
adb shell "su -c 'rm -rf /sdcard/DCIM/.thumbnails/*'"
```

---

## 8. 应用卸载残留

### 位置

- `/sdcard/Android/data/<已卸载应用包名>/`
- `/sdcard/Android/obb/<已卸载应用包名>/`

### 说明

- 应用卸载后，部分数据目录可能残留
- 需要检查应用是否已卸载
- **可安全清理**

### 检查方法

1. 获取已安装应用列表：
   ```bash
   adb shell "pm list packages -3" > installed.txt
   ```

2. 列出 Android/data 目录：
   ```bash
   adb shell "ls /sdcard/Android/data/" > data_dirs.txt
   ```

3. 对比两个列表，找出残留

---

## 9. 微信/QQ 缓存

### 位置

| 应用 | 位置 | 说明 |
|------|------|------|
| 微信 | `/tencent/MicroMsg/` | 微信数据 |
| 微信 | `/sdcard/Android/data/com.tencent.mm/` | 微信外部数据 |
| QQ | `/tencent/QQfile_recv/` | QQ 接收文件 |
| QQ | `/tencent/MobileQQ/` | QQ 数据 |

### 说明

- 包含聊天图片、语音、视频缓存
- **建议在应用内清理**
- 直接删除可能影响聊天记录

### 应用内清理路径

- 微信：我 → 设置 → 通用 → 存储空间
- QQ：设置 → 通用 → 存储空间

---

## 10. 云盘缓存

### 位置

| 应用 | 位置 | 典型大小 |
|------|------|----------|
| 夸克云盘 | `/sdcard/Android/data/com.quark.clouddrive/` | 100 MB - 1 GB |
| 百度网盘 | `/sdcard/Android/data/com.baidu.netdisk/` | 100 MB - 1 GB |
| 阿里云盘 | `/sdcard/Android/data/com.alicloud.databox/` | 100 MB - 1 GB |

### 说明

- 可能包含下载的文件和预览缓存
- **需人工判断**
- 检查是否有重要文件

### 清理命令

```bash
# 仅清理缓存目录
adb shell "su -c 'rm -rf /sdcard/Android/data/<包名>/cache/*'"

# 清理日志
adb shell "su -c 'rm -rf /sdcard/Android/data/<包名>/files/log/*'"
```

---

## 11. 不建议清理的内容

### 备份镜像

- 位置：`/sdcard/Download/*.img`
- 说明：原厂 boot/init_boot 镜像，用于刷机恢复
- **建议保留**

### 通话录音

- 位置：`/sdcard/MIUI/sound_recorder/call_rec/`
- 说明：通话录音文件
- **建议保留**

### 用户数据

- 位置：`/sdcard/DCIM/`, `/sdcard/Pictures/`, `/sdcard/Documents/`, `/sdcard/Download/`
- 说明：用户自己的照片、视频、文档
- **需用户决定**

---

## 清理优先级

1. 🔴 **高优先级**：下载残留、系统日志、应用日志
2. 🟡 **中优先级**：应用缓存、临时文件、空目录
3. 🟢 **低优先级**：缩略图缓存、云盘缓存
4. ⚪ **用户决定**：微信/QQ缓存、用户数据

---

## 清理频率建议

- **每周**：清理下载残留
- **每月**：清理应用缓存、系统日志
- **每季度**：深度清理应用日志、检查卸载残留
