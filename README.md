# 🔍 AI, LLM, K8s Infrastructure Health Check System
# Made by Hwiwon Joung(정휘원, Sean)

**인프라 정기점검 자동화 시스템**

OS, Kubernetes 클러스터, K8s 서비스를 자동으로 점검하고 CSV/DOCX 보고서를 생성하며, 다양한 채널(Email, Slack, Teams, Discord, Telegram)로 알림을 발송하는 자동화 도구입니다.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Bash](https://img.shields.io/badge/bash-5.0+-orange.svg)

---

## 📋 목차

- [주요 기능](#-주요-기능)
- [점검 항목](#-점검-항목-30가지)
- [프로젝트 구조](#-프로젝트-구조)
- [설치 방법](#-설치-방법)
- [사용 방법](#-사용-방법)
- [설정 가이드](#️-설정-가이드)
- [알림 채널 설정](#-알림-채널-설정)
- [Cron 스케줄링](#-cron-스케줄링)
- [출력 예시](#-출력-예시)
- [커스터마이징](#-커스터마이징)
- [트러블슈팅](#-트러블슈팅)
- [라이선스](#-라이선스)

---

<img width="1007" height="1010" alt="521780824-2e6216e2-a129-42eb-b81d-bd7c88de0790" src="https://github.com/user-attachments/assets/41414114-f520-418e-92e9-deb2a7a42099" />


<img width="859" height="988" alt="521780306-46f72405-b88f-435b-8379-530bceffb47a" src="https://github.com/user-attachments/assets/8c26b1a3-ae2f-475d-8a36-31e06c7a4566" />



## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🖥️ **OS 점검** | 디스크, 메모리, CPU, 프로세스 등 10개 항목 |
| ☸️ **K8s 클러스터 점검** | 노드, Pod, PV/PVC, 이벤트 등 10개 항목 |
| 🚀 **K8s 서비스 점검** | Deployment, StatefulSet, Ingress 등 10개 항목 |
| 📊 **보고서 생성** | CSV, DOCX 형식 자동 생성 |
| 🔔 **다채널 알림** | Email, Slack, Teams, Discord, Telegram, Webhook |
| ⏰ **스케줄링** | Cron을 통한 주간/월간 자동 실행 |
| 🎭 **데모 모드** | kubectl 없이도 테스트 가능 |

---

## 📋 점검 항목 (30가지)

### 🖥️ OS 점검 (10개)

| ID | 점검 항목 | 설명 | 임계치 |
|----|----------|------|--------|
| OS-001 | 디스크 사용량 | 루트 파일시스템 사용률 | 80% |
| OS-002 | 메모리 사용량 | 시스템 메모리 사용률 | 85% |
| OS-003 | CPU 사용량 | CPU 평균 사용률 | 90% |
| OS-004 | 시스템 업타임 | 시스템 가동 시간 | - |
| OS-005 | 좀비 프로세스 | 좀비 프로세스 개수 | 0개 |
| OS-006 | 로드 애버리지 | 1분 평균 로드 | 4.0 |
| OS-007 | Swap 사용량 | Swap 메모리 사용률 | 50% |
| OS-008 | 열린 파일 수 | 파일 디스크립터 수 | 50,000개 |
| OS-009 | 네트워크 연결 수 | ESTABLISHED TCP 연결 | 1,000개 |
| OS-010 | 커널 버전 | 현재 커널 버전 정보 | - |

### ☸️ Kubernetes 클러스터 점검 (10개)

| ID | 점검 항목 | 설명 | 기준 |
|----|----------|------|------|
| K8S-001 | 노드 상태 | 모든 노드 Ready 상태 | Ready |
| K8S-002 | 노드 CPU 사용량 | 노드별 CPU 사용률 | 80% |
| K8S-003 | 노드 메모리 사용량 | 노드별 메모리 사용률 | 80% |
| K8S-004 | kube-system Pod | 시스템 Pod 상태 | Running |
| K8S-005 | PV 상태 | PersistentVolume 바인딩 | Bound |
| K8S-006 | PVC 상태 | PersistentVolumeClaim 바인딩 | Bound |
| K8S-007 | Warning 이벤트 | 최근 경고 이벤트 수 | 10개 |
| K8S-008 | NotReady 노드 | NotReady 상태 노드 수 | 0개 |
| K8S-009 | 클러스터 버전 | Kubernetes 버전 | - |
| K8S-010 | 네임스페이스 수 | 전체 네임스페이스 개수 | - |

### 🚀 K8s 서비스 점검 (10개)

| ID | 점검 항목 | 설명 | 기준 |
|----|----------|------|------|
| SVC-001 | Deployment 상태 | 모든 Deployment Ready | Replica 일치 |
| SVC-002 | StatefulSet 상태 | 모든 StatefulSet Ready | Replica 일치 |
| SVC-003 | DaemonSet 상태 | 모든 DaemonSet Ready | Replica 일치 |
| SVC-004 | Service Endpoints | Endpoint 없는 Service | 0개 |
| SVC-005 | Ingress 상태 | Ingress 리소스 개수 | - |
| SVC-006 | Pod 재시작 과다 | 재시작 5회 이상 Pod | 0개 |
| SVC-007 | Pending Pod | Pending 상태 Pod 수 | 0개 |
| SVC-008 | Failed Pod | Failed 상태 Pod 수 | 0개 |
| SVC-009 | CronJob 상태 | 전체 CronJob 개수 | - |
| SVC-010 | Job 실패 | Failed 상태 Job 수 | 0개 |

---

## 📁 프로젝트 구조

```
infra-check/
│
├── 📄 infra-check.sh          # 메인 실행 스크립트 (Bash wrapper)
├── 📄 README.md               # 프로젝트 문서
├── 📄 LICENSE                 # 라이선스 파일
├── 📄 .gitignore              # Git 제외 파일
│
├── 📁 config/                 # 설정 파일 디렉토리
│   └── 📄 check_items.yaml    # 점검 항목 및 알림 설정
│
├── 📁 scripts/                # Python 스크립트 디렉토리
│   ├── 📄 main.py             # 메인 실행 스크립트
│   ├── 📄 checker.py          # 점검 수행 모듈
│   ├── 📄 report_generator.py # 보고서 생성 모듈 (CSV, DOCX)
│   └── 📄 notifier.py         # 알림 발송 모듈
│
└── 📁 output/                 # 보고서 출력 디렉토리
    ├── 📄 infra_check_2025_W49.csv
    └── 📄 infra_check_2025_W49.docx
```

### 각 파일 설명

| 파일 | 역할 |
|------|------|
| `infra-check.sh` | Bash 래퍼 스크립트. 의존성 확인 및 Python 스크립트 실행 |
| `config/check_items.yaml` | 점검 항목 정의, 임계치, 알림 채널 설정 |
| `scripts/main.py` | CLI 인터페이스, 전체 워크플로우 관리 |
| `scripts/checker.py` | OS/K8s/Service 점검 로직, 데모 모드 지원 |
| `scripts/report_generator.py` | CSV, DOCX 보고서 생성 |
| `scripts/notifier.py` | Email, Slack, Teams, Discord, Telegram 알림 |

---

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/infra-check.git
cd infra-check
```

### 2. 실행 권한 부여

```bash
chmod +x infra-check.sh
```

### 3. Python 의존성 설치

```bash
# pip 사용
pip install pyyaml python-docx requests

# 또는 pip3 사용
pip3 install pyyaml python-docx requests

# Ubuntu/Debian (시스템 패키지 충돌 시)
pip3 install pyyaml python-docx requests --break-system-packages
```

### 4. (선택) kubectl 설치

Kubernetes 점검을 위해 kubectl이 필요합니다. 없으면 데모 모드로 테스트하세요.

```bash
# kubectl 설치 확인
kubectl version --client

# 클러스터 연결 확인
kubectl cluster-info
```

### 5. 설치 확인

```bash
# 데모 모드로 테스트
./infra-check.sh --demo
```

---

## 📖 사용 방법

### 기본 명령어

```bash
# 도움말 보기
./infra-check.sh --help

# 데모 모드 실행 (예시 데이터 사용)
./infra-check.sh --demo

# 실제 환경 점검 (주간 보고서)
./infra-check.sh

# 월간 보고서 생성
./infra-check.sh --type monthly

# 알림 발송 포함
./infra-check.sh --notify

# 문제 발생시에만 알림
./infra-check.sh --notify-on-issues

# JSON 형식 출력
./infra-check.sh --json

# 조용한 모드 (출력 최소화)
./infra-check.sh --quiet
```

### Python 직접 실행

```bash
# 기본 실행
python3 scripts/main.py

# 데모 모드
python3 scripts/main.py --demo

# 옵션 조합
python3 scripts/main.py --demo --type monthly --notify
```

### 사용 예시

```bash
# 예시 1: 주간 점검 + Slack 알림
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
./infra-check.sh --notify

# 예시 2: 월간 보고서 + 이슈만 알림
./infra-check.sh --type monthly --notify-on-issues

# 예시 3: 특정 출력 디렉토리 지정
./infra-check.sh --output-dir /var/reports/

# 예시 4: 커스텀 설정 파일 사용
./infra-check.sh --config /etc/infra-check/custom.yaml
```

---

## ⚙️ 설정 가이드

### config/check_items.yaml 구조

```yaml
# 점검 항목 정의
check_items:
  os:           # OS 점검 항목 (10개)
    - id: OS-001
      name: "디스크 사용량"
      description: "루트 파일시스템 디스크 사용률 확인"
      command: "df -h / | awk 'NR==2{gsub(/%/,\"\",$5); print $5}'"
      threshold: 80          # 임계치
      unit: "%"              # 단위
      
  kubernetes:   # K8s 클러스터 점검 항목 (10개)
    - id: K8S-001
      name: "노드 상태"
      command: "kubectl get nodes --no-headers | awk '{print $1\":\"$2}'"
      expected: "Ready"      # 기대값
      
  services:     # K8s 서비스 점검 항목 (10개)
    - id: SVC-001
      name: "Deployment 상태"
      command: "kubectl get deployments --all-namespaces --no-headers"
      check_type: "replica_match"  # 점검 유형

# 알림 채널 설정
notifications:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    sender: "infra@company.com"
    recipients:
      - "admin@company.com"
      - "devops@company.com"
    use_tls: true
    
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"  # 환경변수 참조
    channel: "#infra-alerts"
    
  teams:
    enabled: false
    webhook_url: "${TEAMS_WEBHOOK_URL}"
    
  discord:
    enabled: false
    webhook_url: "${DISCORD_WEBHOOK_URL}"
    
  telegram:
    enabled: false
    bot_token: "${TELEGRAM_BOT_TOKEN}"
    chat_id: "${TELEGRAM_CHAT_ID}"

# 보고서 설정
report:
  type: "weekly"           # weekly 또는 monthly
  output_dir: "./output"
  company_name: "회사명"
  team_name: "인프라팀"
```

### 점검 항목 상태 판단 기준

| 상태 | 조건 | 아이콘 |
|------|------|--------|
| 정상 | 측정값 < 임계치 × 0.8 | ✅ |
| 경고 | 임계치 × 0.8 ≤ 측정값 < 임계치 | ⚠️ |
| 위험 | 측정값 ≥ 임계치 | ❌ |
| 확인불가 | 명령 실행 실패 또는 데이터 없음 | ❓ |

---

## 🔔 알림 채널 설정

### Slack

1. Slack App에서 Incoming Webhook 생성
2. Webhook URL 획득

```bash
# 환경변수 설정
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"

# 또는 config 파일에 직접 입력
```

### Microsoft Teams

1. Teams 채널 → 커넥터 → Incoming Webhook 추가
2. Webhook URL 복사

```bash
export TEAMS_WEBHOOK_URL="https://outlook.office.com/webhook/..."
```

### Discord

1. 서버 설정 → 연동 → 웹후크 → 새 웹후크
2. Webhook URL 복사

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

### Telegram

1. @BotFather로 봇 생성
2. Bot Token 획득
3. Chat ID 확인 (그룹 또는 개인)

```bash
export TELEGRAM_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export TELEGRAM_CHAT_ID="-1001234567890"
```

### Email (SMTP)

Gmail 사용 시:
1. Google 계정 → 보안 → 앱 비밀번호 생성
2. 앱 비밀번호를 SMTP_PASSWORD로 사용

```bash
export SMTP_PASSWORD="your-app-password"
```

```yaml
# config/check_items.yaml
notifications:
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    smtp_user: "your-email@gmail.com"
    sender: "your-email@gmail.com"
    recipients:
      - "admin@company.com"
    use_tls: true
```

---

## ⏰ Cron 스케줄링

### 주간 점검 (매주 월요일 오전 9시)

```bash
# crontab 편집
crontab -e

# 추가할 내용
0 9 * * 1 /path/to/infra-check/infra-check.sh --notify >> /var/log/infra-check.log 2>&1
```

### 월간 점검 (매월 1일 오전 9시)

```bash
0 9 1 * * /path/to/infra-check/infra-check.sh --type monthly --notify >> /var/log/infra-check-monthly.log 2>&1
```

### 일일 점검 (매일 오전 8시, 문제시에만 알림)

```bash
0 8 * * * /path/to/infra-check/infra-check.sh --notify-on-issues >> /var/log/infra-check-daily.log 2>&1
```

### 환경변수 포함 Cron

```bash
# 환경변수와 함께 실행
0 9 * * 1 SLACK_WEBHOOK_URL="https://hooks.slack.com/..." /path/to/infra-check/infra-check.sh --notify
```

---

## 📊 출력 예시

### 콘솔 출력

```
============================================================
🔍 인프라 정기점검 시작
   보고서 유형: weekly
   회사: Your Company
   담당팀: Infrastructure Team
============================================================

📋 OS 점검 중... (10개 항목)
📋 Kubernetes 점검 중... (10개 항목)
📋 서비스 점검 중... (10개 항목)

============================================================
📊 점검 결과 요약
============================================================
  총 점검항목: 30
  ✅ 정상: 28
  ⚠️ 경고: 2
  ❌ 위험: 0
  ❓ 확인불가: 0
============================================================

📂 카테고리별 결과:
  OS: ✅10 ⚠️0 ❌0 ❓0
  Kubernetes: ✅8 ⚠️2 ❌0 ❓0
  Services: ✅10 ⚠️0 ❌0 ❓0

📝 보고서 생성 중...
✅ 보고서 생성 완료:
   - CSV: ./output/infra_check_2025_W49.csv
   - DOCX: ./output/infra_check_2025_W49.docx
============================================================
```

### CSV 보고서 예시

```csv
점검ID,점검항목,카테고리,설명,상태,측정값,임계치,결과메시지,점검시간
OS-001,디스크 사용량,OS,루트 파일시스템 디스크 사용률 확인,정상,45,80%,정상 범위 내,2025-12-03T09:00:00
OS-002,메모리 사용량,OS,시스템 메모리 사용률 확인,정상,62.5,85%,정상 범위 내,2025-12-03T09:00:00
...
```

### JSON 출력 예시

```bash
./infra-check.sh --json --demo
```

```json
{
  "summary": {
    "total": 30,
    "ok": 30,
    "warning": 0,
    "critical": 0,
    "unknown": 0,
    "by_category": {
      "OS": {"ok": 10, "warning": 0, "critical": 0, "unknown": 0},
      "Kubernetes": {"ok": 10, "warning": 0, "critical": 0, "unknown": 0},
      "Services": {"ok": 10, "warning": 0, "critical": 0, "unknown": 0}
    }
  },
  "results": [...],
  "timestamp": "2025-12-03T09:00:00",
  "demo_mode": true
}
```

---

## 🔧 커스터마이징

### 새 OS 점검 항목 추가

```yaml
# config/check_items.yaml
check_items:
  os:
    # 기존 항목들...
    
    - id: OS-011
      name: "새 점검 항목"
      description: "점검 설명"
      command: "your-command-here"
      threshold: 80
      unit: "%"
```

### 새 알림 채널 추가

`scripts/notifier.py`에서 `NotificationSender` 클래스 상속:

```python
class MyCustomSender(NotificationSender):
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        # 커스텀 알림 로직 구현
        try:
            # API 호출 등
            return True
        except Exception as e:
            print(f"발송 실패: {e}")
            return False
```

### 데모 데이터 커스터마이징

`scripts/checker.py`의 `_get_demo_*_data` 메서드 수정:

```python
def _get_demo_os_data(self, item_id: str) -> tuple:
    demo_data = {
        'OS-001': ('75', CheckStatus.WARNING, '임계치 근접'),  # 경고 상태로 변경
        # ...
    }
    return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, '데모 데이터 없음'))
```

---

## ❓ 트러블슈팅

### kubectl 명령 실패

```bash
# 클러스터 연결 확인
kubectl cluster-info

# kubeconfig 확인
echo $KUBECONFIG
cat ~/.kube/config

# 권한 확인
kubectl auth can-i get nodes
```

### Python 모듈 없음

```bash
# 모듈 설치
pip3 install pyyaml python-docx requests

# 설치 확인
python3 -c "import yaml; import docx; import requests; print('OK')"
```

### 한글 깨짐 (CSV)

CSV 파일은 UTF-8 BOM으로 저장됩니다. Excel에서 바로 열 수 있습니다.
만약 깨진다면:
1. Excel → 데이터 → 텍스트에서 → 파일 선택
2. 인코딩을 UTF-8로 선택

### 권한 오류

```bash
# 실행 권한 부여
chmod +x infra-check.sh

# 출력 디렉토리 권한
mkdir -p output
chmod 755 output
```

### 데모 모드로 테스트

kubectl이 없거나 클러스터에 연결할 수 없을 때:

```bash
./infra-check.sh --demo
```

---

## 🔒 종료 코드

| 코드 | 의미 | 설명 |
|------|------|------|
| 0 | 성공 | 모든 항목 정상 |
| 1 | 경고 | 경고 항목 있음 |
| 2 | 위험 | 위험 항목 있음 |

CI/CD 파이프라인에서 활용:

```bash
./infra-check.sh
if [ $? -eq 2 ]; then
    echo "Critical issues found!"
    exit 1
fi
```

---

## 📝 .gitignore 예시

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Output files
output/*.csv
output/*.docx

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Secrets (절대 커밋하지 마세요!)
.env
secrets.yaml
```

---

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포할 수 있습니다.

---

## 👨‍💻 작성자

- 이름: Hwiwon Joung (Sean 정휘원) 
- Email: chicagomenbusy@gmail.com
- GitHub: [@seanjoung](https://github.com/seanjoung/AiLLMOps-operation/)

---

## 📚 관련 링크

- [Kubernetes 공식 문서](https://kubernetes.io/docs/)
- [Python python-docx 문서](https://python-docx.readthedocs.io/)
- [Slack Incoming Webhooks](https://api.slack.com/messaging/webhooks)
