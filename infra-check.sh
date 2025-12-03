#!/bin/bash
#
# Infrastructure Health Check Script
# 인프라 정기점검 보고서 생성 스크립트
#
# 사용법:
#   ./infra-check.sh                    # 기본 실행 (weekly)
#   ./infra-check.sh --type monthly     # 월간 보고서
#   ./infra-check.sh --notify           # 알림 발송 포함
#   ./infra-check.sh --help             # 도움말
#
# 환경변수:
#   SLACK_WEBHOOK_URL      - Slack 웹훅 URL
#   TEAMS_WEBHOOK_URL      - Teams 웹훅 URL
#   DISCORD_WEBHOOK_URL    - Discord 웹훅 URL
#   TELEGRAM_BOT_TOKEN     - Telegram 봇 토큰
#   TELEGRAM_CHAT_ID       - Telegram 채팅 ID
#   SMTP_PASSWORD          - SMTP 비밀번호
#

set -e

# 스크립트 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/scripts/main.py"
CONFIG_FILE="${SCRIPT_DIR}/config/check_items.yaml"
OUTPUT_DIR="${SCRIPT_DIR}/output"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 의존성 확인
check_dependencies() {
    log_info "의존성 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되어 있지 않습니다."
        exit 1
    fi
    
    # pip 패키지 확인 및 설치
    local packages=("pyyaml" "python-docx" "requests")
    for pkg in "${packages[@]}"; do
        if ! python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            log_warning "${pkg} 패키지가 없습니다. 설치 중..."
            pip3 install ${pkg} --quiet --break-system-packages 2>/dev/null || \
            pip3 install ${pkg} --quiet 2>/dev/null || \
            log_warning "${pkg} 설치 실패. 일부 기능이 제한될 수 있습니다."
        fi
    done
    
    log_success "의존성 확인 완료"
}

# 출력 디렉토리 생성
setup_output_dir() {
    mkdir -p "${OUTPUT_DIR}"
}

# 메인 실행
main() {
    echo ""
    echo "=============================================="
    echo "  🔍 인프라 정기점검 시스템"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=============================================="
    echo ""
    
    check_dependencies
    setup_output_dir
    
    # Python 스크립트 실행
    python3 "${PYTHON_SCRIPT}" --config "${CONFIG_FILE}" --output-dir "${OUTPUT_DIR}" "$@"
    
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        log_success "점검 완료: 모든 항목 정상"
    elif [ $exit_code -eq 1 ]; then
        log_warning "점검 완료: 경고 항목 발견"
    else
        log_error "점검 완료: 위험 항목 발견"
    fi
    
    exit $exit_code
}

# 도움말
show_help() {
    cat << EOF
인프라 정기점검 보고서 생성 스크립트

사용법:
    $0 [옵션]

옵션:
    --type, -t <weekly|monthly>    보고서 유형 (기본: weekly)
    --notify, -n                   알림 발송
    --notify-on-issues             문제 발생시에만 알림
    --output-dir, -o <경로>        출력 디렉토리
    --config, -c <경로>            설정 파일 경로
    --json                         JSON 형식으로 출력
    --quiet, -q                    출력 최소화
    --help, -h                     도움말 출력

환경변수:
    SLACK_WEBHOOK_URL              Slack 웹훅 URL
    TEAMS_WEBHOOK_URL              Microsoft Teams 웹훅 URL
    DISCORD_WEBHOOK_URL            Discord 웹훅 URL
    TELEGRAM_BOT_TOKEN             Telegram 봇 토큰
    TELEGRAM_CHAT_ID               Telegram 채팅 ID
    SMTP_PASSWORD                  SMTP 비밀번호

예시:
    $0                             # 기본 실행
    $0 --type monthly --notify     # 월간 보고서 + 알림
    $0 --json                      # JSON 출력
    
Cron 예시:
    # 매주 월요일 오전 9시 실행
    0 9 * * 1 /path/to/infra-check.sh --notify-on-issues >> /var/log/infra-check.log 2>&1
    
    # 매월 1일 오전 9시 실행
    0 9 1 * * /path/to/infra-check.sh --type monthly --notify >> /var/log/infra-check.log 2>&1

EOF
}

# 인자 처리
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

main "$@"
