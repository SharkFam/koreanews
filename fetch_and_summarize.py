import os
import feedparser
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
import markdown  # 파일 상단에 추가

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 주제별 RSS 링크
RSS_TOPICS = {
    "latest": ("최신기사", "https://www.yna.co.kr/rss/news.xml"),
    "politics": ("정치", "https://www.yna.co.kr/rss/politics.xml"),
    "northkorea": ("북한", "https://www.yna.co.kr/rss/northkorea.xml"),
    "economy": ("경제", "https://www.yna.co.kr/rss/economy.xml"),
    "market": ("마켓", "https://www.yna.co.kr/rss/market.xml"),
    "industry": ("산업", "https://www.yna.co.kr/rss/industry.xml"),
    "society": ("사회", "https://www.yna.co.kr/rss/society.xml"),
    "local": ("전국", "https://www.yna.co.kr/rss/local.xml"),
    "international": ("세계", "https://www.yna.co.kr/rss/international.xml"),
    "culture": ("문화", "https://www.yna.co.kr/rss/culture.xml"),
    "health": ("건강", "https://www.yna.co.kr/rss/health.xml"),
    "entertainment": ("연예", "https://www.yna.co.kr/rss/entertainment.xml"),
    "sports": ("스포츠", "https://www.yna.co.kr/rss/sports.xml"),
    "people": ("사람들", "https://www.yna.co.kr/rss/people.xml"),
    "opinion": ("오피니언", "https://www.yna.co.kr/rss/opinion.xml"),
}

def fetch_titles_and_links(rss_url):
    feed = feedparser.parse(rss_url)
    # (제목, 링크) 튜플 리스트 반환
    return [(entry.title, entry.link) for entry in feed.entries[:10]]

def summarize_with_gemini(titles, topic_kr):
    prompt = (
        f"다음은 오늘 대한민국 {topic_kr} 주요 뉴스 제목입니다. "
        "각 제목을 참고하여 오늘의 이슈를 5문장 이내로 요약해 주세요.\n"
        + "\n".join(titles)
    )
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text

def save_html(titles_and_links, summary, date_str, topic, topic_kr):
    # news 폴더 대신 루트에 저장
    # 마크다운을 HTML로 변환
    summary_html = markdown.markdown(summary)
    # 탭/햄버거 메뉴용 주제 리스트
    tab_html = " ".join([
        '<a class="tab{}" href="latest_{}.html">{}</a>'.format(
            ' active' if t == topic else '', t, kr
        ) for t, (kr, _) in RSS_TOPICS.items()
    ])
    menu_items = "".join([
        '<a class="menu-item{}" href="latest_{}.html">{}</a>'.format(
            ' active' if t == topic else '', t, kr
        ) for t, (kr, _) in RSS_TOPICS.items()
    ])
    news_list = "\n".join([
        f'<li><a href="{link}" target="_blank" rel="noopener">{title}</a></li>'
        for title, link in titles_and_links
    ])
    html = f"""<!DOCTYPE html>
<html lang=\"ko\">
<head>
  <meta charset=\"UTF-8\">
  <title>{date_str} {topic_kr} 뉴스 요약</title>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <style>
    body {{ font-family: 'Noto Sans KR', sans-serif; margin: 2rem; background: #f9f9f9; color: #222; }}
    h1 {{ color: #0055a5; }}
    .summary {{ background: #e3f0ff; padding: 1rem; border-radius: 8px; margin-bottom: 2rem; }}
    ul {{ padding-left: 1.2rem; }}
    li {{ margin-bottom: 0.5rem; }}
    .date {{ color: #888; font-size: 0.95em; margin-bottom: 1rem; }}
    .tabs {{ margin-bottom: 2rem; }}
    .tab {{ display: inline-block; margin-right: 1rem; padding: 0.5rem 1rem; background: #eee; border-radius: 5px; text-decoration: none; color: #0055a5; }}
    .tab.active {{ background: #0055a5; color: #fff; }}
    .menu-btn {{ display: none; position: fixed; top: 1.2rem; right: 2rem; z-index: 100; width: 36px; height: 36px; background: #0055a5; border: none; border-radius: 5px; color: #fff; font-size: 2rem; align-items: center; justify-content: center; }}
    .menu-panel {{ display: none; position: fixed; top: 0; right: 0; width: 220px; height: 100%; background: #fff; box-shadow: -2px 0 8px rgba(0,0,0,0.1); z-index: 200; padding: 2rem 1rem; }}
    .menu-item {{ display: block; margin-bottom: 1.2rem; font-size: 1.1em; color: #0055a5; text-decoration: none; }}
    .menu-item.active {{ font-weight: bold; color: #222; }}
    @media (max-width: 800px) {{
      .tabs {{ display: none; }}
      .menu-btn {{ display: flex; }}
    }}
    @media (min-width: 801px) {{
      .menu-btn, .menu-panel {{ display: none !important; }}
      .tabs {{ display: block; }}
    }}
  </style>
</head>
<body>
  <button class=\"menu-btn\" id=\"menuBtn\" aria-label=\"주제 메뉴 열기\">☰</button>
  <div class=\"menu-panel\" id=\"menuPanel\">
    <div style=\"text-align:right; margin-bottom:2rem;\"><button onclick=\"closeMenu()\" style=\"font-size:1.5em; background:none; border:none; color:#0055a5;\">×</button></div>
    {menu_items}
  </div>
  <div class=\"tabs\">
    {tab_html}
  </div>
  <h1>{topic_kr} 뉴스 요약</h1>
  <div class=\"date\">날짜: {date_str} - 뉴스는 매일 오전 9시,오후 12시,오후 5시,오후 9시에 갱신됩니다</div>
  <div class=\"summary\">{summary_html}</div>
  <h2>주요 뉴스 제목</h2>
  <ul>
    {news_list}
  </ul>
  <footer style=\"margin-top:2rem;font-size:0.9em;color:#aaa;\">Powered by Google Gemini & 연합뉴스</footer>
  <script>
    const menuBtn = document.getElementById('menuBtn');
    const menuPanel = document.getElementById('menuPanel');
    menuBtn.onclick = function() {{
      menuPanel.style.display = 'block';
      document.body.style.overflow = 'hidden';
    }};
    function closeMenu() {{
      menuPanel.style.display = 'none';
      document.body.style.overflow = '';
    }}
    window.closeMenu = closeMenu;
    // 바깥 클릭 시 닫기
    menuPanel.addEventListener('click', function(e) {{
      if (e.target === menuPanel) closeMenu();
    }});
  </script>
</body>
</html>
"""
    with open(f'latest_{topic}.html', 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    for topic, (topic_kr, rss_url) in RSS_TOPICS.items():
        print(f'[{topic_kr}] 뉴스 수집 중...')
        titles_and_links = fetch_titles_and_links(rss_url)
        if not titles_and_links:
            print(f'[{topic_kr}] 뉴스 없음 또는 수집 실패!')
            continue
        titles = [title for title, _ in titles_and_links]
        print(f'[{topic_kr}] Gemini 요약 중...')
        summary = summarize_with_gemini(titles, topic_kr)
        print(f'[{topic_kr}] HTML 저장 중...')
        save_html(titles_and_links, summary, date_str, topic, topic_kr)
        print(f'[{topic_kr}] 저장 완료!')
    print('모든 주제 처리 완료.')

if __name__ == '__main__':
    main()
