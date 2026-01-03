"""RSS 피드 생성 유틸리티"""
from datetime import datetime
from feedgen.feed import FeedGenerator


def create_rss_feed(feed_info, posts, output_path):
    """
    RSS 피드 생성
    
    Args:
        feed_info: 피드 정보 딕셔너리 (title, link, description 등)
        posts: 게시글 리스트 (각각 title, link, summary, author, date 포함)
        output_path: 저장 경로
    """
    fg = FeedGenerator()
    fg.id(feed_info['link'])
    fg.title(feed_info['title'])
    fg.author({'name': feed_info.get('author', 'RSS Feed Generator')})
    fg.link(href=feed_info['link'], rel='alternate')
    fg.description(feed_info['description'])
    fg.language('ko')
    
    # posts를 역순으로 추가하여 RSS에서 원래 순서 유지
    for post in reversed(posts):
        fe = fg.add_entry()
        fe.id(post['link'])
        fe.title(post['title'])
        fe.link(href=post['link'])
        fe.description(post.get('summary', ''))

        if 'author' in post:
            fe.author({'name': post['author']})

        # 날짜가 있으면 사용, 없으면 현재 시간
        pub_date = post.get('date', datetime.now())
        fe.published(pub_date)
    
    # RSS 파일 저장
    fg.rss_file(output_path, pretty=True)
    return output_path
