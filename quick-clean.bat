@echo off
chcp 65001 >nul
echo ========================================
echo   ADB Cleaner v2.0 - 快速清理
echo ========================================
echo.

echo [1/3] 检查设备连接...
adb devices
if errorlevel 1 (
    echo ? ADB 未安装或设备未连接
    pause
    exit /b 1
)

echo.
echo [2/3] 检查 Root 权限...
adb shell "su -c 'id'" | findstr "uid=0" >nul
if errorlevel 1 (
    echo ? 无 Root 权限
    pause
    exit /b 1
)

echo ? Root 权限可用
echo.

echo [3/3] 开始扫描垃圾文件...
echo.
echo 应用缓存：
adb shell "su -c 'du -sh /data/data/*/cache 2>/dev/null | sort -rh | head -10'"

echo.
echo 系统日志：
adb shell "su -c 'du -sh /data/anr/ /data/tombstones/ 2>/dev/null'"

echo.
echo ========================================
echo   扫描完成！是否执行清理？
echo ========================================
set /p confirm="输入 Y 确认清理: "

if /i "%confirm%"=="Y" (
    echo.
    echo ?? 开始清理...
    adb shell "su -c 'rm -rf /data/anr/* /data/tombstones/* /data/local/tmp/*'"
    echo ? 系统日志已清理
    
    adb shell "su -c 'find /sdcard -type d -empty -delete 2>/dev/null'"
    echo ? 空目录已清理
    
    echo.
    echo ? 清理完成！
) else (
    echo 已取消
)

pause