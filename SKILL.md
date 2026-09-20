---
name: kindle-desk
description: Build, customize and troubleshoot a jailbroken Kindle desk dashboard with Todoist task completion, daily shuffled vocabulary, twice-daily weather and reversible upside-down display. Use for Kindle desktop screens and this dashboard's USB deployment, not general ebook management or an automatic jailbreak.
---

# Kindle Desk

把已具备脚本启动能力的 Kindle 做成可长期维护的电子墨水桌面屏。用中文与中文用户沟通；先查现有设备、项目和日志，沿用已验证的实现。

## 先确定工作入口

- 维护已有项目：定位 `package/dashboard/direct-client.lua` 或请用户给项目目录。运行 `scripts/inspect_project.py --project <目录>`；连接设备时可加 `--device <挂载根目录>`。检查结果只读，不输出凭据和任务内容。
- 新设备或新项目：读 [references/setup.md](references/setup.md)。`scripts/stage_project.py --destination <新目录>` 可复制附带的参考源码；它不是完整刷机包，仍需配置、字体、词库、日期素材和设备能力验证。
- 显示、倒置、常亮、触摸问题：读 [references/device.md](references/device.md)。
- 待办、天气或单词调度：读 [references/sync.md](references/sync.md)。
- 视觉调整和对外介绍：读 [references/design-and-sharing.md](references/design-and-sharing.md)。

## 不可丢失的实现约束

实机基线是 Paperwhite 3 / 5.10.3 / 1072×1448。不要把屏幕尺寸、旋转值、触摸设备号推广到其他型号。附带代码是可复用参考，不是任意 Kindle 的即插即用固件。

默认参考布局是复古咖啡馆：每日单词、纪念日、时钟、公历/农历/节气、咖啡热气、今明天气、七行待办、双猫与电量。保留当前用户已确认的选择；新项目自行配置纪念日、城市、词库、时间、方向和配色。

已授权范围内连续完成读取、备份、编辑、验证和部署，不因本 skill 额外请求逐步批准。设备变更仍遵守实际工具权限；不要推断此用户的授权适用于其他用户。

待办状态、完成 outbox、项目凭据及天气缓存是运行数据，不能用示例文件覆盖。只部署本次变更文件，写前备份，写后 SHA256 核对。所有 shell 文件使用 LF。

不要读取/展示/打包真实 token、curl.conf、任务缓存、私密日志、用户截图或已提取的商业字体。分享源码不包含第三方 GRE 全词库；导入前核对其使用条件。

## 交付标准

按变更运行相关测试：Lua **5.1**、shell 语法、定时边界、断网缓存与重试、重复启动方向、触摸任意行、图像尺寸和文字溢出。无需为纯排版小改新增镜像实现测试。

部署后明确区分「本机测试通过」「USB 文件校验通过」「Kindle 实机验证通过」。USB 写入不能证明设备联网、UI 正确或长时间稳定。指导用户安全拔线打开 Desk Direct；通过设备日志与实际屏幕确认结果。

本 skill 不自动发布社交内容、邀请协作者、购买服务，也不提供通用自动越狱。天气更新频率、网络轮询、动画频率与电池续航分开解释。
