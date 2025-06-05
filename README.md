# NUM - ML 2025 Spring - Real Estate Assistant
Энэхүү үл хөдлөх хөрөнгийн туслах нь Улаанбаатар хотын үл хөдлөх хөрөнгийн зах зээлийн мэдээллийг цуглуулж, боловсруулж, дүн шинжилгээ хийн 
 линк өгөхөд 5 төрлийн тайлан гаргаж мөн асуусан асуултад хариулдаг болсон. 
| Шаардлага | Хэрэгжүүлсэн файл | 
|-----------|------------------|
| **Vector Store ашиглах** (FAISS/Vertex RAG) | `src/.py` |
| **5 төрлийн тайлан гаргах** | `src/.py` | 
| **Үл хөдлөх хөрөнгийн сайт scraping** (1212.mn/unegui.mn) | `src/.py`, `src/.py` | 
| **Интернэт хайлт нэгтгэх** (Tavily/Bing) | `src/.py` | 
| **PDF тайлан хадгалах** | `src/.py` | 
| **Chain-of-Thought дүн шинжилгээ** | `src/.py` |

## 5 төрлийн тайлангийн ангилал (25 оноо)

### 1. Орон сууцны үнийн дундаж (байршлаар)
- File: `multi_agents/agents/research/district_analysis.py`
- Улаанбаатарын дүүрэг бүрээр орон сууцны дундаж үнэ, м² үнэ тооцоолох
- Chain-of-Thought: Хамгийн хямд дүүргийг зөвлөх 
  
### 2. Түрээсийн зах зээлийн дүн шинжилгээ
- File: `multi_agents/agents/research/rental_analysis.py`
- Үндсэн үүрэг: Түрээсийн үнэ, хугацаа, байршлын харьцуулалт
- Өгөгдлийн эх үүсвэр: unegui.mn веб scraping

### 3. Хувийн орон сууц/байшингийн зах зээлийн мэдээлэл
- File: `src/.py`
- Үндсэн үүрэг: Хотын төв болон захын бүсийн харьцуулалт, эрэлттэй бүсийн дүн шинжилгээ
- Хайлтын нэгтгэл: Bing/Tavily API ашиглалт

### 4. Оффис болон арилжааны талбайн мэдээлэл
- File: `src/.py`
- Үндсэн үүрэг: Арилжааны зориулалттай үл хөдлөх хөрөнгийн үнэ, хэмжээний дүн шинжилгээ

### 5. Нийгмийн аюулгүй байдал (гэмт хэргийн түвшин)
- File: `multi_agents/agents/research/safety_agent.py`
- Өгөгдлийн эх үүсвэр: 1212.mn scraping
- Үзүүлэлтүүд: Хулгай, дээрэм, хүчирхийллийн гэмт хэргийн түвшин

## Хэрэгжүүлэлтийн дэлгэрэнгүй мэдээлэл

### 1. Vector Store 
```python
# faiss_manager.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class FAISSVectorStore:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.index = None
        self.documents = []
    
    def create_index(self, documents):
        embeddings = self.model.encode(documents)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        self.documents = documents
    
    def search(self, query, k=5):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding.astype('float32'), k)
        return [(self.documents[i], distances[0][j]) for j, i in enumerate(indices[0])]
```

### 2. Web scrap
```python
# unegui_scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd

class UneGuiScraper:
    def __init__(self):
        self.base_url = "https://unegui.mn"
    
    def scrape_rental_data(self):
        """unegui.mn에서 임대 정보 크롤링"""
        # 구현 코드
        pass
    
    def save_to_csv(self, data, filename):
       
        df = pd.DataFrame(data)
        df.to_csv(f"data/scraped_data/{filename}", index=False)

# safety_scraper.py
class SafetyScraper:
    def scrape_crime_data(self):
        pass
```

### 3. Web search
```python


```

### 4. Chain-of-Thought 
```python
   
```

### 5. PDF тайлан үүсгэх 
```python
# pdf_generator.py
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
import matplotlib.pyplot as plt

class PDFReportGenerator:
    def __init__(self):
        self.doc = None
        
    def generate_report(self, data):
        """Бүрэн тайланг PDF форматаар үүсгэх"""
        filename = f"reports/real_estate_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        self.doc = SimpleDocTemplate(filename, pagesize=A4)
        
        # Монгол хэлний font дэмжлэг
        story = []
        styles = getSampleStyleSheet()
        
        # Гарчиг нэмэх
        title = Paragraph("ҮЛ ХӨДЛӨХ ХӨРӨНГИЙН ТАЙЛАН", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # 5 бүлгийн тайланг нэмэх
        for section in data:
            story.append(self._create_section(section))
            
        self.doc.build(story)
        return filename
```

##  Файлын бүтэц болон тайлбар

