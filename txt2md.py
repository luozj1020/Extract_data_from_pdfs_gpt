import os
import shutil


def convert_txt_to_md(source_folder, target_folder):
    """
    将 source_folder 中的 .txt 文件转换为 .md 文件，并保存到 target_folder。
    """
    # 确保目标文件夹存在
    os.makedirs(target_folder, exist_ok=True)

    # 遍历 source_folder 中的所有文件
    for filename in os.listdir(source_folder):
        if filename.endswith(".txt"):  # 只处理 .txt 文件
            source_path = os.path.join(source_folder, filename)
            target_path = os.path.join(target_folder, filename.replace(".txt", ".md"))

            # 读取源文件内容
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 写入到目标文件
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Converted: {filename} -> {os.path.basename(target_path)}")


# 设置文件夹路径
source_folder = "./summary_relation_table"
target_folder = "./summary_relation_table_md"

# 执行转换
convert_txt_to_md(source_folder, target_folder)
