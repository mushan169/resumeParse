from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from utils import docx2img
from utils import pdf2img
import itremCF
import extractData


app = FastAPI()
# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（可以限制为特定来源）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法（包括 POST、OPTIONS 等）
    allow_headers=["*"],  # 允许所有请求头
)


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

# 查询参数为城市;需要上传简历图片


@app.get("/recommend")
async def recommend(city: str | None = None, top_n: int = 20, target_position_id: int | None = None):
    upload_image_path = "./images/1.jpg"
    output_path = "./result.json"
    resume = extractData.extract_resume_data(upload_image_path, output_path)
    print(resume)

    # 获得推荐的岗位
    recommend_positions = itremCF.recommend_positions_itemcf(
        resume, city, target_position_id, top_n)

    return recommend_positions

# 测试文件的上传


@app.post("/uploadfile")
async def upload(city: str | None = None, top_n: int = 20, target_position_id: int | None = None, file: UploadFile | None = None):
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
        return {"error": "不支持的文件类型", "file_type": file.content_type}

    # return {"message": "文件上传成功"}
    input_path = "./resume.jpg"
    output_path = "./resumeInfo.json"

    resume = extractData.extract_resume_data(input_path, output_path)
    recommend_positions = itremCF.recommend_positions_itemcf(
        resume, city, target_position_id, top_n)

    return recommend_positions
