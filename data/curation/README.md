# 数据修订工作区

compound_registry.csv 包含全部100条数据库建议结构和原输入。`pending_review` 不是身份确认；legacy_label 仅保留旧标签，正式 label 当前留空，未知不能填0。身份复核需记录 reviewer/date，标签需统一 endpoint、原始证据链接与独立复核。DC-030 已提供反例链接，不自动改成一个新的未经核验标签。

旧 data/raw、data/processed、splits、final-aidd-screening/data/*.csv 是历史输入，不能直接用于候选实验。正式建模仅接受经复核注册表导出的 release；诊断模式只能写到单独 runs 目录。
