import os
import re
import fitz  # PyMuPDF 用于读取PDF文件
from openai import OpenAI
from tqdm import tqdm


client = OpenAI(
    base_url="",
    api_key=""
)


# 读取 PDF 文件并提取全文文本
def extract_full_text(pdf_path):
    """
    从 PDF 文件中提取全文文本。去除 Abstract 部分之前的内容和 References 部分之后的内容。
    """
    full_text = ""

    try:
        doc = fitz.open(pdf_path)

        # 获取每页的文本内容
        for page in doc:
            full_text += page.get_text("text")  # 获取整页文本

        # 去除 Abstract 之前的部分（不区分大小写）
        abstract_start = re.search(r'\babstract\b', full_text, re.IGNORECASE)
        if abstract_start:
            full_text = full_text[abstract_start.start():]  # 保留从 Abstract 开始的部分

        # 去除 References 之后的部分（不区分大小写）
        references_start = re.search(r'\breferences\b', full_text, re.IGNORECASE)
        if references_start:
            full_text = full_text[:references_start.start()]  # 保留到 References 之前的部分

    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")

    return full_text

# 使用GPT模型总结薄膜生长条件和物性信息
def summarize_detailed_info(paragraphs, model="gpt-4o-mini-2024-07-18", max_tokens=1000):
    """
    提取生长条件和物性数据，并建立对应关系，生成表格格式。
    数据中直接包含单位，缺失数据用 '-' 填充。
    """
    text = "\n".join(paragraphs)
    prompt = (
        f"Extract detailed information from the following text about the pulsed laser deposition (PLD) "
        f"growth conditions and properties of SrRuO3 thin films. Specifically, create a table where each row "
        f"represents a specific set of conditions and their results. Columns should include:\n"
        f"1. Oxygen Pressure (e.g., '10 Pa')\n"
        f"2. Growth Temperature (e.g., '700 °C')\n"
        f"3. Laser Energy Density (e.g., '2 J/cm²')\n"
        f"4. Post-growth Dwell Time (e.g., '300 s')\n"
        f"5. Annealing Pressure (e.g., '100 Pa')\n"
        f"6. Annealing Rate (e.g., '5 °C/min')\n"
        f"7. Substrate Type (including orientation)\n"
        f"8. Crystallinity\n"
        f"9. Roughness (e.g., '1.2 nm')\n"
        f"10. Tc (e.g., '150 K')\n"
        f"11. Magnetic Moment (e.g., '1.5 μB')\n"
        f"12. Description (relevant observations or results).\n\n"
        f"Use '-' for missing values. Text: {text}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert in material science, specializing in summarizing experimental data."},
            {"role": "user", "content": prompt}
        ],
    )
    table_text = response.choices[0].message.content
    return table_text
'''
def summarize_detailed_info(text, model="gpt-4o-mini-2024-07-18", max_tokens=1000):
    """
    用 GPT 提取薄膜生长条件与物性之间的对应关系，返回表格格式。
    表格的列包括：
    - 第一列：生长条件（包括多个参数，用分号隔开）
    - 第二列：物性名称
    - 第三列：物性数值（如果没有则记录"-"）
    - 第四列：物性描述
    """
    prompt = (
        "Analyze the text and summarize the relationship between growth conditions and film properties. "
        "Please organize the results into a table with the following columns:\n"
        "1. Growth Conditions: [Specific growth conditions, e.g. oxygen pressure: 1 Pa; growth temperature: 700°C; etc.]\n"
        "2. Property Name: [Name of the property, e.g., crystallinity, roughness, Tc, magnetic moment]\n"
        "3. Property Value: [Specific value of the property, e.g. high, low, 150 K, 1.5 µB, or '-']\n"
        "4. Property Description: [A brief description of the property, e.g., high crystallinity means well-ordered structure]\n\n"
        "For example:\n"
        "| Growth Conditions        | Property Name  | Property Value | Property Description  |\n"
        "| ------------------------ | -------------- | -------------- | --------------------- |\n"
        "| Oxygen pressure: 1 Pa; Growth temperature: 700°C; Substrate type: SrTiO3    | Crystallinity  | High           | Well-ordered structure |\n"
        f"Text: {text}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a materials scientist assistant. You will extract growth conditions and their corresponding properties from the provided text."},
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content

def summarize_detailed_info(paragraphs, model="gpt-4o-mini-2024-07-18", max_tokens=1000):
    """
    用 GPT 提取薄膜生长条件和物性信息
    """
    text = "\n".join(paragraphs)
    prompt = (
        f"Extract and summarize the key pulsed laser deposition (PLD) growth conditions of SrRuO3 thin films and film properties related to the process. "
        f"Include details such as oxygen pressure, growth temperature, laser energy density, substrate type, "
        f"annealing conditions, crystallinity, roughness, magnetic properties (e.g., Tc, moment), and any other relevant information.\n\n"
        f"Text: {text}"
    )
    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "system",
            "content": "You are a materials scientist assistant."},
            {"role": "user", "content": prompt}
        ],
    )
    return response.choices[0].message.content
'''

# 处理长文本，将其拆分为多个部分，并逐个传递给 GPT 进行总结
def process_long_text(full_text, model="gpt-4o-mini-2024-07-18", max_tokens=1000):
    """
    动态调整输入长度，逐步缩短文本块，直到成功处理或分段达到限制。
    """
    def try_summarize(text):
        try:
            return summarize_detailed_info(text, model=model, max_tokens=max_tokens)
        except Exception as e:
            if "context_length_exceeded" in str(e):
                return None
            else:
                raise e

    max_retries = 100  # 最多允许100段
    for num_parts in range(1, max_retries + 1):
        if num_parts == 1:
            # 尝试整段输入
            summary = try_summarize(full_text)
            if summary:
                return summary
        else:
            # 将文本拆分为 num_parts 段
            part_length = len(full_text) // num_parts
            parts = [
                full_text[i * part_length: (i + 1) * part_length]
                for i in range(num_parts - 1)
            ]
            parts.append(full_text[(num_parts - 1) * part_length:])  # 加入剩余部分
            summaries = []
            try:
                for part in parts:
                    part_summary = try_summarize(part)
                    if part_summary:
                        summaries.append(part_summary)
                    else:
                        break
                if len(summaries) == num_parts:  # 确保所有部分都处理成功
                    return "\n".join(summaries)
            except Exception as e:
                print(f"Error while processing {num_parts} parts: {e}")
                continue

    raise ValueError("Text could not be processed even after splitting into smaller parts.")



# 选择 cleaned_papers 文件夹中的第二篇论文开始
def process_papers_from_folder(folder_path, output_path, start_index=1):
    # 获取文件夹中所有文件的列表，并排序
    files = sorted(os.listdir(folder_path))

    for index, filename in tqdm(enumerate(files[start_index:], start=start_index)):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            # 提取论文的全文文本
            full_text = extract_full_text(file_path)
            # 对长文本进行处理
            summary = process_long_text(full_text)
            print(summary)

            # 将总结保存到 './summary' 文件夹
            summary_folder = output_path
            os.makedirs(summary_folder, exist_ok=True)
            summary_filename = f"{os.path.splitext(filename)[0]}.txt"  # 用原文件名作为总结文件名
            summary_path = os.path.join(summary_folder, summary_filename)

            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)

            print(f"Summary saved for {filename} at {summary_path}")



# 示例调用
folder_path = './cleaned_papers'
output_path = './summary_relation_table'
process_papers_from_folder(folder_path, start_index=0)
