# 学期推进流 exe 使用说明（全员版 v1.1）

**程序**：`tools/学期推进流_王启龙.exe`（约 8MB，PyInstaller 单文件打包，无需安装 Python 即可运行；名字虽带"王启龙"，**加 `--member` 参数后 5 名成员都能用**）
**源码**：`tools/semester_flow.py`（修改源码后重新打包的命令见文末）

## 〇、最重要的三件事（先读）

1. **exe 必须放在仓库里用**（默认在 `tools/`，不要单独把它拷出去）。它靠仓库里的 `run_all.py` 定位数据；单独下载到桌面/下载夹运行时，所有自动核验都会[跳过]、进度也会存到 exe 旁边的一个孤立文件里——看起来就是"不生效"。换了位置就加 `--repo 仓库路径`。
2. **第一次运行被 Windows 拦（"已保护你的电脑"）**：无签名的 PyInstaller 程序都会被 SmartScreen 提示，点"更多信息 → 仍要运行"即可；杀毒软件误报时加白名单。
3. **exe 的进度和打卡.html 的进度是两套**：exe 存 `learning/<姓名>/flow_state.json`，打卡页存浏览器 localStorage，互不同步（各自都能导出留痕）。日常打卡以打卡.html 为主，exe 用于练习核验（check）和周报（report）。

## 一、三种用法

1. **双击运行**：显示"本周看板"（自动按日期定位第几周），看完按回车退出。
2. **负责人命令行**（在 cmd / PowerShell / Git Bash 中，先 `cd tools/`）：

```
学期推进流_王启龙.exe              本周看板（同双击）
学期推进流_王启龙.exe plan         学期16周总览 + 里程碑清单
学期推进流_王启龙.exe week 3       查看第3周完整卡片
学期推进流_王启龙.exe next         下一个该做的事
学期推进流_王启龙.exe check        本周自动核验（快速）
学期推进流_王启龙.exe check 1     第1周自动核验
学期推进流_王启龙.exe check 1 --deep   深度核验（会真实运行 run_all.py / verify.py）
学期推进流_王启龙.exe check all --deep 全学期核验
学期推进流_王启龙.exe scaffold 3  生成第3周练习骨架（learning/王启龙/ 下）
学期推进流_王启龙.exe done W1-A1  勾选任务完成
学期推进流_王启龙.exe undo W1-A1  取消勾选
学期推进流_王启龙.exe record MAN-W2-01 pass "截图已存results/logs/"   手工补录外部动作
学期推进流_王启龙.exe ledger       学习验证台账（--sync 同步写入 VERIFY_LEDGER.md）
学期推进流_王启龙.exe report 1     生成周报 md（learning/王启龙/周报_第1周_日期.md）
学期推进流_王启龙.exe milestones   里程碑达成状态
```

3. **成员命令行**（4 名成员：加 `--member 姓名`；练习骨架已全部预生成在 `learning/<姓名>/`，以下按需使用）：

```
学期推进流_王启龙.exe --member 宁显泷            成员看板（自己名下练习清单与状态）
学期推进流_王启龙.exe --member 宁显泷 week 2     看第2周练习的任务/契约/判定
学期推进流_王启龙.exe --member 宁显泷 scaffold 2 重新生成第2周练习骨架（已存在则提示）
学期推进流_王启龙.exe --member 宁显泷 check 2    核验第2周练习（跑你的 .py 比 [FLOW] 契约）
学期推进流_王启龙.exe --member 宁显泷 check all  核验自己全部练习周
学期推进流_王启龙.exe --member 宁显泷 done W2-A1 勾选（任务号按打卡页上的编号）
学期推进流_王启龙.exe --member 宁显泷 record N-C2-01 pass "服务器实测 rho=0.61"   补录服务器结果
学期推进流_王启龙.exe --member 宁显泷 report 2   生成周报 md（learning/宁显泷/ 下）
学期推进流_王启龙.exe --member 宁显泷 ledger     自己的学习台账
```

没有 Python 的成员也可以直接用 `python tools/semester_flow.py --member 姓名 …` 的等价 exe 命令（上面这些就是）；写了代码的深度核验（练习运行）仍需本机或服务器有 Python。

## 二、每周怎么用（对应推进程序 SOP）

| 时段 | 负责人 | 成员 |
|---|---|---|
| 周一组会后 | `next` 看本周第一件事；`week N` 预习 | 打开自己的 打卡.html 看周卡片 |
| 周三学习日 | `scaffold N` 生成练习骨架 → 按验证卡实现 | 骨架已在 `learning/<姓名>/`，直接实现 |
| 周五核验日 | `check N --deep` → `report N` 生成周报发导师；`done/record` 勾选 | `--member 姓名 check N` → `report N` |
| 周日 | `ledger --sync` 同步台账后 git push | 打卡页"数据管理"导出进度备份 |

## 三、放置位置与仓库探测

exe 会按顺序找仓库根（含 run_all.py 的目录）：**exe 所在目录 → 其上级 → 当前目录逐级向上**。
推荐把 exe 放在仓库 `tools/` 里（默认位置，上级即仓库根）；拷到别处用时加 `--repo 仓库路径`。
找不到仓库时：成员看板/台账仍可用，但自动核验显示[跳过]，且状态会写到 **exe 旁边的 `semester_flow_state_<姓名>.json`**（不进 git、与仓库进度脱钩）——发现这种情况说明 exe 不在仓库里。

## 四、核验口径（准确性）

- 快速核验（文件存在/CSV行数/git标签/文本锚点）**开箱即用**；
- 深度核验（run_all.py 一键复现、45项校验、练习运行、md5确定性）**需要本机装有 Python**——exe 自动从 PATH 找 `python` / `py -3`，找不到则[跳过]并提示，不会谎报通过；
- 每条结果都带"实测值 + 依据来源"，预期值全部锚定仓库存档文件；
- 标注【目标态】的不符 = 未来周工作未到期（如 vina 真实分、v2.0-semester 标签），属正常推进状态；
- 成员模式的核验只覆盖**学习练习 [FLOW] 契约**（过关标准与各自打卡页一致）；项目任务/文件核验按打卡.html 与 docs/VERIFY_TASKS.md 执行。

## 五、重新打包（改了 semester_flow.py 之后）

```
cd tools
python -m PyInstaller --onefile --console --name semester_flow --distpath . --workpath build --specpath build semester_flow.py
mv -f semester_flow.exe 学期推进流_王启龙.exe && rm -rf build
```

（文件名保留"王启龙"是为少改各处文档；程序本身已是全员版，`--member` 即成员入口。）

## 六、状态文件

每人一份：`learning/<姓名>/flow_state.json`（删掉即重置该人进度，仓库产物不受影响）。
负责人另有 `learning/<姓名>/VERIFY_LEDGER.md`（`ledger --sync` 追加写入）。
