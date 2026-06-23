#!/usr/bin/env python3
"""
ADB Cleaner - Android 手机垃圾扫描脚本
扫描手机存储，分类垃圾文件，输出 JSON 结果
"""

import subprocess
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class ADBScanner:
    """ADB 手机垃圾扫描器"""

    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.device_id = None
        self.has_root = False

    def run_adb(self, command: str, timeout: int = 30) -> Tuple[bool, str]:
        """执行 ADB 命令"""
        try:
            result = subprocess.run(
                f'{self.adb_path} {command}',
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def run_adb_su(self, command: str, timeout: int = 60) -> Tuple[bool, str]:
        """以 root 权限执行 ADB 命令"""
        return self.run_adb(f'shell "su -c \'{command}\'"', timeout)

    def check_connection(self) -> Dict:
        """检查 ADB 连接和 root 权限"""
        result = {
            "connected": False,
            "device_id": None,
            "has_root": False,
            "error": None
        }

        # 检查设备连接
        success, output = self.run_adb("devices")
        if not success:
            result["error"] = "ADB 命令执行失败"
            return result

        lines = output.split('\n')
        for line in lines[1:]:
            if line.strip() and 'device' in line:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'device':
                    result["connected"] = True
                    result["device_id"] = parts[0]
                    self.device_id = parts[0]
                    break

        if not result["connected"]:
            result["error"] = "未检测到已连接的设备"
            return result

        # 检查 root 权限
        success, output = self.run_adb("shell \"su -c 'id'\"")
        if success and 'uid=0' in output:
            result["has_root"] = True
            self.has_root = True

        return result

    def get_storage_info(self) -> Dict:
        """获取存储空间信息"""
        result = {
            "total": None,
            "used": None,
            "available": None,
            "use_percent": None
        }

        success, output = self.run_adb('shell "df -h /data"')
        if success:
            # 解析: /dev/block/dm-54 228G 91G 136G 41% /apex/...
            lines = output.split('\n')
            for line in lines:
                if '/dev/block' in line or line.startswith('/dev/'):
                    parts = line.split()
                    if len(parts) >= 5:
                        result["total"] = parts[1]
                        result["used"] = parts[2]
                        result["available"] = parts[3]
                        result["use_percent"] = parts[4]

        return result

    def parse_size_to_mb(self, size_str: str) -> float:
        """将大小字符串转换为 MB"""
        if not size_str:
            return 0

        size_str = size_str.strip().upper()
        match = re.match(r'^([\d.]+)([KMGT]?)', size_str)
        if not match:
            return 0

        value = float(match.group(1))
        unit = match.group(2)

        if unit == 'K':
            return value / 1024
        elif unit == 'M':
            return value
        elif unit == 'G':
            return value * 1024
        elif unit == 'T':
            return value * 1024 * 1024

        return value / (1024 * 1024)  # 假设是字节

    def scan_app_cache(self) -> List[Dict]:
        """扫描应用缓存"""
        caches = []

        # /data/data/*/cache
        success, output = self.run_adb_su('du -sh /data/data/*/cache 2>/dev/null')
        if success and output:
            for line in output.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        size = parts[0]
                        path = parts[1]
                        # 提取包名
                        match = re.search(r'/data/data/([^/]+)/cache', path)
                        if match:
                            package = match.group(1)
                            caches.append({
                                "package": package,
                                "size": size,
                                "size_mb": self.parse_size_to_mb(size),
                                "path": path,
                                "type": "data_cache"
                            })

        # 按大小排序
        caches.sort(key=lambda x: x.get("size_mb", 0), reverse=True)

        return caches[:30]  # 返回前 30 个

    def scan_system_logs(self) -> List[Dict]:
        """扫描系统日志"""
        logs = []

        log_paths = [
            ("/data/anr/", "ANR 日志"),
            ("/data/tombstones/", "Tombstone 崩溃日志"),
            ("/data/system/dropbox/", "Dropbox 错误日志"),
            ("/data/local/tmp/", "临时文件")
        ]

        for path, name in log_paths:
            success, output = self.run_adb_su(f'du -sh {path} 2>/dev/null')
            if success and output:
                parts = output.split('\t')
                size = parts[0] if parts else "0"
                logs.append({
                    "name": name,
                    "size": size,
                    "size_mb": self.parse_size_to_mb(size),
                    "path": path
                })

        return logs

    def scan_app_logs(self) -> List[Dict]:
        """扫描应用日志"""
        logs = []

        # debug_log 目录
        success, output = self.run_adb_su('find /data/data -type d -name debug_log 2>/dev/null')
        if success and output:
            debug_dirs = output.split('\n')
            for dir_path in debug_dirs[:20]:
                if dir_path.strip():
                    success2, output2 = self.run_adb_su(f'du -sh {dir_path} 2>/dev/null')
                    if success2 and output2:
                        parts = output2.split('\t')
                        size = parts[0] if parts else "0"
                        logs.append({
                            "type": "debug_log",
                            "size": size,
                            "size_mb": self.parse_size_to_mb(size),
                            "path": dir_path
                        })

        # 日志文件统计
        success, output = self.run_adb_su('find /data/data -name *.log -type f 2>/dev/null | wc -l')
        log_count = int(output.strip()) if success and output.strip().isdigit() else 0

        # xlog 文件统计
        success, output = self.run_adb_su('find /data/data -name *.xlog -type f 2>/dev/null | wc -l')
        xlog_count = int(output.strip()) if success and output.strip().isdigit() else 0

        return {
            "debug_logs": logs[:20],
            "log_file_count": log_count,
            "xlog_file_count": xlog_count
        }

    def scan_download_residue(self) -> Dict:
        """扫描下载残留"""
        result = {
            "total_size": "0",
            "total_mb": 0,
            "pending_files": [],
            "hidden_dirs": []
        }

        # Download 目录大小
        success, output = self.run_adb_su('du -sh /sdcard/Download/ 2>/dev/null')
        if success and output:
            parts = output.split('\t')
            result["total_size"] = parts[0] if parts else "0"
            result["total_mb"] = self.parse_size_to_mb(result["total_size"])

        # .pending 文件
        success, output = self.run_adb_su('ls -lh /sdcard/Download/.* 2>/dev/null')
        if success and output:
            lines = output.split('\n')
            for line in lines:
                if '.pending-' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        result["pending_files"].append({
                            "size": parts[4],
                            "name": parts[-1]
                        })

        return result

    def scan_temp_files(self) -> Dict:
        """扫描临时文件"""
        result = {
            "tmp_count": 0,
            "temp_count": 0,
            "part_count": 0,
            "wechat_tmp_mb": 0
        }

        # 统计各类临时文件
        for ext, key in [('"*.tmp"', 'tmp_count'), ('"*.temp"', 'temp_count'), ('"*.part"', 'part_count')]:
            success, output = self.run_adb_su(f'find /sdcard -name {ext} 2>/dev/null | wc -l')
            if success and output.strip().isdigit():
                result[key] = int(output.strip())

        # 微信临时文件
        success, output = self.run_adb_su('du -sh /sdcard/Android/data/com.tencent.mm/MicroMsg/.tmp 2>/dev/null')
        if success and output:
            parts = output.split('\t')
            result["wechat_tmp_mb"] = self.parse_size_to_mb(parts[0] if parts else "0")

        return result

    def scan_empty_dirs(self) -> int:
        """统计空目录数量"""
        success, output = self.run_adb_su('find /sdcard -type d -empty 2>/dev/null | wc -l')
        if success and output.strip().isdigit():
            return int(output.strip())
        return 0

    def full_scan(self) -> Dict:
        """执行完整扫描"""
        print("🔍 开始扫描手机存储...")

        result = {
            "device": None,
            "storage": None,
            "app_cache": [],
            "system_logs": [],
            "app_logs": {},
            "download_residue": {},
            "temp_files": {},
            "empty_dirs": 0
        }

        # Step 1: 检查连接
        print("  📱 检查设备连接...")
        device_info = self.check_connection()
        result["device"] = device_info

        if not device_info["connected"]:
            print(f"  ❌ {device_info['error']}")
            return result

        print(f"  ✅ 设备已连接: {device_info['device_id']}")
        print(f"  {'✅ Root 权限可用' if device_info['has_root'] else '⚠️ 无 Root 权限'}")

        # Step 2: 存储空间
        print("  💾 获取存储空间信息...")
        result["storage"] = self.get_storage_info()
        if result["storage"]["total"]:
            print(f"     总容量: {result['storage']['total']}, 已用: {result['storage']['used']}, 可用: {result['storage']['available']}")

        # Step 3: 应用缓存
        print("  🗂️ 扫描应用缓存...")
        result["app_cache"] = self.scan_app_cache()
        total_cache_mb = sum(c.get("size_mb", 0) for c in result["app_cache"])
        print(f"     找到 {len(result['app_cache'])} 个应用缓存, 总计约 {total_cache_mb:.0f} MB")

        # Step 4: 系统日志
        print("  📋 扫描系统日志...")
        result["system_logs"] = self.scan_system_logs()
        total_logs_mb = sum(l.get("size_mb", 0) for l in result["system_logs"])
        print(f"     系统日志总计约 {total_logs_mb:.0f} MB")

        # Step 5: 应用日志
        print("  📝 扫描应用日志...")
        result["app_logs"] = self.scan_app_logs()
        debug_logs_mb = sum(l.get("size_mb", 0) for l in result["app_logs"].get("debug_logs", []))
        print(f"     debug_log: {debug_logs_mb:.0f} MB, 日志文件: {result['app_logs'].get('log_file_count', 0)} 个, xlog: {result['app_logs'].get('xlog_file_count', 0)} 个")

        # Step 6: 下载残留
        print("  📥 扫描下载残留...")
        result["download_residue"] = self.scan_download_residue()
        print(f"     Download 目录: {result['download_residue']['total_size']}, 残留文件: {len(result['download_residue']['pending_files'])} 个")

        # Step 7: 临时文件
        print("  🗑️ 扫描临时文件...")
        result["temp_files"] = self.scan_temp_files()
        print(f"     tmp: {result['temp_files']['tmp_count']}, temp: {result['temp_files']['temp_count']}, part: {result['temp_files']['part_count']}")

        # Step 8: 空目录
        print("  📁 统计空目录...")
        result["empty_dirs"] = self.scan_empty_dirs()
        print(f"     空目录: {result['empty_dirs']} 个")

        print("\n✅ 扫描完成！")

        return result


def main():
    """主函数"""
    scanner = ADBScanner()
    result = scanner.full_scan()

    # 输出 JSON
    output_path = "/tmp/adb_scan.json"
    if sys.platform == "win32":
        output_path = os.path.join(os.environ.get("TEMP", "."), "adb_scan.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n📄 扫描结果已保存到: {output_path}")


if __name__ == "__main__":
    import os
    main()
