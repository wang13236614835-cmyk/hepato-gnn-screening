# 环境配置说明

负责人：王启龙（工程支撑）  
统一策略更新：2026-09-14

## 1. 统一原则

本仓库不再要求所有机器安装一模一样的完整科学栈，而是采用**分层环境**：

1. `requirements.txt`：基础层，所有成员默认安装；旧 NumPy GCN、基础清洗、出图可用；
2. `requirements-science.txt`：科学计算/化学层，需要 RDKit、Pandas、统计分析时安装；
3. `requirements-ml.txt`：GNN/ML 层，在科学层之上增加 PyTorch Geometric；**PyTorch 本体必须先按机器的 CPU/CUDA 情况单独安装**；
4. `requirements-validated.txt`：历史“已验证复现快照”，只用于精确复现已登记环境，不作为新机器默认安装文件。

这样做的目的：Windows/Linux、CPU/GPU、不同显卡驱动之间尽量兼容，同时保留需要时的精确复现能力。

## 2. Python 版本

| 范围 | 状态 | 用途 |
|---|---|---|
| Python 3.11 | **推荐基准** | 新建环境默认选它，兼容性最好 |
| Python 3.10 | 支持 | 完整科学/ML 栈 |
| Python 3.12 | 支持 | 完整科学/ML 栈 |
| Python 3.13+ | 基础层可尝试 | 部分 RDKit/PyTorch/PyG 组合可能尚无轮子，不作为完整栈保证范围 |
| Python <3.10 | 不支持 | 不再维护 |

因此：**团队统一推荐 Python 3.11，但代码与依赖声明按 3.10–3.12 兼容设计。**

## 3. 最通用安装方式

### 3.1 基础环境（所有成员）

Windows PowerShell / Linux / macOS 都可使用 venv：

```bash
python -m venv .venv
```

激活：

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows cmd
.venv\Scripts\activate.bat

# Linux/macOS
source .venv/bin/activate
```

然后：

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python tools/check_env.py
```

历史教学流程：

```bash
python run_all.py --legacy-demo
```

该流程不要求 RDKit、PyTorch、PyG、CUDA 或 Vina。

### 3.2 科学计算/化学环境

需要 RDKit、Pandas、scikit-learn、Meeko、Gemmi 等时：

```bash
python -m pip install -r requirements-science.txt
python tools/check_env.py
```

如果某个平台的 RDKit wheel 安装失败，优先创建 Python 3.11 环境重试；仍失败时再使用 conda-forge，而不是修改全仓库依赖版本。

### 3.3 PyTorch / PyG 环境

PyTorch 与 CUDA 必须按机器选择，**不要把 CUDA wheel 固定写进 requirements 文件**。

先根据 PyTorch 官方安装选择器安装与本机对应的：

- CPU-only PyTorch；或
- 对应 CUDA 运行时的 PyTorch。

确认：

```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

再安装 PyG 层：

```bash
python -m pip install -r requirements-ml.txt
python tools/check_env.py
```

CPU 环境同样允许运行；GPU 只是加速选项，不是仓库可用性的前提。

## 4. Conda 用户

Conda 只负责创建干净 Python 环境即可，依赖仍尽量走仓库统一 requirements：

```bash
conda create -n hepato python=3.11 -y
conda activate hepato
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

需要科学层时：

```bash
python -m pip install -r requirements-science.txt
```

需要 GNN 时，先安装匹配本机 CPU/CUDA 的 PyTorch，再：

```bash
python -m pip install -r requirements-ml.txt
```

避免在同一环境里反复交替用 conda 和 pip 安装同一个核心包（尤其 numpy/scipy/pytorch/rdkit），否则容易出现二进制依赖冲突。

## 5. 兼容性矩阵

| 场景 | 基础层 | 科学层 | ML/PyG 层 | 推荐 Python |
|---|---:|---:|---:|---|
| Windows 笔记本 CPU | ✅ | ✅ | ✅ | 3.11 |
| Windows + NVIDIA GPU | ✅ | ✅ | ✅ | 3.11 |
| Linux CPU 服务器 | ✅ | ✅ | ✅ | 3.11 |
| Linux + NVIDIA GPU | ✅ | ✅ | ✅ | 3.11 |
| macOS | ✅ | ✅ | 视 PyTorch/PyG 官方支持 | 3.11 |
| Python 3.10 | ✅ | ✅ | ✅ | 可用 |
| Python 3.12 | ✅ | ✅ | ✅ | 可用 |
| Python 3.13+ | 尽量兼容 | 不保证 | 不保证 | 不建议正式复现 |

`✅` 表示仓库按该组合设计；实际第三方 wheel 是否存在仍以对应包官方发布为准。

## 6. 版本策略

- 通用 requirements 使用**版本范围**，优先兼容新机器和不同平台；
- 不在通用 requirements 中写 CUDA 版本；
- 不要求所有人安装完整依赖；
- 精确复现某次正式计算时，记录 Python、OS、包版本、输入 hash、seed，并可使用对应的锁定快照；
- `requirements-validated.txt` 只代表其注明日期/机器上已验证的快照，不代表唯一合法环境；
- 新增依赖时先判断属于基础层、科学层还是 ML 层，禁止直接把重依赖塞进基础层。

## 7. 环境自检

统一执行：

```bash
python tools/check_env.py
```

它会输出：

- Python 版本与解释器路径；
- 操作系统与架构；
- 基础依赖是否完整；
- RDKit/Pandas/PyTorch/PyG 等可选依赖是否存在；
- PyTorch 是否检测到 CUDA/GPU。

基础依赖缺失会返回非 0；可选包未安装只提示，不会把基础环境判失败。

## 8. 常见问题

- **Windows 中文乱码**：CSV 读取优先 `encoding="utf-8-sig"`；仓库文本统一 UTF-8。
- **matplotlib 中文方框**：代码图内标签优先英文；中文标题放报告层。
- **`pip install torch-geometric` 失败**：先确认 PyTorch 已正确安装，并确认当前 Python 处于 3.10–3.12 支持范围。
- **CUDA 不可用**：不影响基础/CPU 流程；先检查 NVIDIA 驱动与 PyTorch 安装来源，不要通过反复改仓库 requirements 解决。
- **环境混乱**：优先新建 `.venv` 或新的 conda 环境，不要在长期使用的 base 环境中继续堆包。
- **复现性**：代码 seed、输入 hash、模型参数和环境版本必须随正式结果登记；环境兼容不等于科研结果可直接发布。
