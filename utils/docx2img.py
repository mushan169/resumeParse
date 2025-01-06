from spire.doc import *
from spire.doc.common import *
from PIL import Image
import io


def convert_docx_to_img(inputFile, outputFile):
    # 创建Document对象
    document = Document()

    # 加载Word文档
    document.LoadFromFile(inputFile)

    # 存储每一页转换的图片
    images = []

    # 遍历文档中的所有页面
    for i in range(document.GetPageCount()):
        # 将指定页面转换为位图（bitmap）
        imageStream = document.SaveImageToStreams(i, ImageType.Bitmap)

        # 将位图（bitmap）转换为PIL.Image对象
        img = Image.open(io.BytesIO(imageStream.ToArray()))
        images.append(img)

    # 获取单页图片的宽度和高度
    widths, heights = zip(*(img.size for img in images))

    # 合并图片：总高度为所有页面高度之和，宽度为最大宽度
    total_width = max(widths)
    total_height = sum(heights)

    # 创建新的空白图像
    merged_image = Image.new(
        "RGB", (total_width, total_height), (255, 255, 255))

    # 将每一页图片粘贴到总图片上
    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height

    # 保存合并后的图片
    merged_image.save(outputFile)

    # 关闭文档
    document.Close()

    print(f"docx文件已转化为jpg")


if __name__ == "__main__":
    inputFile = "test.docx"
    outputFile = "resume.jpg"
    convert_docx_to_img(inputFile, outputFile)
