.PHONY: help install setup test run clean serve update-readme

# 가상환경 Python 경로
VENV_PYTHON = ./venv/bin/python
VENV_PIP = ./venv/bin/pip

help:
	@echo "사용 가능한 명령어:"
	@echo "  make setup         - 초기 설정 (가상환경 + 의존성 설치)"
	@echo "  make install       - 의존성만 설치"
	@echo "  make test          - 개별 크롤러 테스트"
	@echo "  make run           - 모든 크롤러 실행"
	@echo "  make update-readme - README.md 피드 상태 업데이트"
	@echo "  make serve         - 로컬 서버로 RSS 확인"
	@echo "  make clean         - 생성된 파일 정리"

setup:
	@echo "🔧 초기 설정 중..."
	python3 -m venv venv
	@echo "✅ 가상환경 생성 완료"
	@echo "⚙️  의존성 설치 중..."
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PYTHON) -m playwright install chromium
	@echo "✅ 설정 완료!"
	@echo ""
	@echo "💡 이제 바로 실행하세요:"
	@echo "   make run"

install:
	@echo "📦 의존성 설치 중..."
	$(VENV_PIP) install -r requirements.txt
	$(VENV_PYTHON) -m playwright install chromium
	@echo "✅ 설치 완료!"

test:
	@echo "🧪 개별 크롤러 테스트"
	@echo ""
	@echo "1️⃣  Velog 트렌딩 테스트..."
	$(VENV_PYTHON) crawlers/velog_trending.py
	@echo ""
	@echo "2️⃣  네이버 유튜브 테스트..."
	$(VENV_PYTHON) crawlers/youtube_naver.py
	@echo ""
	@echo "3️⃣  인프런 유튜브 테스트..."
	$(VENV_PYTHON) crawlers/youtube_inflearn.py
	@echo ""
	@echo "✅ 테스트 완료! docs/ 폴더를 확인하세요"

run:
	@echo "🚀 모든 크롤러 실행 중..."
	$(VENV_PYTHON) run_all.py
	@echo ""
	@echo "📁 생성된 파일:"
	@ls -lh docs/*.xml 2>/dev/null || echo "   RSS 파일이 없습니다"
	@echo ""
	@echo "💡 로컬에서 확인: make serve"

serve:
	@echo "🌐 로컬 서버 시작..."
	@echo ""
	@echo "📍 RSS 피드 URL:"
	@echo "   http://localhost:8000/velog-trending.xml"
	@echo "   http://localhost:8000/naver-conference.xml"
	@echo "   http://localhost:8000/inflearn-conference.xml"
	@echo "   http://localhost:8000/crawl_log.json"
	@echo ""
	@echo "🛑 종료: Ctrl+C"
	@echo ""
	cd docs && $(VENV_PYTHON) -m http.server 8000

update-readme:
	@echo "📝 README.md 피드 상태 업데이트 중..."
	$(VENV_PYTHON) utils/readme_updater.py
	@echo "✅ 업데이트 완료!"

clean:
	@echo "🗑️  생성된 파일 정리 중..."
	rm -rf docs/*.xml docs/crawl_log.json
	rm -rf __pycache__ crawlers/__pycache__ utils/__pycache__
	@echo "✅ 정리 완료!"