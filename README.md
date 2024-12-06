# Extract_data_from_pdfs_gpt

`arxiv_spider.py` 从 arxiv 上下载相关论文，`papers_clean.py` 进行筛选

接着 `chatgpt_summary.py` 用 gpt 总结论文中的数据，`conclude_data.py` 对总结的数据进行筛选和汇总

`txt2md.py` 将指定文件夹中的 txt 文件转换成 md 文件方便查看（因为 gpt 返回的都是 markdown 语句）

`aggregated_summary.csv` 是得到的示例数据
