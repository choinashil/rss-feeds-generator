"""README.md 피드 상태 테이블 업데이트 유틸리티"""
import os
import json
from datetime import datetime


def update_readme_feed_status():
    """
    README.md의 피드 상태 테이블을 업데이트합니다.
    crawl_log.json의 최신 실행 결과를 기반으로 테이블을 생성합니다.
    """
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    readme_path = os.path.join(base_dir, 'README.md')
    log_path = os.path.join(base_dir, 'docs', 'crawl_log.json')
    config_path = os.path.join(base_dir, 'config.json')

    # 로그 파일 읽기
    if not os.path.exists(log_path):
        print("⚠️  crawl_log.json 파일이 없습니다. 테이블을 생성할 수 없습니다.")
        return

    with open(log_path, 'r', encoding='utf-8') as f:
        log_data = json.load(f)

    # history 배열에서 로그 가져오기
    logs = log_data.get('history', [])

    # config 파일 읽기
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 최신 로그만 추출 (각 피드별로 최신 것)
    latest_logs = {}
    for log in reversed(logs):  # 최신 것부터
        feed_id = log['feed']
        if feed_id not in latest_logs:
            latest_logs[feed_id] = log

    # 테이블 생성
    table_lines = [
        "## 피드 상태",
        "",
        "| 피드 | 상태 | 마지막 성공 |",
        "|------|------|------------|"
    ]

    for feed_id, feed_config in config['feeds'].items():
        if not feed_config.get('enabled', True):
            continue

        feed_name = feed_config['name']
        output_file = feed_config['output']

        if feed_id in latest_logs:
            log = latest_logs[feed_id]
            status = "✅" if log['status'] == 'success' else "❌"

            # 마지막 성공 시간 표시
            if log['status'] == 'success':
                # 성공 상태면 그 시간 표시
                timestamp = datetime.fromisoformat(log['timestamp'])
                time_str = timestamp.strftime('%Y-%m-%d %H:%M')
            else:
                # 실패 상태면 마지막 성공한 로그 찾기
                last_success = next(
                    (l for l in reversed(logs) if l['feed'] == feed_id and l['status'] == 'success'),
                    None
                )
                if last_success:
                    timestamp = datetime.fromisoformat(last_success['timestamp'])
                    time_str = timestamp.strftime('%Y-%m-%d %H:%M')
                else:
                    time_str = "-"  # 한 번도 성공한 적 없음
        else:
            status = "⚪"
            time_str = "-"

        table_lines.append(
            f"| {feed_name} | {status} | {time_str} |"
        )

    table_lines.append("")
    table_lines.append(f"*마지막 확인: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)*")
    table_lines.append("")

    # README 읽기
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # 기존 테이블 찾기 및 교체
    start_marker = "## 피드 상태"

    start_idx = readme_content.find(start_marker)

    if start_idx != -1:
        # 기존 테이블 교체 - 피드 상태 섹션부터 파일 끝까지
        new_content = (
            readme_content[:start_idx] +
            '\n'.join(table_lines) + '\n'
        )
    else:
        # 테이블이 없으면 "현재 지원 피드" 섹션 다음에 추가
        support_marker = "## 현재 지원 피드"
        support_idx = readme_content.find(support_marker)

        if support_idx != -1:
            # 다음 섹션(##) 찾기
            next_section_idx = readme_content.find("\n## ", support_idx + len(support_marker))
            if next_section_idx != -1:
                new_content = (
                    readme_content[:next_section_idx] +
                    '\n' + '\n'.join(table_lines) + '\n' +
                    readme_content[next_section_idx:]
                )
            else:
                new_content = readme_content + '\n\n' + '\n'.join(table_lines)
        else:
            new_content = readme_content + '\n\n' + '\n'.join(table_lines)

    # README 쓰기
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print("✅ README.md 피드 상태 테이블 업데이트 완료")


if __name__ == '__main__':
    update_readme_feed_status()
