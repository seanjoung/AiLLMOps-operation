#!/usr/bin/env python3
"""
Notification Module
Email, Slack, Teams, Discord 등 다양한 채널로 알림 전송
"""

import smtplib
import json
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


@dataclass
class NotificationConfig:
    """알림 설정"""
    # Email 설정
    email_enabled: bool = False
    smtp_server: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    sender: str = ""
    recipients: List[str] = None
    use_tls: bool = True
    
    # Slack 설정
    slack_enabled: bool = False
    slack_webhook_url: str = ""
    slack_channel: str = "#infra-alerts"
    
    # Microsoft Teams 설정
    teams_enabled: bool = False
    teams_webhook_url: str = ""
    
    # Discord 설정
    discord_enabled: bool = False
    discord_webhook_url: str = ""
    
    # Telegram 설정
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    
    # Webhook (일반) 설정
    webhook_enabled: bool = False
    webhook_url: str = ""
    webhook_headers: Dict[str, str] = None


class NotificationSender(ABC):
    """알림 발송 기본 클래스"""
    
    @abstractmethod
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        pass
    
    def _format_summary_text(self, summary: Dict) -> str:
        """요약 정보를 텍스트로 포맷"""
        return f"""
📊 점검 결과 요약
━━━━━━━━━━━━━━━━━━
총 점검항목: {summary.get('total', 0)}개
✅ 정상: {summary.get('ok', 0)}
⚠️ 경고: {summary.get('warning', 0)}
❌ 위험: {summary.get('critical', 0)}
❓ 확인불가: {summary.get('unknown', 0)}
━━━━━━━━━━━━━━━━━━
"""


class EmailSender(NotificationSender):
    """이메일 발송"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        if not self.config.email_enabled:
            return False
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.sender
            msg['To'] = ', '.join(self.config.recipients or [])
            msg['Subject'] = title
            
            # HTML 본문 생성
            html_body = self._create_html_body(title, message, summary)
            msg.attach(MIMEText(html_body, 'html', 'utf-8'))
            
            # 첨부파일 추가
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
                        msg.attach(part)
            
            # 메일 전송
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls()
                if self.config.smtp_user and self.config.smtp_password:
                    server.login(self.config.smtp_user, self.config.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"Email 발송 실패: {e}")
            return False
    
    def _create_html_body(self, title: str, message: str, summary: Dict) -> str:
        ok_count = summary.get('ok', 0)
        warning_count = summary.get('warning', 0)
        critical_count = summary.get('critical', 0)
        unknown_count = summary.get('unknown', 0)
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Malgun Gothic', Arial, sans-serif; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .summary {{ display: flex; justify-content: space-around; padding: 20px; background: #ecf0f1; }}
        .stat {{ text-align: center; padding: 15px; border-radius: 8px; min-width: 80px; }}
        .ok {{ background: #27ae60; color: white; }}
        .warning {{ background: #f39c12; color: white; }}
        .critical {{ background: #e74c3c; color: white; }}
        .unknown {{ background: #95a5a6; color: white; }}
        .content {{ padding: 20px; }}
        .footer {{ background: #34495e; color: white; padding: 10px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="summary">
        <div class="stat ok">
            <h2>{ok_count}</h2>
            <p>정상</p>
        </div>
        <div class="stat warning">
            <h2>{warning_count}</h2>
            <p>경고</p>
        </div>
        <div class="stat critical">
            <h2>{critical_count}</h2>
            <p>위험</p>
        </div>
        <div class="stat unknown">
            <h2>{unknown_count}</h2>
            <p>확인불가</p>
        </div>
    </div>
    <div class="content">
        <h3>상세 내용</h3>
        <pre>{message}</pre>
    </div>
    <div class="footer">
        <p>본 메일은 인프라 정기점검 시스템에서 자동 발송되었습니다.</p>
    </div>
</body>
</html>
"""


