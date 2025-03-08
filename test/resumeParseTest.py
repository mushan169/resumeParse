import json
import re
import random
import itremCF
education_keywords = {
    "博士": 4,
    "硕士": 3,
    "本科": 2,
    "大专": 1,
}

if __name__ == '__main__':
    # # 提取简历数据
    # image_path = "./images/1.jpg"
    # output_path = "./result.json"
    # resume = extractData.extract_resume_data(image_path, output_path)
    # print(resume)

    # # 获得推荐的岗位
    # city = ['北京市']
    # top_n = 20
    # recommend_positions = itremCF.recommend_positions_itemcf(
    #     resume, city, target_position_id=None, top_n=20)

    # for item in recommend_positions:
    #     print(item)

    resumeJsonData_url = "./test/result.json"

    with open(resumeJsonData_url, 'r', encoding='utf-8') as f:
        resumeJsonData = json.load(f)

    # result = resumeJsonData['result']
    name =  resumeJsonData['result']['name']
    email = resumeJsonData['result']['email']
    phone = resumeJsonData['result']['phone']
    gender = resumeJsonData['result']['gender']
    age = resumeJsonData['result']['age']
    education = resumeJsonData['result']['degree'] # 学历
    major = resumeJsonData['result']['major']
    skills = [skill["skills_name"] for skill in resumeJsonData['result']['skills_objs']]
    # 软性技能/品质
    split_result = re.split(r'[、,]', resumeJsonData['result']['cont_my_desc'])
    quality = [item.strip().replace('\n','') for item in split_result if item.strip()]

    project = [project for project in resumeJsonData['result']['proj_exp_objs']]# 项目经历/暂定

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
    print(resume['education'])
    # 用于推荐算法的resume格式
    resumeFormat = {"name": name, "major": major, "education": [ education_keywords[education] for item in resume['education']],
              "skills": {skill: random.randint(1,4) for skill in skills}, "quality": len(quality), "email": email}

    # print(resume['education'])
    # print(f'resume：{resume}')
    # print(f'resumeFormat：{resumeFormat}')
    city = ['杭州市']
    education = [1, 2, 3]
    skills = ['Python', 'Java', 'C++']
    limit = 10
    top_n = 20
    target_position_id = None
    recommend_positions = itremCF.recommend_positions_itemcf(
    resumeFormat, city, target_position_id, top_n)

    for item in recommend_positions:
        print(item)