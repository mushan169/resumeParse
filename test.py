import extractData
import itremCF


if __name__ == '__main__':
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

    for item in recommend_positions:
        print(item)