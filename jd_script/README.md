# JDGuoBuScript
京东抢购自动化脚本
## 功能特点
- 自动登录京东并保存Cookie
- 精确时间控制抢购
- 支持自定义抢购时间
- 网络时间自同步
## 使用方法
### 保存Cookie
```bash
python jd_cli.py save_cookie
```
### 运行抢购脚本
```bash
# 默认时间 09:00:00
python jd_cli.py run
# 指定时间
python jd_cli.py run 09:00:00
```
## 注意事项
- 首次使用需要手动登录保存Cookie
- 建议提前几分钟运行脚本
