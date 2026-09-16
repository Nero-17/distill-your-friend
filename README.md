# 蒸馏你的朋友 · Distill Your Friend

A method-first agent skill for learning how someone replies from chat history: reply logic, expression, shared context, source-aware memory, and iterative blind evaluation.

从聊天记录学习一个人的**回复逻辑与表达方式**，通过独立辨伪反馈反复修订，并保存有出处的历史记忆。

**本仓库仅包含方法和通用工具。没有真实聊天、训练集、测试集、人物档案、记忆库、模型预测、私人实验成绩或这些内容的改名版本。** 私人工作材料必须存放在仓库之外。

## 使用

将此目录作为支持 `SKILL.md` 的代理技能加载，或让代理读取 [SKILL.md](SKILL.md)。提供本地聊天文件、要学习的发言人以及独立私人工作目录。技能不会自行连接聊天账号、发送消息或上传语料。

先由代理将导出文件适配为 [消息格式](references/data-contract.md)，再在 Python 3.10+ 下运行：

```sh
python scripts/prepare.py --input /private/normalized.json --output /private/learning-work
```

这里的 `/private/...` 是使用者自行指定的仓库外目录，不是随仓库提供的数据。准备脚本按 UTC 聊天日或显式 session_id 分组，默认约75%训练、15%开发、10%测试；输出实际比例。独立生成和评审由代理执行，脚本不会调用模型 API，也不会自动微调。

历史检索：

```sh
python scripts/memory.py --store /private/learning-work/memory retrieve --input /private/query.json
```

query.json 包含 query、before（Unix秒）和可选 limit；before 用当前场景时刻，防止读到未来记录。记录新用户观察与独立保存虚构会话的方式见 [记忆说明](references/memory.md)。

## 方法结构

1. 分组切分数据，保留污染与清洗记录。
2. 每个人分别学习回复动作、表达和活动；共同语境独立保存。
3. 根据历史检索与当前状态生成模拟，不机械背诵旧事。
4. 第三方独立学习训练集，盲评匿名混合续聊。
5. 揭晓错误、核实证据、修订，再用新材料复测。
6. 比较旧新版时使用同题、交叉分配评审，保留全部预测。

“蒸馏”在这里指证据驱动的人物档案与提示词迭代，不是复制一个人、自动获取其实时状态或训练其模型权重。记忆检索也不能保证历史理解准确。辨伪正确率接近随机只是一项观察，不足以证明与真人无差别。

## 开发检查

```sh
python -m unittest discover -s tests
python scripts/check_release.py
```

检查代码仅使用临时生成的结构性测试值，没有聊天语料或训练/测试集。发布检查采用文件白名单；`.gitignore` 只是辅助，不能替代提交前检查。
