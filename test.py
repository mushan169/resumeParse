from py2neo import Graph
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# **1. 连接到 Neo4j 数据库**
class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))
    
    def query(self, query):
        return self.graph.run(query)

# **2. 定义职位特征查询语句**
def get_job_features(neo4j_handler):
    query = """
    MATCH (job:Job)-[r]->(feature)
    RETURN job.name AS job, collect(r.type + ":" + feature.name) AS features
    """
    result = neo4j_handler.query(query)
    job_features = {record["job"]: record["features"] for record in result}
    return job_features

# **3. 将简历与职位特征匹配**
def clean_text(text):
    if isinstance(text, str):
        return text.strip().lower()
    return text

def resume_to_features(resume, weights=None):
    if weights is None:
        weights = {"education": 0.2, "skill": 0.5, "quality": 0.2, "location": 0.1}
    
    features = []
    # 添加学历
    education_mapping = {"博士": 4, "硕士": 3, "本科": 2, "大专": 1}
    education_scores = [education_mapping.get(clean_text(edu), 0) for edu in resume.get("education", [])]
    if education_scores:
        education_score = max(education_scores) * weights['education']
        features.append(f"education:{education_score}")
    
    # 添加技能
    for skill in resume.get("skills", []):
        cleaned_skill = clean_text(skill)
        if cleaned_skill:
            features.append(f"skill:{cleaned_skill} {weights['skill']}")
    
    # 添加个人素质
    for quality in resume.get("personality", []):
        cleaned_quality = clean_text(quality)
        if cleaned_quality:
            features.append(f"quality:{cleaned_quality} {weights['quality']}")
    
    # 添加地理位置
    location = resume.get("location")
    if location:
        cleaned_location = clean_text(location)
        if cleaned_location:
            features.append(f"location:{cleaned_location} {weights['location']}")

    return " ".join(features)

# **4. 计算职位相似性**
def calculate_similarity(job_features, resume_features):
    # 创建特征矩阵
    vectorizer = TfidfVectorizer()
    job_texts = [" ".join(features) for features in job_features.values()]
    all_texts = job_texts + [resume_features]
    features_matrix = vectorizer.fit_transform(all_texts)
    
    # 计算余弦相似度
    similarity_matrix = cosine_similarity(features_matrix)
    resume_similarity = similarity_matrix[-1][:-1]  # 与简历的相似度
    return resume_similarity

# **5. 推荐职位**
def recommend_jobs(job_features, similarity_scores, top_n=5):
    sorted_jobs = sorted(zip(job_features.keys(), similarity_scores), key=lambda x: x[1], reverse=True)
    return sorted_jobs[:top_n]

# **6. 测试简历和推荐逻辑**
if __name__ == "__main__":
    # 连接 Neo4j 数据库
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "mushanmushan"
    neo4j_handler = Neo4jHandler(uri, user, password)
    
    # 获取职位特征
    job_features = get_job_features(neo4j_handler)
    
    # 测试简历数据
    resume = {
        "name": ["田立辉"],
        "major": ["计算机类"],
        "education": ["本科"],
        "skills": ["数据分析", "数据挖掘", "Python", "Spark", "Hive", "SQL", "数据可视化", "PowerBl", "编程语言"],
        "personality": ["分析能力", "逻辑思维", "沟通能力", "迅速融入团队"],
        "email": ["tianlihui222@canva.com"],
        "location": ["北京"]
    }
    
    # 提取简历特征
    resume_features = resume_to_features(resume)
    
    # 计算相似性
    similarity_scores = calculate_similarity(job_features, resume_features)
    
    # 推荐职位
    recommendations = recommend_jobs(job_features, similarity_scores)
    
    print("推荐职位：")
    for job, score in recommendations:
        print(f"职位: {job}, 相似度: {score:.2f}")