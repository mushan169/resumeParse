import spacy
import time
import cv2
import gc
import json
import re
from paddleocr import PaddleOCR
from spacy.matcher import Matcher

# 提取建立数据
def extract_resume_data( img_path, output_path):

    basic_data_path = "./data/basicData.json"
    with open(basic_data_path, "r", encoding="utf-8") as f:
        basicData = json.load(f)

    # 提取文本中的姓名、专业、技能、学历、个人素质、邮箱
    name = []
    major = ["计算机类"]  # 默认为计算机类专业
    education = []
    skills = []
    personality = []

    begin_time = time.time()

    # OCR模型识别简历文字
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", use_gpu=True, show_log=False)

    img = cv2.imread(img_path)

    result = ocr.ocr(img, cls=True)
    resume_text = ""
    for line in result:
        for word_info in line:
            resume_text += word_info[1][0] + " "  # word_info[1][0] 是文字内容

    # 输出识别的文字
    print("OCR 识别结果：")
    print(resume_text.strip())

    # 使用spacy训练模型提取职业技能
    nlp = spacy.load("./spacy/model-best")
    doc = nlp(resume_text)

    # 提取职业技能、个人素质
    for ent in doc.ents:
        if ent.label_ == "major" and ent.text not in major and ent.text in basicData["major"]:
            major.append(ent.text)
        if ent.label_ == "skills" and ent.text not in skills and ent.text in basicData["skills"]:
            skills.append(ent.text)
        if ent.label_ == "personality" and ent.text not in personality and ent.text in basicData["personality"]:
            personality.append(ent.text)

    # 使用预处理模型提取人名、学历
    nlp = spacy.load("zh_core_web_md")
    doc = nlp(resume_text)

    matcher = Matcher(nlp.vocab)
    academic_pattern = [{"TEXT": {"IN": ["博士", "硕士", "本科", "专科", "职高"]}}]
    matcher.add("ACADEMIC_PATTERN", [academic_pattern])
    matches = matcher(doc)

    # 提取人名
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(name) == 0 and ent.text not in name and ent.text in basicData["name"]:
            name.append(ent.text)

    # 正则匹配邮箱
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    email = re.findall(email_pattern, resume_text)

    # 提取学历
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        content = doc[start:end].text
        if content not in education and label == "ACADEMIC_PATTERN":
            education.append(content)

    # 写回文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"name": name, "major": major, "education": education,
                  "skills": skills, "personality": personality, "email": email}, f, ensure_ascii=False, indent=2)

    print("提取结果：")
    print("姓名:", name)
    print("专业:", major)
    print("学历:", education)
    print("技能:", skills)
    print("个人素质:", personality)
    print("邮箱:", email)

    print("总共用时:", time.time() - begin_time, "s")

    gc.collect()


if __name__ == "__main__":
    print("开始提取简历信息...")
    img_path = "./images/1.jpg"
    output_path = "./data/result.json"
    extract_resume_data(img_path, output_path)