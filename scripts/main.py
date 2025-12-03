#!/usr/bin/env python3
"""
Infrastructure Health Check - Main Script
주간/월간 정기점검 보고서 생성 및 알림 발송

사용법:
    python main.py                     # 기본 실행 (weekly)
    python main.py --demo              # 데모 모드 (예시 데이터)
    python main.py --type monthly      # 월간 보고서
    python main.py --notify            # 알림 발송 포함
"""

import argparse
import os
import sys
import yaml
from datetime import datetime

# 스크립트 경로 설정
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from checker import InfraChecker
from report_generator import ReportGenerator, ReportConfig, generate_reports
from notifier import NotificationConfig, NotificationManager


def load_config(config_path: str) -> dict:
    """설정 파일 로드"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_notification_config(config: dict) -> NotificationConfig:
    """YAML 설정에서 알림 설정 생성"""
    notif = config.get('notifications', {})
    
    email_config = notif.get('email', {})
    slack_config = notif.get('slack', {})
    teams_config = notif.get('teams', {})
    discord_config = notif.get('discord', {})
    telegram_config = notif.get('telegram', {})
    webhook_config = notif.get('webhook', {})
    
    return NotificationConfig(
        email_enabled=email_config.get('enabled', False),
        smtp_server=email_config.get('smtp_server', ''),
        smtp_port=email_config.get('smtp_port', 587),
        smtp_user=email_config.get('smtp_user', ''),
        smtp_password=os.environ.get('SMTP_PASSWORD', email_config.get('smtp_password', '')),
        sender=email_config.get('sender', ''),
        recipients=email_config.get('recipients', []),
        use_tls=email_config.get('use_tls', True),
        slack_enabled=slack_config.get('enabled', False),
        slack_webhook_url=os.environ.get('SLACK_WEBHOOK_URL', slack_config.get('webhook_url', '')),
        slack_channel=slack_config.get('channel', '#infra-alerts'),
        teams_enabled=teams_config.get('enabled', False),
        teams_webhook_url=os.environ.get('TEAMS_WEBHOOK_URL', teams_config.get('webhook_url', '')),
        discord_enabled=discord_config.get('enabled', False),
        discord_webhook_url=os.environ.get('DISCORD_WEBHOOK_URL', discord_config.get('webhook_url', '')),
        telegram_enabled=telegram_config.get('enabled', False),
        telegram_bot_token=os.environ.get('TELEGRAM_BOT_TOKEN', telegram_config.get('bot_token', '')),
        telegram_chat_id=os.environ.get('TELEGRAM_CHAT_ID', telegram_config.get('chat_id', '')),
        webhook_enabled=webhook_config.get('enabled', False),
        webhook_url=webhook_config.get('url', ''),
        webhook_headers=webhook_config.get('headers', None)
    )


def create_report_config(config: dict, report_type: str) -> ReportConfig:
    """YAML 설정에서 보고서 설정 생성"""
    report_conf = config.get('report', {})
    
    return ReportConfig(
        report_type=report_type or report_conf.get('type', 'weekly'),
        company_name=report_conf.get('company_name', 'Company'),
        team_name=report_conf.get('team_name', 'Infrastructure Team'),
        output_dir=report_conf.get('output_dir', './output')
    )


def format_issue_message(results: list) -> str:
    """문제 항목을 메시지로 포맷"""
    issues = [r for r in results if r.get('상태') in ['경고', '위험']]
    
    if not issues:
        return "모든 점검 항목이 정상입니다."
    
    lines = ["🚨 조치 필요 항목:"]
    for issue in issues:
        status = issue.get('상태', '')
        icon = "⚠️" if status == '경고' else "❌"
        lines.append(f"{icon} [{issue.get('점검ID')}] {issue.get('점검항목')}")
        lines.append(f"   └─ {issue.get('결과메시지', '')}")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='인프라 정기점검 보고서 생성 스크립트',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--config', '-c',
        default=os.path.join(os.path.dirname(SCRIPT_DIR), 'config', 'check_items.yaml'),
        help='설정 파일 경로'
    )
    parser.add_argument(
        '--type', '-t',
        choices=['weekly', 'monthly'],
        help='보고서 유형 (weekly/monthly)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        help='보고서 출력 디렉토리'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='데모 모드 (예시 데이터 사용)'
    )
    parser.add_argument(
        '--notify', '-n',
        action='store_true',
        help='모든 알림 채널로 발송'
    )
    parser.add_argument(
        '--notify-on-issues',
        action='store_true',
        help='문제 발생시에만 알림 발송'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='결과를 JSON 형식으로 출력'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='출력 최소화'
    )
    
    args = parser.parse_args()
    
    # 설정 로드
    if not os.path.exists(args.config):
        print(f"❌ 설정 파일을 찾을 수 없습니다: {args.config}")
        sys.exit(1)
    
    config = load_config(args.config)
    
    # 보고서 설정
    report_config = create_report_config(config, args.type)
    if args.output_dir:
        report_config.output_dir = args.output_dir
    
    if not args.quiet:
        print("=" * 60)
        print("🔍 인프라 정기점검 시작")
        if args.demo:
            print("   ⚠️  데모 모드 - 예시 데이터 사용")
        print(f"   보고서 유형: {report_config.report_type}")
        print(f"   회사: {report_config.company_name}")
        print(f"   담당팀: {report_config.team_name}")
        print("=" * 60)
    
    # 점검 수행
    checker = InfraChecker(args.config, demo_mode=args.demo)
    
    if not args.quiet:
        print("\n📋 OS 점검 중... (10개 항목)")
    os_results = checker.run_os_checks()
    
    if not args.quiet:
        print("📋 Kubernetes 점검 중... (10개 항목)")
    k8s_results = checker.run_k8s_checks()
    
    if not args.quiet:
        print("📋 서비스 점검 중... (10개 항목)")
    svc_results = checker.run_service_checks()
    
    # 결과 통합
    checker.results = os_results + k8s_results + svc_results
    results_dict = checker.to_dict()
    summary = checker.get_summary()
    
    # JSON 출력 모드
    if args.json:
        import json
        output = {
            'summary': summary,
            'results': results_dict,
            'timestamp': datetime.now().isoformat(),
            'demo_mode': args.demo
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    
    # 결과 요약 출력
    if not args.quiet:
        print("\n" + "=" * 60)
        print("📊 점검 결과 요약")
        print("=" * 60)
        print(f"  총 점검항목: {summary['total']}")
        print(f"  ✅ 정상: {summary['ok']}")
        print(f"  ⚠️ 경고: {summary['warning']}")
        print(f"  ❌ 위험: {summary['critical']}")
        print(f"  ❓ 확인불가: {summary['unknown']}")
        print("=" * 60)
        
        # 카테고리별 결과
        print("\n📂 카테고리별 결과:")
        for cat, cat_summary in summary['by_category'].items():
            print(f"  {cat}: ✅{cat_summary['ok']} ⚠️{cat_summary['warning']} ❌{cat_summary['critical']} ❓{cat_summary['unknown']}")
    
    # 보고서 생성
    if not args.quiet:
        print("\n📝 보고서 생성 중...")
    
    generated_files = generate_reports(results_dict, summary, report_config)
    
    if not args.quiet:
        print("✅ 보고서 생성 완료:")
        for fmt, path in generated_files.items():
            print(f"   - {fmt.upper()}: {path}")
    
    # 알림 발송
    if args.notify or args.notify_on_issues:
        notif_config = create_notification_config(config)
        manager = NotificationManager(notif_config)
        
        now = datetime.now()
        if report_config.report_type == "weekly":
            week_num = now.isocalendar()[1]
            title = f"[{report_config.company_name}] {now.year}년 {week_num}주차 인프라 정기점검 보고서"
        else:
            title = f"[{report_config.company_name}] {now.year}년 {now.month}월 인프라 정기점검 보고서"
        
        message = format_issue_message(results_dict)
        attachments = list(generated_files.values())
        
        if args.notify_on_issues:
            results = manager.send_if_issues(title, message, summary, attachments)
        else:
            results = manager.send_all(title, message, summary, attachments)
        
        if not args.quiet and results:
            print("\n📤 알림 발송 결과:")
            for sender, success in results.items():
                status = "✅" if success else "❌"
                print(f"   {status} {sender}")
    
    # 상세 결과 출력
    if not args.quiet:
        print("\n" + "=" * 60)
        print("📋 상세 점검 결과")
        print("=" * 60)
        
        current_category = ""
        for r in results_dict:
            if r['카테고리'] != current_category:
                current_category = r['카테고리']
                print(f"\n【 {current_category} 】")
            
            status = r['상태']
            if status == '정상':
                icon = "✅"
            elif status == '경고':
                icon = "⚠️"
            elif status == '위험':
                icon = "❌"
            else:
                icon = "❓"
            
            print(f"  {icon} [{r['점검ID']}] {r['점검항목']}")
            print(f"      측정값: {r['측정값'][:50]}{'...' if len(r['측정값']) > 50 else ''}")
            print(f"      결과: {r['결과메시지']}")
    
    # 문제 항목 강조
    issues = [r for r in results_dict if r.get('상태') in ['경고', '위험']]
    if issues and not args.quiet:
        print("\n" + "=" * 60)
        print("🚨 조치 필요 항목")
        print("=" * 60)
        for issue in issues:
            status = issue.get('상태', '')
            icon = "⚠️" if status == '경고' else "❌"
            print(f"{icon} [{issue.get('점검ID')}] {issue.get('점검항목')}")
            print(f"   상태: {status}")
            print(f"   내용: {issue.get('결과메시지', '')}")
            print(f"   설명: {issue.get('설명', '')}")
            print()
    
    if not args.quiet:
        print("=" * 60)
        print("✅ 점검 완료")
        print("=" * 60)
    
    # 종료 코드
    if summary['critical'] > 0:
        sys.exit(2)
    elif summary['warning'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
