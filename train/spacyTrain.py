import spacy
from spacy.training import Example
import json

# 加载预训练的SpaCy模型，假设是中文模型
nlp = spacy.load("zh_core_web_md")

# 定义 JSON 文件路径
json_file_path = "./TrainData.json"

# 从 JSON 文件加载训练数据
with open(json_file_path, "r", encoding="utf-8") as f:
    training_data = json.load(f)

# 获取命名实体识别 (NER) 组件
if "ner" not in nlp.pipe_names:
    ner = nlp.add_pipe("ner")
else:
    ner = nlp.get_pipe("ner")

# 在 NER 模型中添加新的实体类别
name_translate={
    "姓名": "name",
    "学历": "education",
    "邮箱":"email",
    "技能":"skills",
    "技能等级":"skills_level",  
    "专业":"major",
    "电话号码":"phone",
    "个人素质":"personality"
}
for label in name_translate.values():
    ner.add_label(label)

# 开始训练模型
optimizer = nlp.resume_training()

# 训练循环
for epoch in range(40):  # 设置训练轮次
    for data in training_data:  # 遍历 JSON 数据中的每条记录
        text = data["text"]  # 获取文本
        annotations = {"entities": data["entities"]}  # 获取实体标注
        doc = nlp.make_doc(text)  # 创建一个 SpaCy 文档对象
        example = Example.from_dict(doc, annotations)  # 创建 Example 对象
        nlp.update([example], drop=0.5, sgd=optimizer)  # 更新模型参数

# 保存训练好的模型
nlp.to_disk("ner_model")

# 测试训练后的模型
test_text = "田立辉|求职意向：市场专员/随时入职|简|出生年月：1996年3月|手机号码：13066668888|毕业院校：上海交通大学|邮箱：tianlihui222@canva.com|历|教育背景|2014.09-2018.06|上海交通大学|数据科学本科|GPA: 3.4|主修课程：概率论与数理统计，线性代数，统计学原理，大数据统计技术，数据分析方法|工作经历|2018.02-至今|上海天命科技公司|数据分析师|·搜集市场反馈并进行客户关系分析，提高公司的口碑，优化销售不足。|·根据公司产品定位和目标人群展开推广活动，主在线下进行协助宣传，效果显著。|·独立进行竞品分析并撰写发展方案|·负责业务线的数据分析工作|·通过数据挖掘和分析，为业务决策提供有力支持|掌握技能|·熟练掌握Python、R等数据分析编程语言|·熟悉大数据处理框架Hadoop、Spark和Hive|·掌握SQL等数据库查询语言|·熟悉数据可视化工具Tableau、PowerBl等|·具备扎实的统计学基础|自我评价|我是一名对数据敏感、具备较强分析能力的数据分析师。在校期间，我积极参加各类数据科学竞赛|并获奖，积累了丰富的实践经验。我擅长使用Python等编程语言进行数据处理和模型训练，熟悉大|数据处理框架Hadoop和Spark。我具备良好的逻辑思维和沟通能力，能够迅速融入团队并为业务创|造价值。"
doc = nlp(test_text)  # 使用训练好的模型处理新的文本

# 测试文本和标签是否对其
# doc = nlp.make_doc(text)
# span = doc.char_span(562, 566, label='personality')

# print(span)
# 遍历识别到的实体，打印出标签为 "SKILL" 的实体
for ent in doc.ents:
    if ent.label_ == "phone" and len(ent.text) == 11:

        print(ent.text)  # 打印技能实体
