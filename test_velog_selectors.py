"""Velog 페이지 구조 분석 스크립트"""
from playwright.sync_api import sync_playwright
import time

def analyze_velog_page():
    """Velog 페이지의 HTML 구조를 분석"""
    print("🔍 Velog 페이지 분석 시작...\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 브라우저 보기
        page = browser.new_page()

        print("📍 페이지 접속 중: https://velog.io/trending/week")
        page.goto('https://velog.io/trending/week', wait_until='networkidle')

        print("⏳ 페이지 렌더링 대기 (3초)...")
        time.sleep(3)

        # article 태그 확인
        print("\n1️⃣ article 태그 검색...")
        articles = page.query_selector_all('article')
        print(f"   ✅ {len(articles)}개 article 발견")

        if articles:
            print("\n2️⃣ 첫 번째 article 구조 분석:")
            first_article = articles[0]

            # HTML 출력
            html = first_article.inner_html()
            print(f"\n   HTML 길이: {len(html)}자")
            print(f"\n   HTML 미리보기:\n{html[:500]}...")

            # 제목 찾기
            print("\n3️⃣ 제목 요소 찾기:")
            for selector in ['h1', 'h2', 'h3', 'h4', 'a']:
                elem = first_article.query_selector(selector)
                if elem:
                    text = elem.inner_text().strip()
                    if text:
                        print(f"   ✅ {selector}: {text[:50]}...")

            # 링크 찾기
            print("\n4️⃣ 링크 요소 찾기:")
            links = first_article.query_selector_all('a')
            for i, link in enumerate(links[:3]):
                href = link.get_attribute('href')
                text = link.inner_text().strip()
                print(f"   {i+1}. href={href}, text={text[:30]}...")

            # 작성자 정보
            print("\n5️⃣ 작성자 정보 찾기:")
            for selector in ['[class*="user"]', '[class*="author"]', '[class*="name"]', 'img[alt]']:
                elem = first_article.query_selector(selector)
                if elem:
                    if elem.tag_name.lower() == 'img':
                        alt = elem.get_attribute('alt')
                        print(f"   ✅ {selector}: alt={alt}")
                    else:
                        text = elem.inner_text().strip()
                        if text:
                            print(f"   ✅ {selector}: {text[:50]}...")
        else:
            print("❌ article 태그를 찾을 수 없습니다!")
            print("\n대체 방법 시도...")

            # 다른 가능한 컨테이너 확인
            selectors_to_try = [
                'a[href*="/@"]',  # Velog는 포스트 링크가 /@username/post-title 형식
                '[class*="Post"]',
                '[class*="post"]',
                '[class*="Card"]',
                '[class*="card"]',
                '[class*="Item"]',
                '[class*="item"]',
                'main a[href^="/@"]',
            ]

            for selector in selectors_to_try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"   ✅ {selector}: {len(elements)}개 발견")
                    if len(elements) > 0:
                        first = elements[0]
                        print(f"      첫 번째 요소:")
                        href = first.get_attribute('href')
                        text = first.inner_text().strip()[:50]
                        html = first.inner_html()[:200]
                        print(f"      href: {href}")
                        print(f"      text: {text}")
                        print(f"      HTML: {html}...")

        print("\n✅ 분석 완료! 브라우저를 10초간 유지합니다...")
        time.sleep(10)
        browser.close()

if __name__ == '__main__':
    analyze_velog_page()
