# 学期推进流 exe 使用说明（全员版）

**程序**：`tools/学期推进流_王启龙.exe`（5 人通用，加 `--member 姓名` 即成员模式）｜**源码**：`tools/semester_flow.py`

## 三条铁律

1. **exe 放在仓库 tools/ 里运行**，不要单独拷出去（找不到仓库=核验全部跳过、进度脱钩）。
2. 第一次运行被 Windows 拦：**更多信息 → 仍要运行**。
3. 命令行用法先 `cd tools/` 再敲命令。

## 每周就这几个命令

| 谁用 | 命令 | 作用 |
|---|---|---|
| 全员 | `学期推进流_王启龙.exe`（双击） | 本周看板 |
| 负责人 | `学期推进流_王启龙.exe check 周号 --deep` | 核验第 N 周 |
| 负责人 | `学期推进流_王启龙.exe report 周号` | 生成周报 md |
| 成员 | `学期推进流_王启龙.exe --member 姓名 check 周号` | 核验自己的练习 |
| 成员 | `学期推进流_王启龙.exe --member 姓名 report 周号` | 生成自己的周报 |

- 没装 Python 的成员直接用上面 exe 命令（姓名＝宁显泷/衣思淼/代维斯丹/王散曼）；
  装了 Python 的等价写法：`python tools/semester_flow.py --member 姓名 check 周号`。
- 练习骨架已在 `learning/<姓名>/` 里；被误删时 `--member 姓名 scaffold 周号` 重新生成。
- 服务器上跑通的练习，本机核验不过时补录：`--member 姓名 record 编号 pass "服务器实测值"`。

## 进度存哪

- exe/脚本：`learning/<姓名>/flow_state.json`（每人一份）
- 打卡.html：浏览器 localStorage——**两者独立**，日常打卡以打卡页为主，exe 管 check/report。

（重新打包命令：`cd tools && python -m PyInstaller --onefile --console --name semester_flow --distpath . --workpath build --specpath build semester_flow.py`，然后把 semester_flow.exe 改名回 学期推进流_王启龙.exe）
