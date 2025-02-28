import os
import re
from typing import List, Set
from hanlp_restful import HanLPClient


class TextPreprocessor:
    def __init__(self, hanlp_url: str, hanlp_auth: str, stopwords_path: str, output_directory: str = None):
        """
        初始化文本预处理器

        :param hanlp_url: HanLP API 地址
        :param hanlp_auth: HanLP 认证信息
        :param stopwords_path: 停用词文件路径
        :param output_directory: 输出文件目录，默认为None（使用输入文件的同目录）
        """
        # 初始化 HanLP 客户端
        self.HanLP = HanLPClient(hanlp_url, auth=hanlp_auth, language='zh')

        # 读取停用词表
        self.stopwords = self._load_stopwords(stopwords_path)

        # 设置输出目录
        self.output_directory = output_directory

    def _load_stopwords(self, stopwords_path: str) -> Set[str]:
        """
        加载停用词文件

        :param stopwords_path: 停用词文件路径
        :return: 停用词集合
        """
        try:
            with open(stopwords_path, 'r', encoding='utf-8') as f:
                return set(line.strip() for line in f)
        except FileNotFoundError:
            print(f"警告：停用词文件 {stopwords_path} 未找到")
            return set()

    def preprocess_text(self, text: str) -> List[str]:
        """
        对文本进行预处理：去除空格、清洗文本、分词、去停用词

        :param text: 输入文本
        :return: 处理后的词语列表
        """
        # 去除空格
        content_no_spaces = text.replace(' ', '')

        # 清洗文本，只保留中文、数字和字母
        content_clean = re.sub(r'[^\u4e00-\u9fff0-9a-zA-Z]', '', content_no_spaces)

        # 分词
        cut_content = self.HanLP(content_clean, tasks='tok/coarse').to_dict()
        tokens = cut_content.get('tok/coarse', [])

        # 过滤停用词
        all_filtered_tokens = []
        for segment in tokens:
            filtered_segment = [word for word in segment if word not in self.stopwords]
            all_filtered_tokens.extend(filtered_segment)

        return all_filtered_tokens

    def process_file(self, file_path: str) -> List[str]:
        """
        处理单个文件并保存结果

        :param file_path: 文件路径
        :return: 处理后的词语列表
        """
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # 预处理文本
            processed_tokens = self.preprocess_text(content)

            # 确定输出文件路径
            if self.output_directory:
                # 如果指定了输出目录，使用该目录
                os.makedirs(self.output_directory, exist_ok=True)
                output_filename = os.path.join(self.output_directory, os.path.basename(file_path))
            else:
                # 否则使用原文件的目录
                output_filename = file_path.replace('.txt', '_processed.txt')

            # 保存处理后的词语
            with open(output_filename, 'w', encoding='utf-8') as outfile:
                outfile.write(' '.join(processed_tokens))

            print(f"处理完成：{file_path} -> {output_filename}")

            return processed_tokens

        except FileNotFoundError:
            print(f"文件未找到：{file_path}")
            return []
        except Exception as e:
            print(f"处理文件 {file_path} 时发生错误：{e}")
            return []

    def process_directory(self, directory_path: str, file_extension: str = '.txt') -> dict:
        """
        遍历处理目录下的所有文件

        :param directory_path: 目录路径
        :param file_extension: 要处理的文件扩展名，默认为 .txt
        :return: 文件名到处理结果的字典
        """
        results = {}
        for filename in os.listdir(directory_path):
            if filename.endswith(file_extension):
                file_path = os.path.join(directory_path, filename)
                file_tokens = self.process_file(file_path)
                results[filename] = file_tokens
        return results


def main():
    # 配置参数
    HANLP_URL = 'https://www.hanlp.com/api'
    HANLP_AUTH = 'NzE3MUBiYnMuaGFubHAuY29tOnBhNk9FMUFMTjFqczNmV1o='
    STOPWORDS_PATH = r'D:\中文停用词表.txt'
    INPUT_DIRECTORY = r'D:\proxy_pool'
    OUTPUT_DIRECTORY = r'D:\energypolicytextfile\processed'  # 可选的输出目录

    # 创建预处理器实例，指定输出目录（可选）
    preprocessor = TextPreprocessor(
        HANLP_URL,
        HANLP_AUTH,
        STOPWORDS_PATH,
        output_directory=OUTPUT_DIRECTORY
    )

    # 处理整个目录
    results = preprocessor.process_directory(INPUT_DIRECTORY)

    # 打印每个文件的处理结果
    for filename, tokens in results.items():
        print(f"文件：{filename}")
        print(f"处理后的词语数量：{len(tokens)}")
        print("-" * 50)


if __name__ == "__main__":
    main()