```
real_estate/
├── src/
│   ├── vectorstore/
│   │   └── faiss_manager.py      # FAISS vector store удирдлага (15 оноо)
│   ├── scrapers/
│   │   ├── unegui_scraper.py     # unegui.mn-с мэдээлэл татах (15 оноо)
│   │   └── safety_scraper.py     # 1212.mn-с аюулгүй байдлын мэдээлэл
│   ├── search/
│   │   └── web_search.py         # Tavily/Bing хайлт (15 оноо)
│   ├── analysis/
│   │   ├── cot_analyzer.py       # Chain-of-Thought дүн шинжилгээ (15 оноо)
│   │   ├── housing_price_analyzer.py   # Орон сууцны үнийн дүн шинжилгээ
│   │   ├── rental_analyzer.py          # Түрээсийн зах зээлийн дүн шинжилгээ
│   │   ├── housing_market_analyzer.py  # Хувийн сууцны зах зээл
│   │   ├── commercial_analyzer.py      # Арилжааны талбайн дүн шинжилгээ
│   │   └── safety_analyzer.py          # Аюулгүй байдлын дүн шинжилгээ
│   └── reports/
│       ├── report_generator.py   # 5 төрлийн тайлан үүсгэх (25 оноо)
│       └── pdf_generator.py      # PDF тайлан үүсгэх (15 оноо)
├── data/
│   ├── scraped_data/            # Цуглуулсан өгөгдөл
│   ├── processed_data/          # Боловсруулсан өгөгдөл
│   └── vector_stores/           # FAISS индекс файлууд
├── reports/                     # Үүсгэсэн PDF тайлангууд
├── config/
│   └── settings.py             # API түлхүүр болон тохиргоонууд
├── requirements.txt            # Шаардлагатай library-ууд
└── main.py                     # Гол программ
```















## 💻 Модуль тус бүрийн ашиглалт

### Vector Store ашиглах (15 оноо)
```python
from src.vectorstore.faiss_manager import FAISSVectorStore

# Мэдээллийн сангаас хайлт хийх
vector_store = FAISSVectorStore()
vector_store.load_index("data/vector_stores/property_index.faiss")

# Ижил төстэй мэдээлэл хайх
results = vector_store.search("Сүхбаатар дүүргийн орон сууц", k=5)
```

### Web Scraping ажиллуулах (15 оноо)
```python
from src.scrapers.unegui_scraper import UneGuiScraper
from src.scrapers.safety_scraper import SafetyScraper

# unegui.mn-с мэдээлэл цуглуулах
scraper = UneGuiScraper()
rental_data = scraper.scrape_rental_data()

# 1212.mn-с аюулгүй байдлын мэдээлэл
safety_scraper = SafetyScraper()
crime_data = safety_scraper.scrape_crime_data()
```

### Интернэт хайлт (15 оноо)
```python
from src.search.web_search import WebSearchManager

search_manager = WebSearchManager()

# Tavily-аар хайх
tavily_results = search_manager.search_tavily("Улаанбаатар үл хөдлөх хөрөнгө")

# Bing-ээр хайх
bing_results = search_manager.search_bing("Монгол орон сууцны зах зээл")
```

### Chain-of-Thought дүн шинжилгээ (15 оноо)
```python
from src.analysis.cot_analyzer import ChainOfThoughtAnalyzer

analyzer = ChainOfThoughtAnalyzer()
recommendation = analyzer.analyze_best_district(price_data)

print("Шийдвэрийн алхмууд:")
for step in recommendation['reasoning_steps']:
    print(f"  {step}")
```

### PDF тайлан үүсгэх (15 оноо)
```python
from src.reports.pdf_generator import PDFReportGenerator

pdf_gen = PDFReportGenerator()
report_file = pdf_gen.generate_report(all_analysis_data)
print(f"Тайлан хадгалагдлаа: {report_file}")
```

## 5 төрлийн тайлангийн жишээ (25 оноо)

Систем дараах байдлаар тайлан гаргана:

```
=== ҮЛ ХӨДЛӨХ ХӨРӨНГИЙН ТАЙЛАН ===
Огноо: 2025-06-01

1. ОРОН СУУЦНЫ ҮНИЙН ДУНДАЖ
   Chain-of-Thought дүн шинжилгээ:
   - 1-р алхам: Өгөгдөл цуглуулалт
   - 2-р алхам: Дүүрэг бүрээр ангилалт
   - 3-р алхам: Дундаж үнэ тооцоолол
   - 4-р алхам: Хамгийн хямд бүс олох
   
   Үр дүн: Баянзүрх дүүрэг хамгийн хямд (2,100,000₮/м²)

2. ТҮРЭЭСИЙН ЗАХ ЗЭЭЛ (unegui.mn-с цуглуулсан)
   Татсан мэдээлэл: 1,247 зар
   Дундаж түрээс: 850,000₮/сар
   
3. ХУВИЙН СУУЦНЫ ЗАХ ЗЭЭЛ (Tavily/Bing хайлтаар)
   Веб хайлтын үр дүн: 15 эх сурвалж
   Чиг хандлага: Үнэ 5% өсөх төлөв
   
4. АРИЛЖААНЫ ТАЛБАЙ
   Оффисын дундаж түрээс: 45,000₮/м²/сар
   
5. АЮУЛГҮЙ БАЙДАЛ (1212.mn-с цуглуулсан)
   Хамгийн аюулгүй: Хан-Уул дүүрэг
   Анхаарал хандуулах: Баянгол дүүрэг
```
