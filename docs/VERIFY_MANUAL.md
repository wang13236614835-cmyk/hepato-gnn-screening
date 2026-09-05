# 核验操作说明

1. 先读 PROJECT_STATUS.md，区分历史结果与当前结论。
2. 打开本人打卡页，按周提交证据路径/版本、实测结果和限制。
3. 学习视频需记录实际课名、观看时段与时长，完成提取回忆、研究应用和教回。
4. 导出本机记录，保存到 learning/姓名/review_v2/，提交版本后由交叉复核人给出独立结论。
5. 软件检查：`python tools/verify_research.py`；诊断模型：`python final-aidd-screening/run_all.py --diagnostic --model --output <新的空目录>`。
6. 默认研究入口因标签/身份未审核而阻止运行是预期行为，不能改成默认通过。
7. AIDD主线用自己的MASH靶点、终点和数据审核，不能复用GNN通过状态。

核验应发现错误，不要求复现出旧的高AUC、低RMSD或固定排名。
