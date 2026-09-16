# 有来源的记忆

仓库之外的 --store 包含 episodes.json（训练历史）、按需创建的 observations.jsonl（用户新原话与纠正）、sessions/（虚构会话状态）。生成内容和评审意见不能写成真人历史。程序检查字段与来源标签，代理仍须核实来源真实性。

retrieve 的查询文件含 query、before（场景时刻的Unix秒）、可选 limit。词面检索使用二元字符的IDF加权匹配，只选早于before的片段。没有相关记忆就不用，不能为填状态表虚构心理或事实。

过去发生的事、单次体验、明确自述习惯和当前状态分开。过去说“没发生某事”不代表庆幸，报告一个事实不代表嫌弃；不要给旧原文擅自加态度。当前前文可支持新的虚构设定，但不能伪装成已经存在的历史。

remember 输入含 id、date（YYYY-MM-DD）、end_time、source（user_message或user_correction）、messages（speaker/text/timestamp），可选 supersedes 指向需替代的记录。保留原始标签，不因用户与模型对话就认定用户是某位历史角色。纠正在其时间之后才生效；旧原文不会被删除。

state 使用 --session 安全名称和 --input 状态JSON，将内容明确标记为 synthetic_session。不同模拟会话不共享虚构事实。每人维护正在做的事、已完成事项、计划、未完话题和未知项；不强求每项都有值。

这是一套需要代理主动读写的本地文件机制，不会自动给整个应用增加后台记忆，也不代表知道真人实时状态。
