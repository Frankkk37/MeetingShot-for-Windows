# MeetingShot-for-Windows v0.4

Windows版目标：
v0.3 自动变化检测截图 + v0.4 pHash去重输出。

## 功能
- 每秒低清画面检测
- 中心区域变化判断
- 稳定后高清截图
- 30秒兜底截图
- 原始截图永久保存
- pHash智能去重
- 精选PDF输出

## 运行
开发环境：
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

## 打包
安装 pyinstaller 后：
pyinstaller --noconsole --onefile --name MeetingShot main.py

生成：
dist/MeetingShot.exe
