# coding: utf-8

import base64
import requests
import json
import difflib

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
# 定义技能和个人素质列表
skills_list = [
    "HTML5", "JavaScript", "CSS3", "Vue", "Python", "JAVA", "React", "PHP", "C++", "C语言",
    "uni-app", "jQuery", "Angular", "Bootstrap", "Node.js", "Express", "Vue.js",
    "Git", "Webpack", "MySQL", "Oracle", "SQL Server", "Linux", "Windows", "Android",
    "CAD绘图", "系统集成", "电路设计", "BIM技术", "ERP系统", "控制系统", "电子信息", "通信协议", "智能化", "机器人技术", "控制算法",
    "网络设备", "网络安全", "防火墙", "TCP/IP", "OSPF", "BGP", "VPN", "交换机", "路由器", "网络系统", "网络通信",
    "软件测试", "测试计划", "测试报告", "单元测试", "功能测试", "测试用例", "软件工程", "设计模式", "架构设计", "面向对象设计", "软件开发", "系统维护", "项目管理", "API开发",
    "数据分析", "数据结构", "数据库管理", "信息化", "信息安全", "信息系统", "数据中心", "图像处理", "音视频处理"
]

qualities_list = [
    "表达能力", "PPT制作", "售后服务", "技术支持", "方案设计",
    "责任心", "上进心", "逻辑思维", "实践经验", "团队精神", "吃苦耐劳", "认真负责", "解决问题", "主动性", "积极性", "沟通", "语言表达"
]


def find_closest_skill(skill_name, skills_list):
    matches = difflib.get_close_matches(
        skill_name, skills_list, n=1, cutoff=0.5)
    return matches[0] if matches else None


def sdk_resumeParse(url, fname):
    # 读取文件内容
    cont = open(fname, 'rb').read()
    # base_cont = base64.b64encode(cont)  # python2
    base_cont = base64.b64encode(cont).decode('utf8')  # python3

    # 构造json请求
    data = {
        'file_name': fname,         # 简历文件名（需包含正确的后缀名）
        'file_cont': base_cont,     # 简历内容（base64编码的简历内容）
        'need_avatar': 0,            # 是否需要提取头像图片
        'ocr_type': 1,                 # 1为高级ocr
    }

    appcode = 'f420028181e64ded989350ccdc151ec6'
    headers = {'Authorization': 'APPCODE ' + appcode,
               'Content-Type': 'application/json; charset=UTF-8',
               }
    # 发送请求
    data_js = json.dumps(data)
    res = requests.post(url=url, data=data_js, headers=headers)

    # 解析结果
    res_js = json.loads(res.text)
    print(json.dumps(res_js, indent=4, ensure_ascii=False))      # 打印全部结果

    return res_js


def process_resume_data(resume_data):
    # 提取基本信息
    basic_info = {
        'name': resume_data['result']['name'],
        'email': resume_data['result']['email'],
        'phone': resume_data['result']['phone'],
        'major': resume_data['result']['major'],
        # 使用转换后的学历等级
        'degree': education_keywords.get(resume_data['result']['degree'], 0),
        'skills': resume_data['result']['skills_objs'],
        'quality': resume_data['result']['cont_my_desc']
    }
    # 过滤技能

    basic_info['quality'] = sum(basic_info['quality'].count(
        quality) for quality in qualities_list)

    # 简化技能列表：提取技能名和转换等级
    skills = {}
    for skill in basic_info['skills']:
        closest_skill = find_closest_skill(skill['skills_name'], skills_list)
        if closest_skill:
            skill_level = skill.get('skills_level', '了解')  # 默认等级为了解
            skill_level_value = level_keywords.get(skill_level, 1)
            if closest_skill not in skills or skill_level_value > skills[closest_skill]:
                skills[closest_skill] = skill_level_value  # 使用技能等级的数值，而不是等级关键词

    basic_info['skills'] = skills  # 更新技能列表为简化后的字典

    # 返回处理结果
    return {
        'basic_info': basic_info,
        # 'evaluation': evaluation,
        # 'recommended_positions': recommended_positions
    }


if __name__ == '__main__':
    url = 'http://resumesdk.market.alicloudapi.com/ResumeParser'
    fname = u'resume.jpg'
    result = sdk_resumeParse(url, fname)

    # result2 = process_resume_data(result)
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)