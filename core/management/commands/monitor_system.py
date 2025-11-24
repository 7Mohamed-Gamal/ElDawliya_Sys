"""
System Monitoring Management Command
==================================

Command to run system monitoring checks and send alerts
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import time
import logging

from core.services.monitoring_service import (
    system_monitor,
    performance_analyzer,
    alert_manager
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class"""
    help = 'Run system monitoring checks and send alerts'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Monitoring interval in seconds (default: 60)',
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run monitoring once and exit',
        )
        parser.add_argument(
            '--check-health',
            action='store_true',
            help='Check system health only',
        )
        parser.add_argument(
            '--send-report',
            action='store_true',
            help='Send monitoring report',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )

    def handle(self, *args, **options):
        """handle function"""
        self.verbosity = options['verbosity']
        self.verbose = options['verbose']

        if options['check_health']:
            self.check_system_health()
            return

        if options['send_report']:
            self.send_monitoring_report()
            return

        if options['once']:
            self.run_monitoring_cycle()
        else:
            self.run_continuous_monitoring(options['interval'])

    def run_continuous_monitoring(self, interval):
        """Run continuous monitoring with specified interval"""

        self.stdout.write(
            self.style.SUCCESS(f'Starting continuous monitoring (interval: {interval}s)')
        )

        try:
            while True:
                start_time = time.time()

                self.run_monitoring_cycle()

                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)

                if sleep_time > 0:
                    if self.verbose:
                        self.stdout.write(f'Sleeping for {sleep_time:.1f} seconds...')
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nMonitoring stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Monitoring error: {e}')
            )
            logger.error(f'Monitoring error: {e}')

    def run_monitoring_cycle(self):
        """Run a single monitoring cycle"""

        if self.verbose:
            self.stdout.write('Running monitoring cycle...')

        try:
            # Get system metrics
            system_metrics = system_monitor.get_system_metrics()

            if 'error' in system_metrics:
                self.stdout.write(
                    self.style.ERROR(f'Error getting system metrics: {system_metrics["error"]}')
                )
                return

            # Get performance metrics
            performance_metrics = performance_analyzer.get_performance_summary(hours=1)

            if 'error' in performance_metrics:
                self.stdout.write(
                    self.style.WARNING(f'Error getting performance metrics: {performance_metrics["error"]}')
                )
                performance_metrics = {}

            # Check for alerts
            alert_manager.check_alerts(system_metrics, performance_metrics)

            # Log current status
            if self.verbose:
                self.log_current_status(system_metrics, performance_metrics)

            # Check for critical issues
            self.check_critical_issues(system_metrics, performance_metrics)

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in monitoring cycle: {e}')
            )
            logger.error(f'Error in monitoring cycle: {e}')

    def check_system_health(self):
        """Check and display system health"""

        self.stdout.write('Checking system health...')

        try:
            health_status = system_monitor.check_system_health()

            # Display overall status
            status_color = self.style.SUCCESS if health_status['overall_status'] == 'healthy' else \
                          self.style.WARNING if health_status['overall_status'] == 'warning' else \
                          self.style.ERROR

            self.stdout.write(
                status_color(f'Overall Status: {health_status["overall_status"].upper()}')
            )

            # Display individual checks
            if 'checks' in health_status:
                self.stdout.write('\nHealth Checks:')
                for check in health_status['checks']:
                    check_color = self.style.SUCCESS if check['status'] == 'healthy' else \
                                 self.style.WARNING if check['status'] == 'warning' else \
                                 self.style.ERROR

                    self.stdout.write(
                        f'  {check_color(check["status"].upper())}: {check["name"]} - {check["message"]}'
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error checking system health: {e}')
            )

    def send_monitoring_report(self):
        """Send monitoring report"""

        self.stdout.write('Generating and sending monitoring report...')

        try:
            # Get comprehensive metrics
            system_metrics = system_monitor.get_system_metrics()
            db_metrics = system_monitor.get_database_metrics()
            app_metrics = system_monitor.get_application_metrics()
            performance_metrics = performance_analyzer.get_performance_summary(hours=24)
            health_status = system_monitor.check_system_health()

            # Generate report
            report = self.generate_report(
                system_metrics, db_metrics, app_metrics,
                performance_metrics, health_status
            )

            # Send report
            system_monitor.send_alert(
                alert_type='Daily Monitoring Report',
                message=report,
                severity='info'
            )

            self.stdout.write(
                self.style.SUCCESS('Monitoring report sent successfully')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error sending monitoring report: {e}')
            )

    def generate_report(self, system_metrics, db_metrics, app_metrics,
                       performance_metrics, health_status):
        """Generate monitoring report"""

        report = f"""
تقرير مراقبة النظام - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

الحالة العامة: {health_status.get('overall_status', 'unknown').upper()}

مقاييس النظام:
- استخدام المعالج: {system_metrics.get('cpu', {}).get('usage_percent', 0):.1f}%
- استخدام الذاكرة: {system_metrics.get('memory', {}).get('usage_percent', 0):.1f}%
- استخدام القرص: {system_metrics.get('disk', {}).get('usage_percent', 0):.1f}%

قاعدة البيانات:
- الاتصالات النشطة: {db_metrics.get('connections', {}).get('active', 0)}
- حجم قاعدة البيانات: {db_metrics.get('size_mb', 0):.1f} MB

الأداء (آخر 24 ساعة):
- إجمالي الطلبات: {performance_metrics.get('total_requests', 0):,}
- متوسط وقت الاستجابة: {performance_metrics.get('avg_response_time', 0):.3f}s
- معدل الأخطاء: {performance_metrics.get('error_rate', 0):.2f}%

المستخدمون:
- إجمالي المستخدمين: {app_metrics.get('users', {}).get('total', 0)}
- المستخدمون النشطون اليوم: {app_metrics.get('users', {}).get('active_today', 0)}

فحوصات الصحة:
"""

        if 'checks' in health_status:
            for check in health_status['checks']:
                status_symbol = '✓' if check['status'] == 'healthy' else \
                               '⚠' if check['status'] == 'warning' else '✗'
                report += f"- {status_symbol} {check['name']}: {check['message']}\n"

        report += f"\n{'='*60}\nتم إنشاء التقرير تلقائياً بواسطة نظام مراقبة الدولية"

        return report

    def log_current_status(self, system_metrics, performance_metrics):
        """Log current system status"""

        cpu_usage = system_metrics.get('cpu', {}).get('usage_percent', 0)
        memory_usage = system_metrics.get('memory', {}).get('usage_percent', 0)
        disk_usage = system_metrics.get('disk', {}).get('usage_percent', 0)

        total_requests = performance_metrics.get('total_requests', 0)
        avg_response_time = performance_metrics.get('avg_response_time', 0)
        error_rate = performance_metrics.get('error_rate', 0)

        self.stdout.write(
            f'Status: CPU {cpu_usage:.1f}% | Memory {memory_usage:.1f}% | '
            f'Disk {disk_usage:.1f}% | Requests {total_requests} | '
            f'Response {avg_response_time:.3f}s | Errors {error_rate:.2f}%'
        )

    def check_critical_issues(self, system_metrics, performance_metrics):
        """Check for critical issues that need immediate attention"""

        critical_issues = []

        # Check CPU usage
        cpu_usage = system_metrics.get('cpu', {}).get('usage_percent', 0)
        if cpu_usage > 95:
            critical_issues.append(f'Critical CPU usage: {cpu_usage:.1f}%')

        # Check memory usage
        memory_usage = system_metrics.get('memory', {}).get('usage_percent', 0)
        if memory_usage > 95:
            critical_issues.append(f'Critical memory usage: {memory_usage:.1f}%')

        # Check disk usage
        disk_usage = system_metrics.get('disk', {}).get('usage_percent', 0)
        if disk_usage > 95:
            critical_issues.append(f'Critical disk usage: {disk_usage:.1f}%')

        # Check error rate
        error_rate = performance_metrics.get('error_rate', 0)
        if error_rate > 10:
            critical_issues.append(f'High error rate: {error_rate:.2f}%')

        # Check response time
        avg_response_time = performance_metrics.get('avg_response_time', 0)
        if avg_response_time > 5:
            critical_issues.append(f'Slow response time: {avg_response_time:.3f}s')

        # Report critical issues
        if critical_issues:
            self.stdout.write(
                self.style.ERROR('CRITICAL ISSUES DETECTED:')
            )
            for issue in critical_issues:
                self.stdout.write(
                    self.style.ERROR(f'  - {issue}')
                )

            # Send immediate alert
            system_monitor.send_alert(
                alert_type='Critical System Issues',
                message='\n'.join(critical_issues),
                severity='critical'
            )
