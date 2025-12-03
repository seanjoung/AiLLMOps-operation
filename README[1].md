# 인프라 정기점검 보고서 시스템

OS, Kubernetes, K8s 서비스의 15가지 핵심 항목을 점검하고 CSV/DOCX 보고서를 생성하며, 다양한 채널로 알림을 발송하는 자동화 시스템입니다.

## 📋 점검 항목 (15가지)

### OS 점검 (5가지)
| ID | 항목 | 설명 | 임계치 |
|----|------|------|--------|
| OS-001 | 디스크 사용량 | 파일시스템별 디스크 사용률 | 80% |
| OS-002 | 메모리 사용량 | 시스템 메모리 사용률 | 85% |
| OS-003 | CPU 사용량 | CPU 평균 사용률 | 90% |
| OS-004 | 시스템 업타임 | 시스템 가동 시간 | - |
| OS-005 | 좀비 프로세스 | 좀비 프로세스 개수 | 0개 |

### Kubernetes 클러스터 점검 (5가지)
| ID | 항목 | 설명 |
|----|------|------|
| K8S-001 | 노드 상태 | 모든 노드의 Ready 상태 |
| K8S-002 | 노드 리소스 사용량 | 노드별 CPU/Memory 사용률 |
| K8S-003 | 시스템 Pod 상태 | kube-system Pod 상태 |
| K8S-004 | PV/PVC 상태 | 영구 볼륨 바인딩 상태 |
| K8S-005 | 클러스터 이벤트 | 최근 Warning 이벤트 |

### K8s 서비스 점검 (5가지)
| ID | 항목 | 설명 | 임계치 |
|----|------|------|--------|
| SVC-001 | Deployment 상태 | 모든 Deployment Replica 가용성 | - |
| SVC-002 | Service Endpoints | Service Endpoint 연결 상태 | - |
| SVC-003 | Ingress 상태 | Ingress 리소스 및 주소 상태 | - |
| SVC-004 | Pod 재시작 횟수 | 비정상적인 Pod 재시작 감지 | 5회 |
| SVC-005 | CronJob 상태 | CronJob 실행 상태 | - |

## 🚀 빠른 시작

```bash
# 기본 실행 (주간 보고서)
./infra-check.sh

# 월간 보고서 생성
./infra-check.sh --type monthly

# 알림 발송 포함
./infra-check.sh --notify

# 문제 발생시에만 알림
./infra-check.sh --notify-on-issues
```

## 📁 디렉토리 구조

```
infra-check/
├── infra-check.sh          # 메인 실행 스크립트 (Bash)
├── config/
│   └── check_items.yaml    # 점검 항목 및 설정
├── scripts/
│   ├── main.py            # 메인 Python 스크립트
│   ├── checker.py         # 점검 모듈
│   ├── report_generator.py # 보고서 생성 모듈
│   └── notifier.py        # 알림 발송 모듈
├── output/                 # 생성된 보고서
└── README.md
```

## ⚙️ 설정

### config/check_items.yaml

```yaml
# 알림 설정
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender: "infra@company.com"
    recipients:
      - "admin@company.com"
    use_tls: true
    
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#infra-alerts"
    
  teams:
    enabled: false
    webhook_url: "${TEAMS_WEBHOOK_URL}"
    
  discord:
    enabled: false
    webhook_url: "${DISCORD_WEBHOOK_URL}"

# 보고서 설정
report:
  type: "weekly"
  company_name: "회사명"
  team_name: "인프라팀"
  output_dir: "./output"
```

## 🔔 알림 채널 설정

### Slack
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

### Microsoft Teams
```bash
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/YOUR/WEBHOOK/URL"
```

### Discord
```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/YOUR/WEBHOOK"
```

### Telegram
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

### Email (SMTP)
```bash
export SMTP_PASSWORD="your_smtp_password"
```

## 📅 Cron 설정

### 주간 점검 (매주 월요일 09:00)
```cron
0 9 * * 1 /path/to/infra-check.sh --notify-on-issues >> /var/log/infra-check.log 2>&1
```

### 월간 점검 (매월 1일 09:00)
```cron
0 9 1 * * /path/to/infra-check.sh --type monthly --notify >> /var/log/infra-check.log 2>&1
```

## 📊 출력 형식

### CSV
- 엑셀/구글시트에서 바로 열 수 있는 형식
- UTF-8 BOM 지원 (한글 깨짐 방지)

### DOCX
- 전문적인 보고서 형식
- 요약 테이블, 카테고리별 결과, 조치 필요 항목 포함
- 서명란 포함

## 🔧 의존성

### 필수
- Python 3.8+
- PyYAML
- python-docx
- requests

### 선택 (Kubernetes 점검용)
- kubectl (클러스터 접근 권한 필요)

### 설치
```bash
pip install pyyaml python-docx requests
```

## 📤 사용 예시

### Python 직접 사용
```python
from scripts.checker import InfraChecker
from scripts.report_generator import generate_reports, ReportConfig
from scripts.notifier import NotificationConfig, NotificationManager

# 점검 수행
checker = InfraChecker("config/check_items.yaml")
results = checker.run_all_checks()
summary = checker.get_summary()

# 보고서 생성
config = ReportConfig(company_name="우리회사", team_name="DevOps팀")
files = generate_reports(checker.to_dict(), summary, config)

# 알림 발송
notif_config = NotificationConfig(
    slack_enabled=True,
    slack_webhook_url="https://hooks.slack.com/..."
)
manager = NotificationManager(notif_config)
manager.send_all("점검 보고서", "상세 내용", summary, list(files.values()))
```

### JSON 출력
```bash
./infra-check.sh --json > result.json
```

## 🔒 종료 코드

| 코드 | 의미 |
|------|------|
| 0 | 모든 항목 정상 |
| 1 | 경고 항목 있음 |
| 2 | 위험 항목 있음 |

## 📝 커스터마이징

### 점검 항목 추가
`config/check_items.yaml`에서 각 카테고리에 항목 추가:

```yaml
check_items:
  os:
    - id: OS-006
      name: "새 점검 항목"
      description: "설명"
      command: "your_command_here"
      threshold: 80
      unit: "%"
```

### 새 알림 채널 추가
`scripts/notifier.py`에서 `NotificationSender` 클래스 상속:

```python
class MySender(NotificationSender):
    def send(self, title, message, summary, attachments=None):
        # 구현
        pass
```

## 📄 라이선스

MIT License
