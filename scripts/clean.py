#!/usr/bin/env python3
"""
ADB Cleaner - Android 手机垃圾清理脚本
根据扫描结果执行清理操作
"""

import subprocess
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ADBCleaner:
    """ADB 手机垃圾清理器"""

    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self.device_id = None
        self.has_root = False
        self.log_file = None
        self.cleaned_items = []

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

    def init_log(self, work_dir: str):
        """初始化日志文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(work_dir, f"cleanup_log_{timestamp}.md")
        self.log_file = open(log_path, 'w', encoding='utf-8')
        self.log_write(f"# 手机清理日志\n\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n---\n\n")

    def log_write(self, content: str):
        """写入日志"""
        if self.log_file:
            self.log_file.write(content)
            self.log_file.flush()

    def close_log(self):
        """关闭日志文件"""
        if self.log_file:
            self.log_file.close()
            self.log_file = None

    def check_connection(self) -> bool:
        """检查连接和权限"""
        success, output = self.run_adb("devices")
        if not success:
            print("❌ ADB 命令执行失败")
            return False

        lines = output.split('\n')
        for line in lines[1:]:
            if line.strip() and 'device' in line:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == 'device':
                    self.device_id = parts[0]
                    break

        if not self.device_id:
            print("❌ 未检测到已连接的设备")
            return False

        # 检查 root
        success, output = self.run_adb("shell \"su -c 'id'\"")
        if success and 'uid=0' in output:
            self.has_root = True
            print(f"✅ 设备已连接: {self.device_id}")
            print("✅ Root 权限可用")
            return True
        else:
            print("❌ 无 Root 权限")
            return False

    def get_storage_info(self) -> Dict:
        """获取存储空间信息"""
        success, output = self.run_adb('shell "df -h /data"')
        if success:
            lines = output.split('\n')
            for line in lines:
                if '/dev/block' in line or line.startswith('/dev/'):
                    parts = line.split()
                    if len(parts) >= 5:
                        return {
                            "total": parts[1],
                            "used": parts[2],
                            "available": parts[3],
                            "use_percent": parts[4]
                        }
        return {}

    def clean_app_cache(self, packages: List[str] = None, dry_run: bool = False) -> int:
        """清理应用缓存

        Args:
            packages: 要清理的包名列表，None 表示清理所有
            dry_run: 仅模拟，不实际执行

        Returns:
            清理的项目数量
        """
        print("\n🧹 清理应用缓存...")

        if packages:
            # 清理指定应用
            for pkg in packages:
                cmd = f'rm -rf /data/data/{pkg}/cache/*'
                if dry_run:
                    print(f"  [模拟] {cmd}")
                else:
                    success, _ = self.run_adb_su(cmd)
                    if success:
                        print(f"  ✅ {pkg}")
                        self.cleaned_items.append(("app_cache", pkg, cmd))
        else:
            # 清理所有应用缓存
            cmd = 'find /data/data -type d -name cache -exec rm -rf {}/* \\;'
            if dry_run:
                print(f"  [模拟] 清理所有应用缓存")
            else:
                success, _ = self.run_adb_su(cmd)
                if success:
                    print("  ✅ 所有应用缓存已清理")
                    self.cleaned_items.append(("app_cache", "all", cmd))

        return len([x for x in self.cleaned_items if x[0] == "app_cache"])

    def clean_system_logs(self, dry_run: bool = False) -> int:
        """清理系统日志"""
        print("\n🧹 清理系统日志...")

        log_paths = [
            ("/data/anr/*", "ANR 日志"),
            ("/data/tombstones/*", "Tombstone 崩溃日志"),
            ("/data/system/dropbox/*", "Dropbox 错误日志"),
            ("/data/local/tmp/*", "临时文件")
        ]

        count = 0
        for path, name in log_paths:
            cmd = f'rm -rf {path}'
            if dry_run:
                print(f"  [模拟] 清理 {name}")
            else:
                success, _ = self.run_adb_su(cmd)
                if success:
                    print(f"  ✅ {name}")
                    self.cleaned_items.append(("system_log", name, cmd))
                    count += 1

        return count

    def clean_app_logs(self, dry_run: bool = False) -> int:
        """清理应用日志"""
        print("\n🧹 清理应用日志...")

        commands = [
            ("find /data/data -type d -name debug_log -exec rm -rf {}/* \\;", "debug_log 目录"),
            ("find /data/data -name *.log -type f ! -path \"*/leveldb/*\" ! -path \"*/shared_proto_db/*\" -delete", "日志文件"),
            ("find /data/data -name *.xlog -type f -delete", "xlog 文件")
        ]

        count = 0
        for cmd, name in commands:
            if dry_run:
                print(f"  [模拟] 清理 {name}")
            else:
                success, _ = self.run_adb_su(cmd)
                if success:
                    print(f"  ✅ {name}")
                    self.cleaned_items.append(("app_log", name, cmd))
                    count += 1

        return count

    def clean_download_residue(self, dry_run: bool = False) -> int:
        """清理下载残留"""
        print("\n🧹 清理下载残留...")

        commands = [
            ("rm -f /sdcard/Download/.pending-*", ".pending 文件"),
            ("rm -rf /sdcard/Download/.[!.]*", "隐藏目录")
        ]

        count = 0
        for cmd, name in commands:
            if dry_run:
                print(f"  [模拟] 清理 {name}")
            else:
                success, _ = self.run_adb_su(cmd)
                if success:
                    print(f"  ✅ {name}")
                    self.cleaned_items.append(("download_residue", name, cmd))
                    count += 1

        return count

    def clean_temp_files(self, dry_run: bool = False) -> int:
        """清理临时文件"""
        print("\n🧹 清理临时文件...")

        commands = [
            ("find /sdcard -name \"*.tmp\" -type f -delete", "*.tmp 文件"),
            ("find /sdcard -name \"*.temp\" -type f -delete", "*.temp 文件"),
            ("find /sdcard -name \"*.part\" -type f -delete", "*.part 文件"),
            ("rm -rf /sdcard/Android/data/com.tencent.mm/MicroMsg/.tmp/*", "微信临时文件")
        ]

        count = 0
        for cmd, name in commands:
            if dry_run:
                print(f"  [模拟] 清理 {name}")
            else:
                success, _ = self.run_adb_su(cmd)
                if success:
                    print(f"  ✅ {name}")
                    self.cleaned_items.append(("temp_file", name, cmd))
                    count += 1

        return count

    def clean_empty_dirs(self, dry_run: bool = False) -> int:
        """清理空目录"""
        print("\n🧹 清理空目录...")

        cmd = "find /sdcard -type d -empty -delete"
        if dry_run:
            print("  [模拟] 清理空目录")
            return 0
        else:
            success, _ = self.run_adb_su(cmd)
            if success:
                print("  ✅ 空目录已清理")
                self.cleaned_items.append(("empty_dir", "all", cmd))
                return 1
        return 0

    def generate_report(self, work_dir: str, storage_before: Dict, storage_after: Dict):
        """生成清理报告"""
        timestamp = datetime.now().strftime("%Y%m%d")
        report_path = os.path.join(work_dir, f"phone_cleanup_{timestamp}.md")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 手机清理报告\n\n")
            f.write(f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")

            # 存储对比
            f.write("## 清理前后对比\n\n")
            f.write("| 项目 | 清理前 | 清理后 | 变化 |\n")
            f.write("|------|--------|--------|------|\n")
            f.write(f"| 已使用 | {storage_before.get('used', '-')} | {storage_after.get('used', '-')} | - |\n")
            f.write(f"| 可用 | {storage_before.get('available', '-')} | {storage_after.get('available', '-')} | - |\n")
            f.write(f"| 使用率 | {storage_before.get('use_percent', '-')} | {storage_after.get('use_percent', '-')} | - |\n\n")

            # 清理详情
            f.write("## 清理详情\n\n")
            for item in self.cleaned_items:
                f.write(f"- **{item[0]}**: {item[1]}\n")
                f.write(f"  ```bash\n  {item[2]}\n  ```\n\n")

            # 命令汇总
            f.write("## 清理命令汇总\n\n")
            f.write("```bash\n")
            for item in self.cleaned_items:
                f.write(f"# {item[1]}\n")
                f.write(f"adb shell \"su -c '{item[2]}'\"\n\n")
            f.write("```\n")

        print(f"\n📄 清理报告已保存到: {report_path}")
        return report_path

    def full_clean(self, work_dir: str, dry_run: bool = False):
        """执行完整清理"""
        print("=" * 50)
        print("🧹 ADB Cleaner - Android 手机深度清理")
        print("=" * 50)

        # 检查连接
        if not self.check_connection():
            return False

        # 初始化日志
        self.init_log(work_dir)

        # 记录清理前状态
        storage_before = self.get_storage_info()
        print(f"\n📊 清理前存储: {storage_before.get('used', '-')} 已用, {storage_before.get('available', '-')} 可用")

        # 执行清理
        self.clean_app_cache(dry_run=dry_run)
        self.clean_system_logs(dry_run=dry_run)
        self.clean_app_logs(dry_run=dry_run)
        self.clean_download_residue(dry_run=dry_run)
        self.clean_temp_files(dry_run=dry_run)
        self.clean_empty_dirs(dry_run=dry_run)

        # 记录清理后状态
        storage_after = self.get_storage_info()
        print(f"\n📊 清理后存储: {storage_after.get('used', '-')} 已用, {storage_after.get('available', '-')} 可用")

        # 生成报告
        report_path = self.generate_report(work_dir, storage_before, storage_after)

        # 关闭日志
        self.close_log()

        print("\n" + "=" * 50)
        print("✅ 清理完成！")
        print("=" * 50)

        return True


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="ADB Cleaner - Android 手机深度清理")
    parser.add_argument("--dry-run", action="store_true", help="仅模拟，不实际执行清理")
    parser.add_argument("--work-dir", default=".", help="工作目录，用于保存日志和报告")
    args = parser.parse_args()

    cleaner = ADBCleaner()
    cleaner.full_clean(work_dir=args.work_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
