# 暑假管线修订与诊断入口

此目录用于核验一般保肝教学任务，不是完整MASH工作链。旧报告已归档到 docs/archive/20260904/final-aidd-screening/。

[当前状态](../docs/PROJECT_STATUS.md) · [AIDD研究库](https://github.com/wang13236614835-cmyk/aidd)

默认 `python run_all.py` 会拦截未审核数据。`--diagnostic --model --output <新目录>` 可评估代码修复影响，沿用旧标签，不能称为MASH结果。`--redock-only --output <新目录>` 仅检验FXR/KEAP1结构方法。设置 VINA_BIN 指向合法安装的Vina可执行文件；当前GitHub不包含exe。

软件检查和诊断记录见 ../results/validation；旧Top-10不能作为候选药效依据。
