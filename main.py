import random
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Body
from openai import OpenAI
from utils import docx2img, pdf2img,responseFormat
from py2neo import Graph
import itemCF
import extractData
import graphTest

app = FastAPI()
# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（可以限制为特定来源）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（包括 POST、OPTIONS 等）
    allow_headers=["*"],  # 允许所有请求头
)

# Neo4j 连接配置
uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
username = "neo4j"  # 修改为您的用户名
password = "mushanmushan"  # 修改为您的密码

# 初始化 Neo4j 连接
graph = Graph(uri, auth=(username, password))


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/test")
async def root():
    return {"message": "Hello World"}

# 用于快速模式的简历解析的测试，目前快速模式使用的是这个接口


@app.post("/quickMode")
async def resumeParseQuick(city: str | None = None, top_n: int = 20, target_position_id: int | None = None):
    # 测试目前使用./test/result.json中的假数据
    resume, resumeFormat = extractData.extract_resume_data_quick()

    recommend_positions = itemCF.recommend_positions_itemcf(
        resumeFormat, city, target_position_id, top_n)

    return responseFormat.Response.success(message="数据处理成功", data={
        "resumeInfo": resume,
        "recommendPositions": recommend_positions
    })




@app.post("/userMode")
async def resumeParseQuick(
    city: Optional[List[str]] = Body(None),
    major: Optional[str] = Body(None),
    education: Optional[str] = Body(None),
    skills: Optional[List[str]] = Body(None),
    quality: Optional[List[str]] = Body(None),
    top_n: int = Body(40),
    target_position_id: Optional[int] = Body(None)
):
    # 处理逻辑保持不变
    print("city:", city)
    print("major:", major)
    print("education:", education)
    print("skills:", skills)
    print("quality:", quality)
    
    education_keywords = {
        "博士": 4,
        "硕士": 3,
        "本科": 2,
        "大专": 1,
    }

    # 处理 None 值，避免 KeyError
    education_level = education_keywords.get(education, 0)
 
    resumeFormat = {
        "major": major,
        "education": education_level,
        "skills": {skill: random.randint(1, 4) for skill in (skills or [])},
        "quality": len(quality or []),
    }

    recommend_positions = itemCF.recommend_positions_itemcf(
        resumeFormat, city, target_position_id, top_n)
    
    print(recommend_positions)
    return responseFormat.Response.success(message="数据处理成功", data={
        "recommendPositions": recommend_positions
    })

# 用于简历解析和岗位推荐的测试
@app.get("/resumeParseTest")
async def resumeParseTest(city: str | None = None, top_n: int = 20, target_position_id: int | None = None):
    upload_image_path = "./images/1.jpg"
    output_path = "./result.json"
    resume = extractData.extract_resume_data(upload_image_path, output_path)
    print(resume)

    # 获得推荐的岗位
    recommend_positions = itemCF.recommend_positions_itemcf(
        resume, city, target_position_id, top_n)

    return recommend_positions


# 用于简历文件解析和岗位推荐
@app.post("/resumeParse")
async def resumeParse(city: str | None = None, top_n: int = 20, target_position_id: int | None = None, file: UploadFile | None = None):
    file_type = file.content_type  # 文件类型

    if file is None:
        return {"error": "请上传文件"}
    # 设置处理文件都是jpg格式
    if file_type == "application/pdf":  # 如果上传的是pdf文件
        file_name = "resume.pdf"
        with open(file_name, "wb") as f:
            f.write(file.file.read())
        pdf2img.convert_pdf_to_image(file_name, "resume.jpg")

    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":  # 如果上传的是docx文件
        file_name = "resume.docx"
        with open(file_name, "wb") as f:
            f.write(file.file.read())
        docx2img.convert_docx_to_img(file_name, "resume.jpg")

    elif file_type == "image/jpeg":  # 如果上传的是jpg文件
        file_name = "resume.jpg"
        with open(file_name, "wb") as f:
            f.write(file.file.read())
    else:
        return responseFormat.Response.fail(message="文件格式上传错误")

    # return {"message": "文件上传成功"}
    input_path = "./resume.jpg"
    output_path = "./resumeInfo.json"

    resume, resumeFormat = extractData.extract_resume_data(
        input_path, output_path)

    recommend_positions = itemCF.recommend_positions_itemcf(
        resumeFormat, city, target_position_id, top_n)

    return responseFormat.Response.success(message="数据处理成功", data={
        "resumeInfo": resume,
        "recommendPositions": recommend_positions
    })

