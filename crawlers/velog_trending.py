"""Velog 트렌딩 페이지 크롤러"""
import os
import sys
import re
import json
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

# 상위 디렉토리 모듈 import를 위한 경로 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.rss_generator import create_rss_feed
from utils.logger import CrawlLogger


def load_config():
    """설정 파일 로드"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'config.json'
    )
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_velog_date(date_text):
    """
    Velog 날짜 텍스트를 datetime 객체로 변환

    Args:
        date_text: "2025년 12월 21일" 또는 "6일 전" 형식

    Returns:
        datetime: UTC timezone이 적용된 datetime 객체
    """
    date_text = date_text.strip()

    # 절대 날짜 형식: "2025년 12월 21일"
    absolute_pattern = r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'
    match = re.match(absolute_pattern, date_text)
    if match:
        year, month, day = map(int, match.groups())
        return datetime(year, month, day, tzinfo=timezone.utc)

    # 상대 시간 형식: "X일 전", "X시간 전", "X분 전"
    now = datetime.now(timezone.utc)

    if '일 전' in date_text:
        days = int(re.search(r'(\d+)일', date_text).group(1))
        return now - timedelta(days=days)
    elif '시간 전' in date_text:
        hours = int(re.search(r'(\d+)시간', date_text).group(1))
        return now - timedelta(hours=hours)
    elif '분 전' in date_text:
        minutes = int(re.search(r'(\d+)분', date_text).group(1))
        return now - timedelta(minutes=minutes)
    elif '방금' in date_text or '초 전' in date_text:
        return now

    # 파싱 실패 시 현재 시간 반환
    return now


def crawl_velog_trending(max_items=20):
    """
    Velog 트렌딩 페이지 크롤링

    Args:
        max_items: 최대 수집 개수

    Returns:
        list: 게시글 정보 리스트
    """
    print("Velog 트렌딩 크롤링 시작...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Velog 트렌딩 페이지 접속 (week 단위)
        page.goto('https://velog.io/trending/week', wait_until='networkidle', timeout=30000)

        # JavaScript 렌더링 대기
        page.wait_for_selector('h4[class*="PostCard"]', timeout=30000)

        posts = []
        seen_links = set()  # 중복 제거

        # 포스트 카드(li 태그) 기준으로 수집
        cards = page.query_selector_all('li[class*="PostCard"]')
        print(f"✅ 총 {len(cards)}개 게시글 발견")

        for card in cards[:max_items]:
            try:
                # 제목 (h4 태그)
                title_elem = card.query_selector('h4[class*="PostCard"]')
                if not title_elem:
                    continue
                title = title_elem.inner_text().strip()

                # 링크 (a 태그)
                link_elem = card.query_selector('a[href*="/@"]')
                if not link_elem:
                    continue
                link = link_elem.get_attribute('href')

                # 전체 URL 만들기
                if link and not link.startswith('http'):
                    link = f'https://velog.io{link}' if link.startswith('/') else link

                # 중복 체크
                if link in seen_links:
                    continue
                seen_links.add(link)

                # 요약 (p.PostCard_clamp___2g_C)
                summary = ''
                summary_elem = card.query_selector('p[class*="PostCard_clamp"]')
                if summary_elem:
                    summary = summary_elem.inner_text().strip()

                # 작성자 (footer 영역의 b 태그)
                author = 'Unknown'
                author_elem = card.query_selector('div[class*="PostCard_footer"] b')
                if author_elem:
                    author = author_elem.inner_text().strip()

                # 날짜 (PostCard_subInfo 내부의 첫 번째 span)
                date = datetime.now(timezone.utc)
                date_elem = card.query_selector('div[class*="PostCard_subInfo"] span')
                if date_elem:
                    date_text = date_elem.inner_text().strip()
                    date = parse_velog_date(date_text)

                posts.append({
                    'title': title,
                    'link': link,
                    'summary': summary[:500] if summary else '',
                    'author': author,
                    'date': date
                })

            except Exception as e:
                print(f"  ⚠️  게시글 파싱 오류: {e}")
                continue

        browser.close()

    print(f"\n📊 수집 결과: {len(posts)}개 게시글")
    return posts


def main():
    """메인 실행 함수"""
    logger = CrawlLogger()

    try:
        # 설정 로드
        config = load_config()
        feed_config = config['feeds']['velog_trending']

        # 크롤링 실행
        posts = crawl_velog_trending(max_items=20)

        if not posts:
            raise Exception("수집된 게시글이 없습니다")

        # RSS 생성
        feed_info = {
            'title': feed_config['name'],
            'link': 'https://velog.io/trending',
            'description': feed_config['description']
        }

        output_path = f"docs/{feed_config['output']}"
        os.makedirs('docs', exist_ok=True)

        create_rss_feed(feed_info, posts, output_path)

        # 성공 로그
        logger.log_success('velog_trending', len(posts), f'{output_path} 생성 완료')

    except Exception as e:
        # 실패 로그
        logger.log_failure('velog_trending', str(e))
        raise

    finally:
        logger.save()


if __name__ == '__main__':
    main()
