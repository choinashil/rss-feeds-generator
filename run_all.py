"""모든 크롤러 실행"""
import json
import sys
import importlib.util
import os
from utils.logger import CrawlLogger
from utils.readme_updater import update_readme_feed_status


def load_config():
    """설정 파일 로드"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def run_crawler(crawler_name):
    """
    특정 크롤러 실행
    
    Args:
        crawler_name: 크롤러 모듈 이름 (예: 'velog_trending')
        
    Returns:
        bool: 성공 여부
    """
    try:
        # 크롤러 모듈 동적 import
        module_path = f'crawlers/{crawler_name}.py'
        
        if not os.path.exists(module_path):
            print(f"❌ 크롤러를 찾을 수 없습니다: {module_path}")
            return False
        
        # 모듈 로드
        spec = importlib.util.spec_from_file_location(crawler_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # main() 함수 실행
        print(f"\n{'='*60}")
        print(f"🚀 {crawler_name} 실행 중...")
        print(f"{'='*60}")
        
        module.main()
        
        print(f"✅ {crawler_name} 완료\n")
        return True
        
    except Exception as e:
        print(f"❌ {crawler_name} 실패: {e}\n")
        return False


def main():
    """모든 크롤러 실행"""
    print("RSS 피드 생성 시작\n")
    
    # 설정 로드
    config = load_config()
    
    # 활성화된 피드만 실행
    results = {}
    for feed_id, feed_config in config['feeds'].items():
        if feed_config.get('enabled', True):
            crawler_name = feed_config['crawler']
            success = run_crawler(crawler_name)
            results[feed_id] = success
        else:
            print(f"⏭️  {feed_id} - 비활성화됨\n")
    
    # 결과 요약
    print("\n" + "="*60)
    print("📊 실행 결과 요약")
    print("="*60)
    
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for feed_id, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {feed_id}")
    
    print(f"\n성공: {success_count}/{total_count}")
    
    # README.md 피드 상태 테이블 업데이트
    print("\n📝 README.md 업데이트 중...")
    try:
        update_readme_feed_status()
    except Exception as e:
        print(f"⚠️  README 업데이트 실패: {e}")

    # 하나라도 실패하면 exit code 1
    if success_count < total_count:
        sys.exit(1)
    else:
        print("\n🎉 모든 피드 생성 완료!")


if __name__ == '__main__':
    main()