# 测试获取图数据库信息
@app.get("/testProperties")
async def get_graph_data_properties(company_position: str = ""):
    # 根据 company_position 是否为空来动态构造 Cypher 查询
    if company_position:
        # 当传入的 company_position 不为空时，进行模糊查询
        nodes_query = f"""
            MATCH (n:CompanyPosition)
            WHERE n.name CONTAINS '{company_position}'
            RETURN id(n) AS id, labels(n) AS labels, n.name AS name, properties(n) AS properties
            LIMIT 50
        """
    else:
        # 如果 company_position 为空，则随机查询
        nodes_query = f"""
            MATCH (n)
            RETURN id(n) AS id, labels(n) AS labels, n.name AS name, properties(n) AS properties
            LIMIT 50
        """

    # 查询节点数据
    nodes_result = graph.run(nodes_query).data()

    nodes = [
        {
            "id": str(record["id"]),
            "name": record["name"] if record["labels"][0] != "CompanyPosition" else record["properties"]["id"],
            "category": record["labels"][0] if record["labels"] else "Unknown",
        }
        for record in nodes_result
    ]

    return nodes


# 获取图数据库信息，用于知识图谱的可视化展示
@app.get("/graphData")
async def get_graph_data(limit: int = 30, position_name: str = ""):

    # 返回给前端
    graphData = graphTest.get_fuzzy_graph_data(position_name, limit=limit)
    return {"nodes": graphData["nodes"], "links": graphData["links"], "categories": graphData["categories"]}

# 获取所有的职位信息，用于职位分页查询


