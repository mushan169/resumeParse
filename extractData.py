import spacy
import time
import cv2
import gc
import json
import re
import random
from paddleocr import PaddleOCR
from spacy.matcher import Matcher


level_keywords = {
    "精通": 4,
    "熟练": 3,
    "熟悉": 2,
    "了解": 1,
}
education_keywords = {
    "博士": 4,
    "硕士": 3,
    "本科": 2,
    "大专": 1,
}

# 提取简历数据，包含ocr识别图片和提取简历数据，
# 普通模式
def extract_resume_data(img_path, output_path):
    # 基础数据用于校对提取的内容
    basic_data_path = "./data/basicData.json"
    with open(basic_data_path, "r", encoding="utf-8") as f:
        basicData = json.load(f)

    # 提取文本中的姓名、专业、技能、学历、个人素质、邮箱
    name = []
    major = ["计算机类"]  # 默认为计算机类专业,专业与技能之间不易识别
    education = []
    skills = []
    personality = []

    begin_time = time.time()

    # OCR模型识别简历文字
    ocr = PaddleOCR(use_angle_cls=True, lang="ch",
                    use_gpu=True, show_log=False)

    img = cv2.imread(img_path)

    result = ocr.ocr(img, cls=True)
    resume_text = ""
    for line in result:
        for word_info in line:
            # word_info[1][0] 是文字内容
            resume_text += word_info[1][0].strip() + " "

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

    resume = {"name": name, "major": major, "education": education,
              "skills": skills, "quality": personality, "email": email}

    resumeFormat = {"name": name, "major": major, "education": [education_keywords.get(item) for item in education],
                    "skills": {skill: random.randint(1, 4) for skill in skills}, "quality": len(personality), "email": email}

    # 写回文件
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resume, f, ensure_ascii=False, indent=2)

    # print("提取结果：")
    # print("姓名:", name)
    # print("专业:", major)
    # print("学历:", education)
    # print("技能:", skills)
    # print("个人素质:", personality)
    # print("邮箱:", email)

    print("总共用时:", time.time() - begin_time, "s")

    gc.collect()

    return resume, resumeFormat

# 快速模式
def extract_resume_data_quick():

    # 快速模式的测试
    resumeJsonData_url = "./test/result.json" # 模拟api得到的简历数据

    with open(resumeJsonData_url, 'r', encoding='utf-8') as f:
        resumeJsonData = json.load(f)

    # result = resumeJsonData['result']
    name = resumeJsonData['result']['name']
    email = resumeJsonData['result']['email']
    phone = resumeJsonData['result']['phone']
    gender = resumeJsonData['result']['gender']
    age = resumeJsonData['result']['age']
    education = resumeJsonData['result']['degree']  # 学历
    major = resumeJsonData['result']['major']
    skills = [skill["skills_name"]
              for skill in resumeJsonData['result']['skills_objs']]
    # 软性技能/品质
    split_result = re.split(r'[、,]', resumeJsonData['result']['cont_my_desc'])
    quality = [item.strip().replace('\n', '')
               for item in split_result if item.strip()]

    project = [project for project in resumeJsonData['result']
               ['proj_exp_objs']]  # 项目经历/暂定

    # 用于前端展示的resume格式
    resume = {
        "name": name,
        "email": email,
        "phone": phone,
        "gender": gender,
        "age": age,
        "education": [education],
        "major": major,
        "skills": skills,
        "quality": quality,
        "project": project
    }
    # 用于推荐算法的resume格式
    resumeFormat = {
        "name": name,
        "major": major,
        "education": [education_keywords[education] for item in resume['education']],
        "skills": {skill: random.randint(1, 4) for skill in skills},
        "quality": len(quality),
        "email": email}

    return resume, resumeFormat


if __name__ == "__main__":
    print("开始提取简历信息...")
    img_path = "./images/1.jpg"
    output_path = "result.json"
    extract_resume_data(img_path, output_path)
