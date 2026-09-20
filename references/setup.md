# 建立项目与维护边界

## 附带什么

`assets/reference-project` 包含此次实现的 Lua/shell 运行源码、三个启动入口、设计与素材构建脚本、相关测试、设计预览和农历日期表。它不含任何用户凭据、真实任务、运行日志、第三方词库、字体文件、FBInk 二进制或完整预渲染素材。

脚本保留原项目的目录契约；部分构建器仍有 Windows 字体路径、F: 盘、本地测试依赖路径及纪念日/坐标/日期常量。这些是要检查并调整的参考代码，不能对新设备盲目执行。现有项目维护优先修改原项目，避免用快照覆盖更新。

## 新项目流程

1. 确认设备型号、固件、屏幕分辨率、已越狱且能从书库运行 `.sh`。本 skill 不执行越狱，不默认让其他型号运行 PW3 服务控制命令。
2. 使用 stage_project.py 复制到不存在的新目录。明确设备挂载位置，不假定 F:。先完成离线绘图与正常退出验证。
3. 需要 Pillow；提取本机已授权字体时用 fontTools；本机测试需要带 Lua5.1 模块的 lupa。不要把本机商业字体复制进公开包。设备需要 Lua5.1+cjson、curl+CA、OpenType 版 FBInk。通过文件与日志确认，不能把桌面可用等同于设备可用。
4. 修改 build_preview.py / build_live_assets.py 的字体、纪念日与日期覆盖。参考 lunar-dates.json 仅涵盖2026-09-01至2027-10-05；超出会退出。新范围用 .NET ChineseLunisolarCalendar 或可靠农历库重新生成；节气采用太阳黄经近似算法，覆盖年也必须扩展。
5. 原素材生成链：build_preview → build_live_assets → build_always_on（含battery）→ build_todo_launcher → build_direct → build_upside_down。**build_direct 旧入口读取 private/todoist.json、private/cloud-test/curl.conf 和旧设备 cloud-test/tasks.json；新项目先将其改成当前用户配置输入及空 results 或经验证的本项目响应，不能复用历史凭据。** 启动器快照已附带，不必为小改重走整条链。
6. direct目录需base/tasks-empty/checkbox/connecting/online/offline/pending PNG，song.ttf、ca.pem、project.json、curl.conf、initial.json。空列表初始值可为 `{"results":[]}`。project.json为 `{"project":"用户选择的项目ID"}`。在私密本地配置工具中输入个人 API token，不把 token 放在命令行、对话或仓库。curl.conf仅供Todoist域名请求；核对TLS证书，不关闭验证。
7. 词库用 `word|pos|中文释义` 的 UTF-8 文本，去重后 build_gre 生成卡片与排列 manifest。新词库不强制7211数量。分享版不含此前第三方词库，来源记录见 sync.md。
8. 天气需生成 weather/blank.png 和本地合法字体 serif.ttf。首次可不放 cache.json，由设备下载；参考 build_weather.py 的桌面初始预报读取是可选的，移除/改写该依赖后运行。设置经纬度和北京时间调度，其他时区需同时改调度、日期与API参数。
9. 使用 inspect_project 检查依赖；按设备验证绘图、触摸、方向、退出恢复，再接Todoist和天气；最后进行跨09/17与跨日测试。

## 免费与联网

参考方案不租服务器：Kindle 自己调用 Todoist / Open-Meteo，电脑只用于配置。日常手机浏览器可管理共享项目，无需额外安装手机 App。微信普通个人群不在已实现链路中；不要宣传为微信群自动读取。

此前使用 Todoist Beginner 免费项目及协作额度、Open-Meteo 免费非商业接口。提供新用户方案时重新核对当前额度/条款，不开试用、不假定商业用途免费；AI工具、硬件与已有网络不属于本项目承诺的免费服务。

2.4GHz 是此设备约束，电脑可以保持自己的办公网络。若Kindle能直接访问公网API，电脑无需连接Guest，也无需常开。不要改用户办公网络或绕过Guest隔离。
