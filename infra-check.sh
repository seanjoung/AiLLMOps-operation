#!/bin/bash
#
# Infrastructure Health Check Script
# Automated infrastructure monitoring and reporting
#
# Usage:
#   ./infra-check.sh                    # Default (weekly)
#   ./infra-check.sh --type monthly     # Monthly report
#   ./infra-check.sh --demo             # Demo mode
#   ./infra-check.sh --notify           # Include notifications
#   ./infra-check.sh --help             # Show help
#
# Environment Variables:
#   SLACK_WEBHOOK_URL      - Slack webhook URL
#   TEAMS_WEBHOOK_URL      - Teams webhook URL
#   DISCORD_WEBHOOK_URL    - Discord webhook URL
#   TELEGRAM_BOT_TOKEN     - Telegram bot token
#   TELEGRAM_CHAT_ID       - Telegram chat ID
#   SMTP_PASSWORD          - SMTP password
#

set -e

# Script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/scripts/main.py"
CONFIG_FILE="${SCRIPT_DIR}/config/check_items.yaml"
OUTPUT_DIR="${SCRIPT_DIR}/output"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed."
        exit 1
    fi
    
    # Check and install pip packages
    local packages=("pyyaml" "python-docx" "requests")
    for pkg in "${packages[@]}"; do
        if ! python3 -c "import ${pkg//-/_}" 2>/dev/null; then
            log_warning "${pkg} package not found. Installing..."
            pip3 install ${pkg} --quiet --break-system-packages 2>/dev/null || \
            pip3 install ${pkg} --quiet 2>/dev/null || \
            log_warning "${pkg} installation failed. Some features may be limited."
        fi
    done
    
    log_success "Dependency check completed"
}

# Setup output directory
setup_output_dir() {
    mkdir -p "${OUTPUT_DIR}"
}

# Main execution
main() {
    echo ""
    echo "=============================================="
    echo "  🔍 Infrastructure Health Check System"
    echo "  $(date '+%Y-%m-%d %H:%M:%S')"
    echo "=============================================="
    echo ""
    
    check_dependencies
    setup_output_dir
    
    # Run Python script
    python3 "${PYTHON_SCRIPT}" --config "${CONFIG_FILE}" --output-dir "${OUTPUT_DIR}" "$@"
    
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        log_success "Check completed: All items healthy"
    elif [ $exit_code -eq 1 ]; then
        log_warning "Check completed: Warning items found"
    else
        log_error "Check completed: Critical items found"
    fi
    
    exit $exit_code
}

# Help
show_help() {
    cat << EOF
Infrastructure Health Check Report Generator

Usage:
    $0 [options]

Options:
    --type, -t <weekly|monthly>    Report type (default: weekly)
    --demo                         Demo mode (use sample data)
    --notify, -n                   Send notifications
    --notify-on-issues             Notify only on issues
    --output-dir, -o <path>        Output directory
    --config, -c <path>            Configuration file path
    --json                         Output in JSON format
    --quiet, -q                    Minimal output
    --help, -h                     Show this help

Environment Variables:
    SLACK_WEBHOOK_URL              Slack webhook URL
    TEAMS_WEBHOOK_URL              Microsoft Teams webhook URL
    DISCORD_WEBHOOK_URL            Discord webhook URL
    TELEGRAM_BOT_TOKEN             Telegram bot token
    TELEGRAM_CHAT_ID               Telegram chat ID
    SMTP_PASSWORD                  SMTP password

Examples:
    $0                             # Default run
    $0 --demo                      # Demo mode
    $0 --type monthly --notify     # Monthly report + notifications
    $0 --json                      # JSON output
    
Cron Examples:
    # Weekly check every Monday at 9:00 AM
    0 9 * * 1 /path/to/infra-check.sh --notify >> /var/log/infra-check.log 2>&1
    
    # Monthly check on the 1st at 9:00 AM
    0 9 1 * * /path/to/infra-check.sh --type monthly --notify >> /var/log/infra-check.log 2>&1

EOF
}

# Argument handling
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

main "$@"
