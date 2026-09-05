# 保肝中药成分虚拟筛选(GNN + 分子对接)

**是什么**:用图神经网络(含不确定性量化)+ 分子对接,从中药成分中筛选保肝候选分子,产出可复现的候选排名总表。

**怎么做**:

```bash
git clone https://github.com/wang13236614835-cmyk/hepato-gnn-screening.git
cd hepato-gnn-screening
python run_all.py        # 仅需 numpy,约 6 秒跑通全流程
```

结果看 `results/`,解读看 `reports/`;成员任务:打开 `自己文件夹/工作台.md`。

## 目录分类(按用途三组)

**① 数据流(全队公用,流水线工作原件)**

| 目录 | 内容 |
|---|---|
| `data/` | 原始与清洗数据、训练/验证/测试划分 |
| `src/` | 全部代码:图解析、GNN 模型、基线、对接、融合评分 |
| **`final-aidd-screening/`** | **完整研究管线**：按复旦 AIDD 课程 8 步 SOP 组织——redock 门控(FXR 0.74Å/Keap1 1.10Å)、双基线+GNN、Lipinski/PAINS 预过滤、真实 Vina 对接(118/120 次)、三源共识排名、骨架多样性 Top-10；解读见其 `REPORT.md` |
| `results/` | 产出:`docking/` 演示分(45项核验锚点)+ `docking/real/` 真实对接 144 次 · `rankings/` 排名表 · `figures/` `metrics/` `predictions/` `ad/` `logs/` |
| `literature/` | 文献证据库(经典证据/新分子调研/机制溯源) |

**② 项目管理**

| 目录/文件 | 内容 |
|---|---|
| `docs/` | 总纲:`MANIFEST`(全文件清单)· `VERIFY_TASKS`(任务分派)· `PHASE_PLAN`(两阶段规划)· `VERIFY_MANUAL`(核验手册)· `minutes/` `personal/` |
| `reports/` | 报告 + `pdf_all/` 全量 PDF 镜像 |
| `phase2_semester/` | 下学期五个工作包(WP1–WP5) |
| `tools/` | 学期推进等工程工具 |

**③ 个人(每人一份,互不改动)**

| 目录 | 内容 |
|---|---|
| `王启龙/` `宁显泷/` `衣思淼/` `代维斯丹/` `王散曼/` | 各含 `工作台.md`(我的任务)+ `打卡_姓名.html` + `待核文件/` |
| `learning/` | 学习档案(按人)+ `共享/` 共享资源(复旦 AIDD 课程学习任务+手写笔记 PDF) |

根目录另有 `run_all.py`(一键复现)与 `requirements.txt`(依赖声明)。

## 当前在哪一步

**全线流程与当前进度**(打卡页「🔬 全线流程」标签页同步):

- ✅ 完整研究管线已就绪:双靶 redock 门控(FXR 0.74Å/Keap1 1.10Å) + 118 次真实对接 + 三源共识排名(黄芩苷居首) + 多样性 Top-10,见 [final-aidd-screening/REPORT.md](final-aidd-screening/REPORT.md);
- 🔄 进行中:9/20 前人人复核暑假结果(45 项锚点)、服务器复现对账、PyMOL 目检;
- ⏳ 待办:数据扩充 ≥1000 条、模型迁移 PyG+校准、Top-10 文献专查与体外衔接。

**逐文件核验锚点与状态**:[docs/全线研究流程与暑假文件验证对照.md](docs/全线研究流程与暑假文件验证对照.md)。
