from fastapi import FastAPI
from pydantic import BaseModel
from py2neo import Graph
import itremCF
import extractData
# # Neo4j 连接配置
# uri = "bolt://localhost:7687"  # 修改为您的 Neo4j 实例地址
# username = "neo4j"  # 修改为您的用户名
# password = "mushanmushan"  # 修改为您的密码

# # 初始化 Neo4j 连接
# graph = Graph(uri, auth=(username, password))

class CompanyPosition(BaseModel):
    name: str
    # 根据实际情况添加其他字段

class Position(BaseModel):
    name: str
    age: int
    salary: str

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/test")
async def test():
    # 提取简历数据
    image_path = "./images/1.jpg"
    output_path = "./result.json"
    resume = extractData.extract_resume_data(image_path, output_path)
    print(resume)

    # 获得推荐的岗位
    city = ['北京市']
    top_n = 20
    recommend_positions = itremCF.recommend_positions_itemcf(
        resume, city, target_position_id=None, top_n=20)

    return recommend_positions
# @app.get("/position")
# async def get_position():
#     query = """
#     MATCH (p:Position {name: '运维工程师'})-[:POSITION]-(cp:CompanyPosition) 
#     RETURN cp, p LIMIT 5
#     """

#     results = graph.run(query).to_data_frame()
#     data = []
#     for index, row in results.iterrows():
#         data.append(row["p"]["name"])
    
#     return data

  