# MeetingShot v0.4.1 Windows

修复 Windows 电脑上“程序能打开，但点击开始截图没有反应”的问题。

## 本版修复
- 保存目录固定优先使用 `C:\Users\<用户名>\Pictures\MeetingShots`
- 点击开始时同步验证截图API和磁盘写入
- 如果启动失败，直接弹窗显示真实错误
- 后台截图失败时不再静默
- 自动生成 `MeetingShot-error.log`
- 成功开始后立刻保存第一张截图，并明确显示“正在截图”
- 保留 v0.4 原有帧差检测、30秒兜底与 pHash 去重

## 测试时
请先完整解压 GitHub Actions 下载的 ZIP，再运行 `MeetingShot.exe`。
