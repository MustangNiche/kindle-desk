# PW3设备操作与问题定位

## 运行与恢复

共享锁 `/tmp/kindle-desk-always.lock`，资源 `/mnt/us/dashboard`，启动入口 `/mnt/us/documents`。Desk Direct 与 Desk Upside Down 为相同倒置实现；Desk Upright 为明确正向入口。旧 Desk Preview / Live / Todo 不应作为新部署入口。

进入前保存 preventScreenSaver 原值，设1且回读。暂时禁用pillow、SIGSTOP awesome以避免约6分钟后系统状态栏重画；退出与独立watchdog负责CONT、pillow enable、恢复休眠与方向。不要停止volumd。不要仅删除锁而放任旧进程运行；异常时先检查进程/日志并恢复UI。

联网前检查 ota-update 已停止，暂停已运行的 otaupd/otav3并记原状态。退出先关闭本次Wi-Fi，再恢复原先运行的OTA服务。不要把这个临时生命周期改成无提示永久禁用或固件升级。

FBInk可来自 `/var/local/kmc/bin/fbink`，备用 `/mnt/us/libkh/bin/fbink`；FAT上直接执行可能失败，已有启动器会复制到/tmp再执行。shell及positions.conf须LF，CRLF会让坐标携带回车而绘制失败。

## 固定倒置与触摸

本机 native normal=3、upside=1，固定目标值，不用当前方向+2；否则异常退出后再启动会翻回正向。screen-rotation.sh在退出/watchdog恢复3。

倒置触摸转换 `(1071-x,1447-y)`，/dev/input/event1的32位little-endian input_event、ABS53/54。其他机型重新检测。触摸reader保持同一evdev描述符读取，过滤拖动和旧动作；依赖屏幕视图UUID与不可变行映射，避免点击更新中的错误任务。

七行待办首行热区y968..1016、每行48px；分页点条数，退出点左下。上下倒置必须同时改画面与触摸坐标。实际任意第一/中间/最后行都要验证，不能只测第一行。

## 诊断顺序

- 闪退：查看当前入口的 LIVE_EXIT、unsupported device date、字体/FBInk、LF和素材缺失，勿反复重启掩盖日志。
- 又正向：先核对打开的入口、UPSIDE_DOWN_REVISION与rotate值，GRE更新不应覆盖启动器。
- 系统栏重现：核对防休眠回读、pillow/awesome生命周期、watchdog是否提前恢复，不通过不断全屏重画掩盖。
- 几天后黑屏：看BATTERY轨迹与结束时间。此台机曾100%到0约10小时（动画+Wi-Fi），不宣传多周续航。常驻建议墙充；防休眠不是把前光亮度固定为最大。改变天气频率不会自动降低咖啡逐秒刷新/待办轮询耗电。
- 热气不动：是6帧局部FBInk绘制而非原生GIF播放器，查蒸汽RESULT、帧路径及刷新波形。宣传可称热气动画，不能称设备通用GIF支持。

设备日志可能含私密任务操作，不整包公开。诊断提取状态码和时间；任务内容与token不回显。备份后只替换变更文件，SHA256核验；保持state/outbox/config缓存。
