#!/usr/bin/env python3
"""
Infrastructure Health Check Module
OS, Kubernetes, K8s Services 점검 수행
데모 모드 지원 - kubectl 없어도 예시 데이터로 테스트 가능
"""

import subprocess
import random
import yaml
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum

class CheckStatus(Enum):
    OK = "정상"
    WARNING = "경고"
    CRITICAL = "위험"
    UNKNOWN = "확인불가"

@dataclass
class CheckResult:
    check_id: str
    name: str
    category: str
    description: str
    status: CheckStatus
    value: str
    threshold: Optional[float]
    unit: str
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    raw_output: str = ""

class InfraChecker:
    def __init__(self, config_path: str = "config/check_items.yaml", demo_mode: bool = False):
        self.config = self._load_config(config_path)
        self.results: List[CheckResult] = []
        self.demo_mode = demo_mode
        
    def _load_config(self, path: str) -> dict:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _run_command(self, command: str, timeout: int = 30) -> tuple:
        """쉘 명령어 실행"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Command timed out", -1
        except Exception as e:
            return "", str(e), -1
    
    def _check_kubectl_available(self) -> bool:
        """kubectl 사용 가능 여부 확인"""
        if self.demo_mode:
            return True
        stdout, _, returncode = self._run_command("which kubectl")
        return returncode == 0
    
    def _evaluate_threshold(self, value: str, threshold: float, check_id: str) -> CheckStatus:
        """임계치 기반 상태 판단"""
        try:
            numeric_value = float(value.replace('%', '').replace('개', '').strip())
            
            # 0이 정상인 항목들
            zero_is_ok = ['OS-005', 'K8S-008', 'SVC-004', 'SVC-006', 'SVC-007', 'SVC-008', 'SVC-010']
            
            if check_id in zero_is_ok:
                if numeric_value == 0:
                    return CheckStatus.OK
                elif numeric_value <= 3:
                    return CheckStatus.WARNING
                else:
                    return CheckStatus.CRITICAL
            else:
                if numeric_value < threshold * 0.8:
                    return CheckStatus.OK
                elif numeric_value < threshold:
                    return CheckStatus.WARNING
                else:
                    return CheckStatus.CRITICAL
        except (ValueError, AttributeError):
            return CheckStatus.UNKNOWN
    
    def _get_demo_os_data(self, item_id: str) -> tuple:
        """OS 점검 데모 데이터"""
        demo_data = {
            'OS-001': ('45', CheckStatus.OK, '정상 범위 내'),
            'OS-002': ('62.5', CheckStatus.OK, '정상 범위 내'),
            'OS-003': ('23', CheckStatus.OK, '정상 범위 내'),
            'OS-004': ('up 15 days, 4 hours, 32 minutes', CheckStatus.OK, '정상 확인'),
            'OS-005': ('0', CheckStatus.OK, '좀비 프로세스 없음'),
            'OS-006': ('1.25', CheckStatus.OK, '정상 범위 내'),
            'OS-007': ('12.3', CheckStatus.OK, '정상 범위 내'),
            'OS-008': ('3456', CheckStatus.OK, '정상 범위 내'),
            'OS-009': ('128', CheckStatus.OK, '정상 범위 내'),
            'OS-010': ('5.15.0-91-generic', CheckStatus.OK, '정상 확인'),
        }
        return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, '데모 데이터 없음'))
    
    def _get_demo_k8s_data(self, item_id: str) -> tuple:
        """Kubernetes 점검 데모 데이터"""
        demo_data = {
            'K8S-001': ('master-01:Ready\nworker-01:Ready\nworker-02:Ready\nworker-03:Ready', 
                        CheckStatus.OK, '모든 노드 정상 (4/4)'),
            'K8S-002': ('master-01:32%\nworker-01:45%\nworker-02:38%\nworker-03:52%', 
                        CheckStatus.OK, '모든 노드 CPU 정상'),
            'K8S-003': ('master-01:58%\nworker-01:62%\nworker-02:55%\nworker-03:71%', 
                        CheckStatus.OK, '모든 노드 메모리 정상'),
            'K8S-004': ('coredns-5d78c9869d-abc12:Running\ncoredns-5d78c9869d-def34:Running\netcd-master-01:Running\nkube-apiserver-master-01:Running\nkube-controller-manager-master-01:Running\nkube-proxy-xxxxx:Running\nkube-scheduler-master-01:Running', 
                        CheckStatus.OK, '모든 시스템 Pod 정상 (7/7)'),
            'K8S-005': ('pv-data-01:Bound\npv-data-02:Bound\npv-logs-01:Bound', 
                        CheckStatus.OK, '모든 PV 정상 (3/3)'),
            'K8S-006': ('data-pvc-01:Bound\ndata-pvc-02:Bound\nlogs-pvc-01:Bound', 
                        CheckStatus.OK, '모든 PVC 정상 (3/3)'),
            'K8S-007': ('3', CheckStatus.OK, '경고 이벤트 정상 범위'),
            'K8S-008': ('0', CheckStatus.OK, 'NotReady 노드 없음'),
            'K8S-009': ('v1.28.4', CheckStatus.OK, '정상 확인'),
            'K8S-010': ('8', CheckStatus.OK, '8개 네임스페이스'),
        }
        return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, '데모 데이터 없음'))
    
    def _get_demo_svc_data(self, item_id: str) -> tuple:
        """서비스 점검 데모 데이터"""
        demo_data = {
            'SVC-001': ('nginx-deployment:3/3\napi-server:2/2\nworker-deployment:5/5\nredis:1/1\npostgres:1/1', 
                        CheckStatus.OK, '모든 Deployment 정상 (5개)'),
            'SVC-002': ('mysql:1/1\nredis:3/3\nelasticsearch:3/3', 
                        CheckStatus.OK, '모든 StatefulSet 정상 (3개)'),
            'SVC-003': ('fluentd:4/4\nnode-exporter:4/4\nkube-proxy:4/4', 
                        CheckStatus.OK, '모든 DaemonSet 정상 (3개)'),
            'SVC-004': ('0', CheckStatus.OK, 'Endpoint 없는 Service 없음'),
            'SVC-005': ('5', CheckStatus.OK, '5개 Ingress 리소스'),
            'SVC-006': ('0', CheckStatus.OK, '재시작 과다 Pod 없음'),
            'SVC-007': ('0', CheckStatus.OK, 'Pending Pod 없음'),
            'SVC-008': ('0', CheckStatus.OK, 'Failed Pod 없음'),
            'SVC-009': ('3', CheckStatus.OK, '3개 CronJob'),
            'SVC-010': ('0', CheckStatus.OK, 'Failed Job 없음'),
        }
        return demo_data.get(item_id, ('N/A', CheckStatus.UNKNOWN, '데모 데이터 없음'))

    def run_os_checks(self) -> List[CheckResult]:
        """OS 점검 수행"""
        results = []
        for item in self.config['check_items']['os']:
            if self.demo_mode:
                value, status, message = self._get_demo_os_data(item['id'])
            else:
                stdout, stderr, returncode = self._run_command(item['command'])
                
                if returncode != 0 or not stdout:
                    status = CheckStatus.UNKNOWN
                    message = f"명령 실행 실패: {stderr}" if stderr else "결과 없음"
                    value = "N/A"
                else:
                    value = stdout
                    if item.get('threshold') is not None:
                        status = self._evaluate_threshold(stdout, item['threshold'], item['id'])
                        if status == CheckStatus.OK:
                            message = "정상 범위 내"
                        elif status == CheckStatus.WARNING:
                            message = f"임계치({item['threshold']}{item['unit']}) 근접"
                        else:
                            message = f"임계치({item['threshold']}{item['unit']}) 초과"
                    else:
                        status = CheckStatus.OK
                        message = "정상 확인"
            
            results.append(CheckResult(
                check_id=item['id'],
                name=item['name'],
                category="OS",
                description=item['description'],
                status=status,
                value=value,
                threshold=item.get('threshold'),
                unit=item.get('unit', ''),
                message=message,
                raw_output=value
            ))
        return results
    
    def run_k8s_checks(self) -> List[CheckResult]:
        """Kubernetes 클러스터 점검 수행"""
        results = []
        
        kubectl_available = self._check_kubectl_available()
        
        for item in self.config['check_items']['kubernetes']:
            if self.demo_mode:
                value, status, message = self._get_demo_k8s_data(item['id'])
            elif not kubectl_available:
                value = "N/A"
                status = CheckStatus.UNKNOWN
                message = "kubectl 명령어 사용 불가"
            else:
                stdout, stderr, returncode = self._run_command(item['command'])
                
                if "error" in stderr.lower() or (returncode != 0 and not stdout):
                    status = CheckStatus.UNKNOWN
                    message = f"점검 실패: {stderr[:100]}" if stderr else "명령 실행 오류"
                    value = "N/A"
                else:
                    value = stdout if stdout and stdout != 'N/A' else "데이터 없음"
                    expected = item.get('expected')
                    threshold = item.get('threshold')
                    
                    if expected:
                        lines = [l for l in stdout.strip().split('\n') if l and l != 'N/A']
                        ok_count = sum(1 for line in lines if expected in line)
                        total_count = len(lines) if lines else 0
                        
                        if total_count == 0:
                            status = CheckStatus.UNKNOWN
                            message = "점검 대상 없음"
                        elif ok_count == total_count:
                            status = CheckStatus.OK
                            message = f"모든 항목 정상 ({ok_count}/{total_count})"
                        elif ok_count > total_count * 0.7:
                            status = CheckStatus.WARNING
                            message = f"일부 항목 이상 ({ok_count}/{total_count})"
                        else:
                            status = CheckStatus.CRITICAL
                            message = f"다수 항목 이상 ({ok_count}/{total_count})"
                    elif threshold is not None:
                        status = self._evaluate_threshold(stdout, threshold, item['id'])
                        if status == CheckStatus.OK:
                            message = "정상 범위 내"
                        elif status == CheckStatus.WARNING:
                            message = f"임계치({threshold}{item.get('unit','')}) 근접"
                        else:
                            message = f"임계치({threshold}{item.get('unit','')}) 초과"
                    else:
                        status = CheckStatus.OK
                        message = "정상 확인"
            
            results.append(CheckResult(
                check_id=item['id'],
                name=item['name'],
                category="Kubernetes",
                description=item['description'],
                status=status,
                value=value[:300] if value else "N/A",
                threshold=item.get('threshold'),
                unit=item.get('unit', ''),
                message=message,
                raw_output=value[:500] if value else ""
            ))
        return results
    
    def run_service_checks(self) -> List[CheckResult]:
        """K8s 서비스 점검 수행"""
        results = []
        
        kubectl_available = self._check_kubectl_available()
        
        for item in self.config['check_items']['services']:
            if self.demo_mode:
                value, status, message = self._get_demo_svc_data(item['id'])
            elif not kubectl_available:
                value = "N/A"
                status = CheckStatus.UNKNOWN
                message = "kubectl 명령어 사용 불가"
            else:
                stdout, stderr, returncode = self._run_command(item['command'])
                
                if "error" in stderr.lower() or (returncode != 0 and not stdout):
                    status = CheckStatus.UNKNOWN
                    message = f"점검 실패: {stderr[:100]}" if stderr else "명령 실행 오류"
                    value = "N/A"
                else:
                    value = stdout if stdout and stdout != 'N/A' else "0"
                    check_type = item.get('check_type', '')
                    threshold = item.get('threshold')
                    
                    if check_type == 'replica_match':
                        lines = [l for l in stdout.strip().split('\n') if l and ':' in l and l != 'N/A']
                        issues = []
                        for line in lines:
                            if '/' in line:
                                parts = line.split(':')
                                if len(parts) >= 2:
                                    replicas = parts[-1]
                                    if '/' in replicas:
                                        try:
                                            avail, desired = replicas.split('/')
                                            if avail != desired:
                                                issues.append(parts[0])
                                        except:
                                            pass
                        
                        if len(lines) == 0 or value == 'N/A':
                            status = CheckStatus.UNKNOWN
                            message = "점검 대상 없음"
                        elif len(issues) == 0:
                            status = CheckStatus.OK
                            message = f"모든 리소스 정상 ({len(lines)}개)"
                        elif len(issues) <= 2:
                            status = CheckStatus.WARNING
                            message = f"일부 리소스 이상: {', '.join(issues[:3])}"
                        else:
                            status = CheckStatus.CRITICAL
                            message = f"다수 리소스 이상 ({len(issues)}개)"
                    
                    elif threshold is not None:
                        status = self._evaluate_threshold(stdout, threshold, item['id'])
                        if status == CheckStatus.OK:
                            message = "정상"
                        elif status == CheckStatus.WARNING:
                            message = f"임계치({threshold}{item.get('unit','')}) 근접"
                        else:
                            message = f"임계치({threshold}{item.get('unit','')}) 초과"
                    else:
                        status = CheckStatus.OK
                        message = "정상 확인"
            
            results.append(CheckResult(
                check_id=item['id'],
                name=item['name'],
                category="Services",
                description=item['description'],
                status=status,
                value=value[:300] if value else "N/A",
                threshold=item.get('threshold'),
                unit=item.get('unit', ''),
                message=message,
                raw_output=value[:500] if value else ""
            ))
        return results
    
    def run_all_checks(self) -> List[CheckResult]:
        """모든 점검 수행"""
        self.results = []
        self.results.extend(self.run_os_checks())
        self.results.extend(self.run_k8s_checks())
        self.results.extend(self.run_service_checks())
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """점검 결과 요약"""
        if not self.results:
            return {}
        
        summary = {
            'total': len(self.results),
            'ok': sum(1 for r in self.results if r.status == CheckStatus.OK),
            'warning': sum(1 for r in self.results if r.status == CheckStatus.WARNING),
            'critical': sum(1 for r in self.results if r.status == CheckStatus.CRITICAL),
            'unknown': sum(1 for r in self.results if r.status == CheckStatus.UNKNOWN),
            'by_category': {
                'OS': {'ok': 0, 'warning': 0, 'critical': 0, 'unknown': 0},
                'Kubernetes': {'ok': 0, 'warning': 0, 'critical': 0, 'unknown': 0},
                'Services': {'ok': 0, 'warning': 0, 'critical': 0, 'unknown': 0}
            }
        }
        
        for r in self.results:
            cat = r.category
            if r.status == CheckStatus.OK:
                summary['by_category'][cat]['ok'] += 1
            elif r.status == CheckStatus.WARNING:
                summary['by_category'][cat]['warning'] += 1
            elif r.status == CheckStatus.CRITICAL:
                summary['by_category'][cat]['critical'] += 1
            else:
                summary['by_category'][cat]['unknown'] += 1
        
        return summary
    
    def to_dict(self) -> List[Dict]:
        """결과를 딕셔너리 리스트로 변환"""
        return [
            {
                '점검ID': r.check_id,
                '점검항목': r.name,
                '카테고리': r.category,
                '설명': r.description,
                '상태': r.status.value,
                '측정값': r.value,
                '임계치': f"{r.threshold}{r.unit}" if r.threshold else "-",
                '결과메시지': r.message,
                '점검시간': r.timestamp
            }
            for r in self.results
        ]


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', action='store_true', help='데모 모드로 실행')
    args = parser.parse_args()
    
    checker = InfraChecker(demo_mode=args.demo)
    results = checker.run_all_checks()
    summary = checker.get_summary()
    
    print("\n" + "="*60)
    print("인프라 정기점검 결과 요약")
    if args.demo:
        print("(데모 모드)")
    print("="*60)
    print(f"총 점검 항목: {summary['total']}")
    print(f"  - 정상: {summary['ok']}")
    print(f"  - 경고: {summary['warning']}")
    print(f"  - 위험: {summary['critical']}")
    print(f"  - 확인불가: {summary['unknown']}")
    print("="*60)
    
    for r in results:
        status_icon = "✅" if r.status == CheckStatus.OK else "⚠️" if r.status == CheckStatus.WARNING else "❌" if r.status == CheckStatus.CRITICAL else "❓"
        print(f"{status_icon} [{r.check_id}] {r.name}: {r.message}")
