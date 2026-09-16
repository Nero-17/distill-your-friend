# 数据约定

输入为 JSON 对象，messages 为消息数组。每条包含唯一字符串 id、稳定字符串 speaker、Unix秒 timestamp、字符串 text；可选 quote（字符串或 null）、session_id（完整会话分组ID）。适配器负责类型转换、引用发言归属、时区及多媒体占位，不猜测图片内容。

timestamp 按秒解释，不自动猜毫秒。选择 UTC 日期作为分组时，如原导出跨午夜仍属同一事件，应提供 session_id 避免拆开。session_id 要么所有消息都有，要么都没有。至少需要十个分组才能使用准备脚本的默认划分。

重复ID的完全相同记录去重；同ID不同内容报错。凭据筛选仅为保守模式匹配，无法证明所有敏感信息都已清除。即使经过清洗，产物仍视为私人材料，不可发布。

历史 episode 包含 id、date、end_time、source=real_training、messages；消息保留来源 id、speaker、text、timestamp、quote。短窗口不代表独立事件；检索后仍需判断上下文是否充分。

预测文件为数组，每项 id、label（real或synthetic）、p_synthetic（0到1）。标签文件同ID且含 label，可选 control=true。控制样本单独报告；不要将标签文件交给盲评者。
