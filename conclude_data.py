import os
import pandas as pd


def read_txt_files_and_aggregate(folder_path):
    """
    读取文件夹中所有 txt 文件，解析表格内容，去除分隔线和无效数据。
    """
    all_data = []

    # 遍历所有 txt 文件
    for file in os.listdir(folder_path):
        if file.endswith(".txt"):
            file_path = os.path.join(folder_path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                # 找到表格数据部分
                data_start = False
                for line in lines:
                    # 判断是否是表头行
                    if "Oxygen Pressure" in line and "|" in line:
                        data_start = True
                        headers = [col.strip() for col in line.split("|")]  # 表头
                        continue

                    if data_start:
                        # 跳过分隔线
                        if line.strip().startswith("|------"):
                            continue

                        # 数据行解析
                        row = [col.strip() for col in line.split("|")]
                        print(row)
                        if len(row) == len(headers):
                            # 判断前三列中"-"的数量是否>=2
                            if row[1:4].count("-") < 2:  # 第一列是 ''
                                all_data.append(row[1:])

    # 创建 DataFrame
    df = pd.DataFrame(all_data, columns=headers[1:])
    return df


def save_aggregated_data_to_csv(df, output_path):
    """
    保存汇总数据到 CSV 文件。
    """
    df.to_csv(output_path, index=False, encoding="utf-8-sig")


# 示例用法
folder_path = "./summary_relation_table"
output_csv_path = "./aggregated_summary.csv"

# 读取并合并所有 txt 文件的数据
aggregated_data_df = read_txt_files_and_aggregate(folder_path)

# 保存为 CSV 文件
save_aggregated_data_to_csv(aggregated_data_df, output_csv_path)

print(f"Aggregated data saved to {output_csv_path}")
