import requests
import groq
import os
from dotenv import load_dotenv

from datetime import datetime
from bs4 import BeautifulSoup
from newspaper import Article

from groq import Groq




class ArticleExtractor:
    def __init__(self, groq_api_key):
        # Groq API key
        self.groq_api_key = groq_api_key
        
    def extract_article(self, url):
        # 使用 newspaper3k 提取文章
        article = Article(url)
        article.download()
        article.parse()
        
        return {
            'title': article.title,
            'text': article.text,
            'url': url
        }
    
    def generate_summary(self, text):
        # 使用 Groq 官方客戶端
        client = groq.Client(api_key=self.groq_api_key)
        
        system_prompt = """你是一個專業的文章摘要助手，擅長將文章重點整理成結構化的摘要。
請遵循以下規則：
1. 使用繁體中文
2. 摘要格式：
   主要論點
   關鍵重點（列點式）
   結論或見解
3. 保持客觀專業的語氣
4. 摘要長度控制在300字以內
5. 如果是新聞文章，需包含時間、地點、人物等要素"""

        chat_completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"請幫我摘要以下文章：\n\n{text}"}
            ],
            temperature=0.7,  # 控制創意度
            max_tokens=800    # 控制回應長度
        )
        
        return chat_completion.choices[0].message.content
    
    def create_markdown(self, article_data, summary):
        # 建立 Markdown 格式內容，加入更多資訊
        markdown_content = f"""# {article_data['title']}

## 文章資訊
- 來源網址：{article_data['url']}
- 摘要時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## AI 摘要
{summary}

## 原文內容
{article_data['text']}

---
*此摘要由 AI 自動生成，僅供參考*
"""
        return markdown_content
    
    def save_to_file(self, content, title):
        # 建立輸出目錄
        output_dir = "articles"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 建立檔案名稱（使用日期和標題）
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{date_str}_{title[:30]}.md"
        filename = "".join(c for c in filename if c.isalnum() or c in (' ', '-', '_', '.'))
        
        # 儲存檔案
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath

def main():
    # 從環境變數讀取 Groq API 金鑰
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
    
    if not GROQ_API_KEY:
        raise ValueError("請設定 GROQ_API_KEY 環境變數")
    
    # 初始化擷取器
    extractor = ArticleExtractor(GROQ_API_KEY)
    
    # 取得使用者輸入的網址
    url = input("請輸入文章網址：")
    
    try:
        # 擷取文章
        print("正在擷取文章...")
        article_data = extractor.extract_article(url)
        
        # 生成摘要
        print("正在生成AI摘要...")
        summary = extractor.generate_summary(article_data['text'])
        
        # 建立 Markdown
        markdown_content = extractor.create_markdown(article_data, summary)
        
        # 儲存檔案
        filepath = extractor.save_to_file(markdown_content, article_data['title'])
        
        print(f"文章已成功儲存至：{filepath}")
        
    except Exception as e:
        print(f"發生錯誤：{str(e)}")

# 執行主程式
if __name__ == "__main__":
    main() 
