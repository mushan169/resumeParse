import json
from py2neo import Graph
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

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

with open("./data/basicData.json", "r", encoding="utf-8") as f:
    basicData = json.load(f)
    skills_list = basicData["skills"]
    qualities_list = basicData["personality"]


def build_query(city, education, skills, limit):
    uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
    username = "neo4j"              # 修改为您的用户名
    password = "mushanmushan"          # 修改为您的密码
    graph = Graph(uri, auth=(username, password))

    query = """
MATCH (cn:Company)-[:HAS]->(cp:CompanyPosition)-[:POSITION]->(p:Position),
      (cp)-[r:REQUIRES_SKILL]->(sk:Skill),
      (cp)-[:SALARY]->(s:Salary),
      (cp)-[:EDUCATION]->(e:Education),
      (cp)-[:ADDRESS]->(ad:Address),
      (cp)-[:CITY]->(c:City),
      (cp)-[:QUALITY]->(q:Quality)
WHERE e.name IN $education 
  AND c.name IN $city 
  AND ANY(skill IN $skills WHERE skill IN [(cp)-[:REQUIRES_SKILL]->(sk2:Skill) | sk2.name])
WITH p.name AS Position, 
     cn.name AS Company, 
     cp.id AS CompanyPosition, 
     collect(sk.name) AS Skills, 
     count(sk) AS skillMatchCount, 
     s.name AS Salary, 
     e.name AS Education, 
     ad.name AS Address, 
     c.name AS City, 
     q.name AS Quality
RETURN Position,
       Company,
       CompanyPosition,
       Skills,
       skillMatchCount,
       Salary,
       Education,
       Address,
       City,
       Quality
ORDER BY skillMatchCount DESC
LIMIT $limit

    """
    results = graph.run(query, education=education,
                        city=city, skills=skills, limit=limit)

    # 将结果转换为字典列表
    results_list = []
    for result in results:
        # 将每个结果项转换为字典
        result_dict = {
            "Position": result["Position"],
            "Company": result["Company"],
            "Salary": result["Salary"],
            "Skills": result["Skills"],
            "Education": result["Education"],
            "Quality": result["Quality"],
            "CompanyPosition": result["CompanyPosition"]
        }
        results_list.append(result_dict)

    # 将获得的数据写到文件中
    # with open('positions.json', 'w', encoding='utf-8') as f:
    #     json.dump(results_list, f, ensure_ascii=False, indent=2)
    # print(f'获取职位数据:{results_list}')

    return results_list


# 职位相似度计算
def calculate_similarity_matrix(positions):
    feature_vectors = []
    position_ids = []

    for position in positions:
        # 收集职位 ID
        position_ids.append(position["CompanyPosition"])

        # 构造特征向量
        feature_vector = []

        # 技能特征（检查技能是否在 skills_list 中）
        for skill in skills_list:
            feature_vector.append(1 if skill in position["Skills"] else 0)

        # 质量特征（直接使用 Quality 数值）
        feature_vector.append(position["Quality"])

        # 教育特征（直接使用 Education 数值）
        feature_vector.append(position["Education"])

        # 添加到特征向量列表
        feature_vectors.append(feature_vector)

    # 转换为 NumPy 矩阵
    feature_matrix = np.array(feature_vectors)

    # 计算余弦相似度矩阵
    similarity_matrix = cosine_similarity(feature_matrix)

    return position_ids, similarity_matrix


# 推荐函数
def recommend_positions_itemcf(resume, city, target_position_id=None, top_n=10):
    # 假设用户学历为本科以上
    user_education_levels = [resume["education"]]
    user_skills = list(resume["skills"].keys())
    # 查询符合条件的职位数据
    positions = build_query(city, user_education_levels,
                            user_skills, limit=100)
    print(positions)
    if not positions:
        return []

    # 计算职位相似度矩阵
    position_ids, similarity_matrix = calculate_similarity_matrix(positions)
    print(similarity_matrix)
    print(position_ids)

    recommendations = []

    # 如果目标职位 ID 为空，按平均相似度降序排序
    if target_position_id is None:
        # 计算每个职位的平均相似度
        average_similarity = np.mean(similarity_matrix, axis=1)
        # 按平均相似度降序排序，返回前 top_n 个职位
        sorted_indices = np.argsort(-average_similarity)
        for idx in sorted_indices[:top_n]:
            recommendations.append({
                "Position": positions[idx],
                "Similarity": average_similarity[idx],
            })
        return recommendations

    # 查找目标职位的索引
    if target_position_id not in position_ids:
        return []

    target_index = position_ids.index(target_position_id)

    # 获取与目标职位最相似的职位
    similar_indices = np.argsort(-similarity_matrix[target_index])  # 按相似度降序排序

    for idx in similar_indices[:top_n + 1]:  # 获取前 n+1 个职位（包括目标职位）
        if position_ids[idx] != target_position_id:  # 排除目标职位本身
            recommendations.append({
                "Position": positions[idx],
                "Similarity": similarity_matrix[target_index][idx],
            })

    return recommendations


if __name__ == "__main__":

    city = ['北京市']
    education = [1, 2, 3]
    skills = ['Python', 'Java', 'C++']
    limit = 10
    resume = {
        'name': "田立辉",
        'email': "tianlihui222@canva.com",
        'phone': "13868555068",
        'major': "计算机科学与技术",
        'education': 3,
        'skills': {'Python': 4, 'Java': 3, 'C++': 1},
        'quality': 5
    }
# print(list(resume["skills"].keys()))
# 岗位查询部分
# result = build_query(city, education,skills, limit)
# for item in result:
#     print(item["Education"])

# 协同过滤算法实现
# 输入为用户的简历信息,指定的城市和目标职位id（可不选）
recommendations = recommend_positions_itemcf(
    resume, city, target_position_id=None, top_n=10)

# for item in recommendations:
#     print({
#         "PositionInfo": {
#             "Position": item["Position"]["Position"],
#             "Company": item["Position"]["Company"],
#             "Salary": item["Position"]["Salary"],
#             "Skills": item["Position"]["Skills"],
#             "Education": item["Position"]["Education"],
#             "Quality": item["Position"]["Quality"]
#         },
#         "Similarity": f"{item['Similarity']:.5f}"
#     })

with open('positions.json', 'w', encoding='utf-8') as f:
    json.dump([{
        "PositionInfo": {
            "Position": item["Position"]["Position"],
            "Company": item["Position"]["Company"],
            "Salary": item["Position"]["Salary"],
            "Skills": item["Position"]["Skills"],
            "Education": item["Position"]["Education"],
            "Quality": item["Position"]["Quality"]
        },
        "Similarity": f"{item['Similarity']:.5f}"
    } for item in recommendations], f, ensure_ascii=False, indent=2)
