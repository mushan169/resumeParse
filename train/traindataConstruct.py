import json
import spacy
import json
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans

# 该模块用户将json数据转化为spacy格式

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

# 转化成 .spacy格式
def convert_to_spacy_spacyFormat(labelstudio_data):
    # 读取 Label Studio 导出的 JSON 文件
    with open('./train/devTrainData.json', 'r', encoding='utf-8') as f:
        TRAIN_DATA = json.load(f)
    nlp = spacy.blank('zh')   # 选择中文空白模型
    doc_bin = DocBin()
    for training_example in tqdm(TRAIN_DATA):
        text = training_example['text']
        labels = training_example['entities']
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in labels:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        filtered_ents = filter_spans(ents)
        doc.ents = filtered_ents
        doc_bin.add(doc)

    doc_bin.to_disk("dev.spacy")

# 转换为 SpaCy json格式
def convert_to_spacy_jsonFormat(labelstudio_data):
    
    training_data = []
    for item in labelstudio_data:
        text = item["data"]["text"]  # 文本字段
        annotations = item["annotations"][0]["result"]  # 标注结果
        entities = []
        for annotation in annotations:
            if annotation["type"] == "labels":  # 确保是标注实体
                label = name_translate.get(annotation["value"]["labels"][0])  # 标签名
                start = annotation["value"]["start"]  # 实体起始位置
                end = annotation["value"]["end"]  # 实体结束位置
                entities.append((start, end, label))
        training_data.append(({"text":text,"entities": entities}))

    # 保存spacy训练格式数据
    with open("devTrainData.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)

    print(training_data)

if __name__ == "__main__":
    # 读取 Label Studio 导出的 JSON 文件
    with open('./train/devTrainData.json', 'r', encoding='utf-8') as f:
        TRAIN_DATA = json.load(f)
    convert_to_spacy_spacyFormat(TRAIN_DATA)

