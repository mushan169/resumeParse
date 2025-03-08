# Please install OpenAI SDK first: `pip3 install openai`

from openai import OpenAI

client = OpenAI(api_key="sk-d129cd5ff21f408e8c82a327a556a139", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "你是一个职业分析的专家"},
        {"role": "user", "content": "可以分析以下目前计算机专业的学生就业前景吗？限定在100字左右"},
    ],
    stream=False
)

print(response.choices[0].message.content)