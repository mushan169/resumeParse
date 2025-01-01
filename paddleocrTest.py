import cv2
import time
from paddleocr import PaddleOCR

start = time.time()
# OCR模型识别简历文字
ocr = PaddleOCR(use_angle_cls=True, lang="ch",enable_mkldnn=True)


img_path = './images/1.jpg'
img = cv2.imread(img_path)

result = ocr.ocr(img, cls=True)

full_text = ""
for line in result:
    for word_info in line:
        full_text += word_info[1][0] + " "  # word_info[1][0] 是文字内容

print(full_text.strip())
print(time.time() - start)