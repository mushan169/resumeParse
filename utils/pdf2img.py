from spire.pdf.common import *
from spire.pdf import *


def convert_pdf_to_image(inputFile,outputFile):
    # 创建PdfDocument对象
    pdf = PdfDocument()

    # 加载PDF文档
    pdf.LoadFromFile(inputFile)

    # pages_num = pdf.Pages.Count
    # print(pages_num)
    # for i in range(0): 
        # 将指定PDF页面转换为图片
    with pdf.SaveAsImage(0) as imageS: # 默认只提取pdf的第一页
        # 将图片保存为jpg格式
        imageS.Save(outputFile)
    pdf.Close()

if __name__ == '__main__':
    inputFile = "test.pdf"
    outputFile = "resume.jpg"
    convert_pdf_to_image(inputFile, outputFile)