@app.get("/getAllPositionInfo")
async def get_position_info(
    page: int = 1,
    page_size: int = 20,
    company: str = "",
    position: str = "",
    education: int = None,  # 直接使用整数类型
    skill: str = "",
    address: str = "",
    salary: str = ""
):
    skip = (page - 1) * page_size  # 计算跳过的记录数

    # 查询符合条件的记录总数
    count_query = """
    MATCH (cn:Company)-[:HAS]->(cp:CompanyPosition)-[:POSITION]->(p:Position),
          (cp)-[r:REQUIRES_SKILL]->(sk:Skill),
          (cp)-[:SALARY]->(s:Salary),
          (cp)-[:EDUCATION]->(e:Education),
          (cp)-[:ADDRESS]->(ad:Address),
          (cp)-[:CITY]->(c:City),
          (cp)-[:QUALITY]->(q:Quality)
    WHERE 1=1
    """

    # 动态添加查询条件
    if company:
        count_query += f" AND cn.name CONTAINS '{company}'"
    if position:
        count_query += f" AND p.name CONTAINS '{position}'"
    if education:
        count_query += f" AND e.name = {education}"  # 直接匹配整数
    if skill:
        count_query += f" AND sk.name CONTAINS '{skill}'"
    if address:
        count_query += f" AND ad.name CONTAINS '{address}'"
    if salary:
        count_query += f" AND s.name CONTAINS '{salary}'"

    # 计算所有相关节点的总数
    count_query += """
    RETURN count(p) AS total, 
           count(DISTINCT cn) AS total_companies, 
           count(DISTINCT cp) AS total_company_positions,
           count(DISTINCT sk) AS total_skills,
           count(DISTINCT e) AS total_educations,
           count(DISTINCT ad) AS total_addresses,
           count(DISTINCT c) AS total_cities,
           count(DISTINCT q) AS total_qualities
    """

    total_result = graph.run(count_query).data()
    total = total_result[0]["total"] if total_result else 0
    total_companies = total_result[0]["total_companies"] if total_result else 0
    total_company_positions = total_result[0]["total_company_positions"] if total_result else 0
    total_skills = total_result[0]["total_skills"] if total_result else 0
    total_educations = total_result[0]["total_educations"] if total_result else 0
    total_addresses = total_result[0]["total_addresses"] if total_result else 0
    total_cities = total_result[0]["total_cities"] if total_result else 0
    total_qualities = total_result[0]["total_qualities"] if total_result else 0

    # 查询当前页的数据
    nodes_query = f"""
    MATCH (cn:Company)-[:HAS]->(cp:CompanyPosition)-[:POSITION]->(p:Position),
          (cp)-[r:REQUIRES_SKILL]->(sk:Skill),
          (cp)-[:SALARY]->(s:Salary),
          (cp)-[:EDUCATION]->(e:Education),
          (cp)-[:ADDRESS]->(ad:Address),
          (cp)-[:CITY]->(c:City),
          (cp)-[:QUALITY]->(q:Quality)
    WHERE 1=1
    """

    # 动态添加查询条件
    if company:
        nodes_query += f" AND cn.name CONTAINS '{company}'"
    if position:
        nodes_query += f" AND p.name CONTAINS '{position}'"
    if education:
        nodes_query += f" AND e.name = {education}"  # 直接匹配整数
    if skill:
        nodes_query += f" AND sk.name CONTAINS '{skill}'"
    if address:
        nodes_query += f" AND ad.name CONTAINS '{address}'"
    if salary:
        nodes_query += f" AND s.name CONTAINS '{salary}'"

    nodes_query += f"""
    WITH p.name AS Position, cn.name AS Company, cp.name AS CompanyPosition, collect(sk.name) AS Skills, 
         count(sk) AS skillMatchCount, s.name AS Salary, e.name AS Education, ad.name AS Address, 
         c.name AS City, q.name AS Quality, properties(cp) as Properties
    RETURN Position,
           Company,
           CompanyPosition,
           Skills,
           skillMatchCount,
           Salary,
           Education,
           Address,
           City,
           Quality,
           Properties
    ORDER BY skillMatchCount DESC
    SKIP {skip}  
    LIMIT {page_size}
    """

    nodes = graph.run(nodes_query).data()

    return {
        "message": "数据处理成功",
        "data": {
            "positionInfo": nodes,
            "total": total,  # 职位总数
            "total_companies": total_companies,  # 公司总数
            "total_company_positions": total_company_positions,  # 公司职位总数
            "total_skills": total_skills,  # 技能总数
            "total_educations": total_educations,  # 学历总数
            "total_addresses": total_addresses,  # 地址总数
            "total_cities": total_cities,  # 城市总数
            "total_qualities": total_qualities  # 质量要求总数
        }
    }

# 用户获取AI的建议,后续可以新增type类型来规范需要获取需要什么类容
@app.post("/getRecommendContent")
async def get_recommend_content(resume: Optional[str] = Body(None), selectedPosition: Optional[str] = Body(None), selectedSearchPosition: Optional[str] = Body(None)):
    print("开始获取提升建议")

    # 根据接收到的数据构造响应内容
    content = (
        f"请根据以下内容给出求职建议，并以一段没有特殊格式的文本返回数据，字数限定在100到200之间：\n"
        f"- 用户简历技能：{resume}\n"
        f"- 选定职位所需技能：{selectedPosition}\n"
        f"- 图数据库搜索职位所需技能：{selectedSearchPosition}"
    )
    # print(content)
    client = OpenAI(api_key="sk-d129cd5ff21f408e8c82a327a556a139",
                    base_url="https://api.deepseek.com")

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个职业分析的专家"},
            {"role": "user", "content": content},
        ],
        stream=True
    )

    async def generate():
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/plain")
