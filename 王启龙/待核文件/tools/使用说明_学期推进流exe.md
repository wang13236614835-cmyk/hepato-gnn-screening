# 学期推进流 exe 使用说明（负责人·王启龙）

**程序**：`tools/学期推进流_王启龙.exe`（约 8MB，PyInstaller 单文件打包，无需安装 Python 即可运行）
**源码**：`tools/semester_flow.py`（修改源码后重新打包的命令见文末）

## 一、两种用法

1. **双击运行**：显示"本周看板"（自动按日期定位第几周：学习内容、学习验证卡、推进任务、统筹事项），看完按回车退出。
2. **命令行运行**（在 cmd / PowerShell / Git Bash 中）：

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
学期推进流_王启龙.exe milestones   里程碑 M1–M9 达成状态
```

## 二、每周怎么用（对应推进程序 SOP）

| 时段 | 命令 |
|---|---|
| 周一组会后 | `next` 看本周第一件事；`week N` 预习 |
| 周三学习日 | `scaffold N` 生成练习骨架 → 按验证卡实现 |
| 周五核验日 | `check N --deep` → `report N` 生成周报发导师；`done/record` 勾选 |
| 周日 | `ledger --sync` 同步台账后 git push |

## 三、放置位置与仓库探测

exe 会按顺序找仓库根（含 run_all.py 的目录）：**exe 所在目录 → 其上级 → 当前目录逐级向上**。
推荐把 exe 放在仓库 `tools/` 里（默认位置，上级即仓库根）；拷到别处用时加 `--repo 仓库路径`。
找不到仓库时：看板/任务/台账仍可用，自动核验显示[跳过]。

## 四、核验口径（准确性）

- 快速核验（文件存在/CSV行数/git标签/文本锚点）**开箱即用**；
- 深度核验（run_all.py 一键复现、45项校验、练习运行、md5确定性）**需要本机装有 Python**——exe 自动从 PATH 找 `python` / `py -3`，找不到则[跳过]并提示，不会谎报通过；
- 每条结果都带"实测值 + 依据来源"，预期值全部锚定仓库存档文件；
- 标注【目标态】的不符 = 未来周工作未到期（如 vina 真实分、v2.0-semester 标签），属正常推进状态。

## 五、重新打包（改了 semester_flow.py 之后）

```
cd tools
python -m PyInstaller --onefile --console --name semester_flow --distpath . --workpath build --specpath build semester_flow.py
mv -f semester_flow.exe 学期推进流_王启龙.exe && rm -rf build
```

## 六、状态文件

勾选与核验记录存于 `learning/王启龙/flow_state.json`（删掉即重置进度，仓库产物不受影响）。
