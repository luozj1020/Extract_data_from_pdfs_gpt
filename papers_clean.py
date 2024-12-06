import os
import shutil
import re
import fitz  # PyMuPDF，用于读取PDF文件
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm

# 加载Sentence-BERT模型
sentence_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 生长条件关键词
growth_conditions = [
    "oxygen pressure", "growth temperature", "laser energy density",
    "post-growth dwell time", "annealing pressure", "annealing rate", "substrate type",
    "substrate orientation", "substrate"
]

# 基本相关关键词（分为两组）
keywords_group_1 = ["SrRuO", "SRO"]
keywords_group_2 = ["PLD", "pulsed laser deposition"]


def extract_text_from_pdf(pdf_path):
    """
    从PDF文件中提取文本
    """
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text")
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text


def extract_text_from_txt(txt_path):
    """
    从TXT文件中提取文本
    """
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()


def contains_keywords(text, keywords):
    """
    检查文本中是否包含给定的关键词（不区分大小写）
    """
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            return True
    return False


def contains_growth_conditions(text, growth_conditions):
    """
    检查文本中是否包含生长条件相关内容
    """
    for condition in growth_conditions:
        if re.search(r'\b' + re.escape(condition) + r'\b', text, re.IGNORECASE):
            return True
    return False


def find_relevant_papers(folder_path):
    """
    从文件夹中筛选包含生长条件和基本关键词相关内容的论文
    """
    relevant_papers = []

    # 遍历文件夹中的所有文件
    for filename in tqdm(os.listdir(folder_path)):
        file_path = os.path.join(folder_path, filename)

        # 仅处理PDF和文本文件
        if filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        else:
            continue

        # 判断是否包含两组关键词
        if contains_keywords(text, keywords_group_1) and contains_keywords(text, keywords_group_2):
            # 检查文本中是否包含生长条件
            if contains_growth_conditions(text, growth_conditions):
                relevant_papers.append(filename)

    return relevant_papers


def save_relevant_papers(source_folder, target_folder, relevant_papers):
    """
    将筛选出的论文复制到新的文件夹
    """
    # 确保目标文件夹存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    for paper in relevant_papers:
        source_path = os.path.join(source_folder, paper)
        target_path = os.path.join(target_folder, paper)

        # 确保目标路径的文件夹存在
        target_dir = os.path.dirname(target_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        try:
            shutil.copy(source_path, target_path)
            print(f"Saved: {paper}")
        except Exception as e:
            print(f"Error saving {paper}: {e}")


# 示例调用
source_folder = './arxiv_papers'
target_folder = './cleaned_papers'

# 获取符合条件的论文
relevant_papers = find_relevant_papers(source_folder)

# 保存符合条件的论文到新文件夹
save_relevant_papers(source_folder, target_folder, relevant_papers)

print("Relevant papers have been saved to:", target_folder)
