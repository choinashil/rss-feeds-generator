"""로깅 유틸리티"""
import json
import os
from datetime import datetime, timezone


class CrawlLogger:
    """크롤링 결과 로거"""
    
    def __init__(self, log_file='docs/crawl_log.json'):
        self.log_file = log_file
        self.logs = self._load_logs()
        
    def _load_logs(self):
        """기존 로그 불러오기"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {'history': []}
        return {'history': []}
    
    def log_success(self, feed_name, count, message=''):
        """성공 로그 기록"""
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'feed': feed_name,
            'status': 'success',
            'count': count,
            'message': message
        }
        self.logs['history'].append(entry)
        print(f"✅ [{feed_name}] 성공: {count}개 항목 생성")
        
    def log_failure(self, feed_name, error):
        """실패 로그 기록"""
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'feed': feed_name,
            'status': 'failure',
            'error': str(error)
        }
        self.logs['history'].append(entry)
        print(f"❌ [{feed_name}] 실패: {error}")
        
    def save(self):
        """로그 저장"""
        # 최근 100개만 유지
        self.logs['history'] = self.logs['history'][-100:]
        
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.logs, f, ensure_ascii=False, indent=2)
    
    def get_recent_failures(self, hours=24):
        """최근 실패 목록 가져오기"""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(hours=hours)

        failures = [
            log for log in self.logs['history']
            if log['status'] == 'failure'
            and datetime.fromisoformat(log['timestamp']) > cutoff
        ]
        return failures
