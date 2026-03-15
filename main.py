import os
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockSnapshotRequest
from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

# 載入 .env 檔案 (本地測試時會用到，Railway 雲端會自動忽略並使用後台變數)
load_dotenv()

app = FastAPI()

# 安全讀取金鑰：從 Railway 後台的 Variables 抓取真實密碼
API_KEY = os.getenv('ALPACA_API_KEY')
API_SECRET = os.getenv('ALPACA_API_SECRET')

@app.get("/")
def read_root():
    return {"訊息": "Railway 伺服器正常運作中！請在網址後面加上 /test 來進行 Alpaca 連線測試。"}

@app.get("/test")
def test_alpaca():
    if not API_KEY or not API_SECRET:
        return {"錯誤": "找不到 API 金鑰！請確認 Railway 後台的 Variables 是否有設定正確。"}
        
    try:
        data_client = StockHistoricalDataClient(API_KEY, API_SECRET)
        news_client = NewsClient(API_KEY, API_SECRET)

        # 測試 A：抓取蘋果 (AAPL) 報價快照
        req = StockSnapshotRequest(symbol_or_symbols="AAPL")
        snap = data_client.get_stock_snapshots(req)["AAPL"]
        
        # 測試 B：抓取蘋果最新 Benzinga 新聞
        news_req = NewsRequest(symbols="AAPL", limit=1)
        news_data = news_client.get_news(news_req)
        news_title = news_data.news[0].headline if news_data.news else "查無最新新聞"

        # 將成功抓取的數據整理成 JSON 格式回傳到網頁
        return {
            "狀態": "✅ Alpaca 連線成功！",
            "測試標的": "AAPL",
            "最新價格": snap.latest_trade.price,
            "今日成交量": snap.volume,
            "最新新聞": news_title
        }
    except Exception as e:
        return {"錯誤": f"連線失敗，原因：{str(e)}"}

if __name__ == "__main__":
    # 讓程式自動抓取 Railway 分配的 PORT 端口
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)