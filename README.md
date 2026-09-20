# Kindle Desk ☕

把旧 Kindle 变成一块受《双峰》咖啡馆启发的电子墨水桌面屏。

**这是给 AI 助手使用的 skill、参考源码与维护工具。当前实机基线为已越狱的 Kindle Paperwhite 3，固件 5.10.3，1072×1448；不是通用越狱工具或一键安装固件。**

<img src="docs/images/01-cover.png" alt="复古咖啡馆风格的 Kindle 桌面屏界面示意" width="460">

## 它能做什么

- **共享待办**：手机浏览器使用 Todoist 共享项目；Kindle 轮询获取待办，轻触完成后同步回清单。通常约20–40秒，受网络影响。
- **每日单词**：北京时间每天09:00换词，固定乱序，同轮不重复，同日重启不重抽。
- **定时天气**：每天09:00、17:00更新北京海淀今明预报，提供带伞、添衣提示；断网保留缓存并重试。
- **日常仪式感**：大时钟、公历、农历、节气、纪念日、咖啡热气动画、小猫与电量。
- **倒置常驻**：充电口朝上，同步转换触摸坐标；退出恢复系统界面、方向和休眠设置。

Kindle 直接访问 API，电脑不必常开，也不必与 Kindle 连接同一个无线网络。日常使用需要设备联网；动画和 Wi-Fi 会耗电，常驻推荐稳定墙充。

## 使用这个 skill

1. 从 GitHub 下载本仓库 ZIP 并解压。
2. 将包含 `SKILL.md` 的目录命名为 `kindle-desk`，放入 `~/.codex/skills/`（Windows 通常为 `%USERPROFILE%\.codex\skills\`）。
3. 在新的 Codex 对话中输入：

   > 使用 $kindle-desk 检查我的 Kindle 桌面屏项目，并帮我完成配置。

4. 让助手先读取 [SKILL.md](SKILL.md) 和 [设备准备说明](references/setup.md)，确认型号、依赖和素材，再进行部署。

也可直接阅读参考资料，独立复用源码。不要将整个仓库直接复制进 Kindle 并运行所有历史入口。

## 附带的工具

只读检查现有项目，不输出密钥和任务内容：

```sh
python scripts/inspect_project.py --project /path/to/your/project
```

将参考源码复制到一个尚不存在的新目录：

```sh
python scripts/stage_project.py --destination /path/to/new/project
```

复制后仍需配置设备、字体、词库、Todoist、天气和日期素材。参考构建器保留部分 Windows 路径及原项目目录约定，使用前按说明调整。

## 仓库结构

| 目录 | 内容 |
| --- | --- |
| `SKILL.md` | AI 助手的工作入口与关键约束 |
| `agents/` | skill 的显示信息 |
| `references/` | 配置、设备、同步、设计与分享说明 |
| `scripts/` | 只读检查与新项目复制工具 |
| `assets/reference-project/` | Lua/shell运行源码、参考构建器和测试 |
| `docs/images/` | 已标注为示意的展示图 |

## 实现状态与适用范围

本项目来自一台 PW3 的实际迭代。待办点击及同步、常驻显示等已有使用反馈；倒置与每日词汇有程序测试。天气已通过 Lua5.1 测试并写入设备，**截至2026-09-20，仍待 Kindle 联网取天气的实机验收**。本机测试、USB文件核验不等于所有设备上的端到端验证。

参考日期素材范围为2026-09-01至2027-10-05，使用前应生成当前所需范围。其他机型需要重新确认分辨率、原生旋转值、触摸输入和系统服务。

## 费用与隐私

方案不租云服务器，使用 Todoist 与 Open-Meteo 现有免费额度；新部署请核对最新条款。Open-Meteo 的这里所用免费方案面向非商业用途。设备、网络和 AI 工具费用不在免费服务承诺之内。

仓库不含账号token、真实任务、设备运行日志、商业字体文件、第三方完整GRE词库或越狱工具。原个人配置中的7211词不是本仓库附赠词库，请自行导入有权使用的词表。

不支持直接读取普通个人微信群；共享待办采用 Todoist。咖啡动画是局部逐帧刷新，不代表 Kindle 原生支持任意 GIF。

## 来源与说明

- [Todoist](https://www.todoist.com/)：共享待办及官方 API。
- [Open-Meteo](https://open-meteo.com/)：天气预报；界面保留来源署名。
- [FBInk](https://github.com/NiLuJe/FBInk)：设备绘图依赖，本仓库不分发其二进制。
- 原词库来源记录：[kajweb/dict](https://github.com/kajweb/dict)，使用前自行核对相关许可。

视觉主题为个人创作，受《双峰》咖啡馆启发，非官方联名。本仓库没有附加统一开源许可证；公开可见不代表第三方素材或品牌获得额外授权。
