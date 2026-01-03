"""유튜브 네이버 컨퍼런스 영상 크롤러"""
import os
import sys
import json
from datetime import datetime, timezone
import feedparser

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


def crawl_youtube_channel(channel_id, filter_keywords=None, exclude_shorts=False):
    """
    유튜브 채널 RSS를 가져와서 키워드 필터링

    Args:
        channel_id: 유튜브 채널 ID
        filter_keywords: 필터링할 키워드 리스트
        exclude_shorts: 쇼츠 제외 여부 (기본값: False)

    Returns:
        list: 필터링된 영상 정보 리스트
    """
    print(f"유튜브 채널 크롤링 시작... (channel_id: {channel_id})")

    # 유튜브 채널 RSS URL
    rss_url = f'https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}'
    print(f"RSS URL: {rss_url}")

    # RSS 파싱
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        raise Exception("피드에서 항목을 찾을 수 없습니다. 채널 ID를 확인하세요.")

    print(f"✅ 총 {len(feed.entries)}개 영상 발견")

    videos = []

    for entry in feed.entries:
        title = entry.get('title', '')
        link = entry.get('link', '')
        summary = entry.get('summary', '')
        author = entry.get('author', 'Unknown')

        # 쇼츠 제외 옵션 체크
        if exclude_shorts and '/shorts/' in link:
            continue

        # 날짜 파싱 (timezone 정보 포함)
        published = entry.get('published_parsed')
        if published:
            date = datetime(*published[:6], tzinfo=timezone.utc)
        else:
            date = datetime.now(timezone.utc)

        # 키워드 필터링
        if filter_keywords:
            # 제목에 키워드가 포함되어 있는지 확인
            title_lower = title.lower()

            # 키워드 중 하나라도 포함되어 있으면 추가
            matched = False
            for keyword in filter_keywords:
                if keyword.lower() in title_lower:
                    matched = True
                    print(f"  ✅ {title}")
                    break

            if matched:
                videos.append({
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'author': author,
                    'date': date
                })
        else:
            # 필터링 없이 모두 추가
            videos.append({
                'title': title,
                'link': link,
                'summary': summary,
                'author': author,
                'date': date
            })

    if filter_keywords:
        print(f"\n📊 필터링 결과: {len(videos)}개 영상 (전체 {len(feed.entries)}개 중)")
    else:
        print(f"✅ {len(videos)}개 영상 수집 완료")

    return videos


def main():
    """메인 실행 함수"""
    logger = CrawlLogger()

    try:
        # 설정 로드
        config = load_config()
        feed_config = config['feeds']['naver_conference']

        # 크롤링 실행
        channel_id = feed_config['channel_id']
        filter_keywords = feed_config.get('filter_keywords', [])
        exclude_shorts = feed_config.get('exclude_shorts', False)

        videos = crawl_youtube_channel(channel_id, filter_keywords, exclude_shorts)

        # RSS 생성
        feed_info = {
            'title': feed_config['name'],
            'link': f'https://www.youtube.com/channel/{channel_id}',
            'description': feed_config['description']
        }

        output_path = f"docs/{feed_config['output']}"
        os.makedirs('docs', exist_ok=True)

        create_rss_feed(feed_info, videos, output_path)

        # 성공 로그
        if videos:
            logger.log_success(
                'naver_conference',
                len(videos),
                f'{output_path} 생성 완료 (필터: {", ".join(filter_keywords)})'
            )
            print(f"\n✅ RSS 피드 생성 완료: {output_path}")
        else:
            # 영상이 없어도 성공으로 기록 (경고 메시지 포함)
            logger.log_success(
                'naver_conference',
                0,
                f'⚠️ 필터링된 영상 없음 - 빈 RSS 생성: {output_path}'
            )
            print(f"\n⚠️  필터링된 영상이 없어 빈 RSS 피드를 생성했습니다: {output_path}")
            print(f"💡 나중에 키워드에 맞는 영상이 업로드되면 자동으로 추가됩니다.")

    except Exception as e:
        # 실패 로그
        logger.log_failure('naver_conference', str(e))
        raise

    finally:
        logger.save()


if __name__ == '__main__':
    main()