class SlackSender(NotificationSender):
    """Slack 웹훅 발송"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        if not self.config.slack_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            # Slack Block Kit 형식
            blocks = [
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": f"🔍 {title}"}
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*총 점검:*\n{summary.get('total', 0)}개"},
                        {"type": "mrkdwn", "text": f"*✅ 정상:*\n{summary.get('ok', 0)}"},
                        {"type": "mrkdwn", "text": f"*⚠️ 경고:*\n{summary.get('warning', 0)}"},
                        {"type": "mrkdwn", "text": f"*❌ 위험:*\n{summary.get('critical', 0)}"}
                    ]
                },
                {"type": "divider"},
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"📅 점검시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"}
                    ]
                }
            ]
            
            # 경고/위험 항목이 있으면 추가
            if summary.get('warning', 0) > 0 or summary.get('critical', 0) > 0:
                blocks.append({
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": f"```{message[:2000]}```"}
                })
            
            payload = {
                "channel": self.config.slack_channel,
                "blocks": blocks
            }
            
            response = requests.post(
                self.config.slack_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Slack 발송 실패: {e}")
            return False


class TeamsSender(NotificationSender):
    """Microsoft Teams 웹훅 발송"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        if not self.config.teams_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            # Teams Adaptive Card 형식
            card = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": self._get_theme_color(summary),
                "summary": title,
                "sections": [
                    {
                        "activityTitle": f"🔍 {title}",
                        "activitySubtitle": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "facts": [
                            {"name": "총 점검", "value": str(summary.get('total', 0))},
                            {"name": "✅ 정상", "value": str(summary.get('ok', 0))},
                            {"name": "⚠️ 경고", "value": str(summary.get('warning', 0))},
                            {"name": "❌ 위험", "value": str(summary.get('critical', 0))},
                            {"name": "❓ 확인불가", "value": str(summary.get('unknown', 0))}
                        ],
                        "markdown": True
                    }
                ]
            }
            
            if message:
                card["sections"].append({
                    "text": f"```\n{message[:2000]}\n```"
                })
            
            response = requests.post(
                self.config.teams_webhook_url,
                json=card,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Teams 발송 실패: {e}")
            return False
    
    def _get_theme_color(self, summary: Dict) -> str:
        if summary.get('critical', 0) > 0:
            return "FF0000"  # Red
        elif summary.get('warning', 0) > 0:
            return "FFA500"  # Orange
        else:
            return "00FF00"  # Green


class DiscordSender(NotificationSender):
    """Discord 웹훅 발송"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        if not self.config.discord_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            # Discord Embed 형식
            embed = {
                "title": f"🔍 {title}",
                "color": self._get_color(summary),
                "timestamp": datetime.now().isoformat(),
                "fields": [
                    {"name": "총 점검", "value": str(summary.get('total', 0)), "inline": True},
                    {"name": "✅ 정상", "value": str(summary.get('ok', 0)), "inline": True},
                    {"name": "⚠️ 경고", "value": str(summary.get('warning', 0)), "inline": True},
                    {"name": "❌ 위험", "value": str(summary.get('critical', 0)), "inline": True},
                    {"name": "❓ 확인불가", "value": str(summary.get('unknown', 0)), "inline": True}
                ],
                "footer": {"text": "인프라 정기점검 시스템"}
            }
            
            if message:
                embed["description"] = f"```\n{message[:2000]}\n```"
            
            payload = {"embeds": [embed]}
            
            response = requests.post(
                self.config.discord_webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"Discord 발송 실패: {e}")
            return False
    
    def _get_color(self, summary: Dict) -> int:
        if summary.get('critical', 0) > 0:
            return 0xFF0000  # Red
        elif summary.get('warning', 0) > 0:
            return 0xFFA500  # Orange
        else:
            return 0x00FF00  # Green


class TelegramSender(NotificationSender):
    """Telegram 봇 발송"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        if not self.config.telegram_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            text = f"""
*{title}*

📊 *점검 결과 요약*
━━━━━━━━━━━━━━━━
총 점검: {summary.get('total', 0)}개
✅ 정상: {summary.get('ok', 0)}
⚠️ 경고: {summary.get('warning', 0)}
❌ 위험: {summary.get('critical', 0)}
❓ 확인불가: {summary.get('unknown', 0)}
━━━━━━━━━━━━━━━━
📅 점검시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": self.config.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            # 첨부파일 전송
            if attachments and response.status_code == 200:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        self._send_document(filepath)
            
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram 발송 실패: {e}")
            return False
    
    def _send_document(self, filepath: str) -> bool:
        try:
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendDocument"
            with open(filepath, 'rb') as f:
                response = requests.post(
                    url,
                    data={"chat_id": self.config.telegram_chat_id},
                    files={"document": f},
                    timeout=30
                )
            return response.status_code == 200
        except:
            return False


class WebhookSender(NotificationSender):
    """일반 웹훅 발송"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
    
    def send(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> bool:
        if not self.config.webhook_enabled or not REQUESTS_AVAILABLE:
            return False
        
        try:
            payload = {
                "title": title,
                "message": message,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
                "attachments": attachments or []
            }
            
            headers = self.config.webhook_headers or {'Content-Type': 'application/json'}
            
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            return response.status_code in [200, 201, 202, 204]
        except Exception as e:
            print(f"Webhook 발송 실패: {e}")
            return False


class NotificationManager:
    """알림 관리자 - 모든 알림 채널 통합 관리"""
    
    def __init__(self, config: NotificationConfig):
        self.config = config
        self.senders: List[NotificationSender] = []
        
        # 활성화된 발송자 등록
        if config.email_enabled:
            self.senders.append(EmailSender(config))
        if config.slack_enabled:
            self.senders.append(SlackSender(config))
        if config.teams_enabled:
            self.senders.append(TeamsSender(config))
        if config.discord_enabled:
            self.senders.append(DiscordSender(config))
        if config.telegram_enabled:
            self.senders.append(TelegramSender(config))
        if config.webhook_enabled:
            self.senders.append(WebhookSender(config))
    
    def send_all(self, title: str, message: str, summary: Dict, attachments: List[str] = None) -> Dict[str, bool]:
        """모든 활성화된 채널로 알림 발송"""
        results = {}
        
        for sender in self.senders:
            sender_name = sender.__class__.__name__
            results[sender_name] = sender.send(title, message, summary, attachments)
        
        return results
    
    def send_if_issues(self, title: str, message: str, summary: Dict, 
                       attachments: List[str] = None,
                       send_on_warning: bool = True,
                       send_on_critical: bool = True) -> Dict[str, bool]:
        """문제가 있을 때만 알림 발송"""
        has_warning = summary.get('warning', 0) > 0
        has_critical = summary.get('critical', 0) > 0
        
        if (send_on_warning and has_warning) or (send_on_critical and has_critical):
            return self.send_all(title, message, summary, attachments)
        
        return {}


if __name__ == "__main__":
    # 테스트
    config = NotificationConfig(
        slack_enabled=True,
        slack_webhook_url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        slack_channel="#test"
    )
    
    manager = NotificationManager(config)
    summary = {'total': 15, 'ok': 12, 'warning': 2, 'critical': 1, 'unknown': 0}
    
    results = manager.send_all(
        title="인프라 정기점검 보고서",
        message="테스트 메시지",
        summary=summary
    )
    print(f"발송 결과: {results}")
