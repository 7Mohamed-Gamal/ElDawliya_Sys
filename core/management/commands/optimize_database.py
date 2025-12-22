"""
Django management command for database optimization
أمر إدارة Django لتحسين قاعدة البيانات
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.cache import cache
from django.utils import timezone
from core.database_optimization import db_optimization_service
from core.data_integration import data_integration_service
import json


class Command(BaseCommand):
    """Command class"""
    help = 'Optimize database performance and analyze query patterns'

    def add_arguments(self, parser):
        """add_arguments function"""
        parser.add_argument(
            '--analyze',
            action='store_true',
            help='Analyze current query performance',
        )
        parser.add_argument(
            '--recommendations',
            action='store_true',
            help='Get index recommendations',
        )
        parser.add_argument(
            '--statistics',
            action='store_true',
            help='Show database statistics',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all optimization caches',
        )
        parser.add_argument(
            '--clear-logs',
            action='store_true',
            help='Clear query performance logs',
        )
        parser.add_argument(
            '--connection-info',
            action='store_true',
            help='Show database connection information',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all optimization tasks',
        )

    def handle(self, *args, **options):
        """handle function"""
        self.stdout.write(
            self.style.SUCCESS('🚀 ElDawliya Database Optimization Tool')
        )
        self.stdout.write('=' * 50)

        if options['all']:
            options.update({
                'analyze': True,
                'recommendations': True,
                'statistics': True,
                'connection_info': True
            })

        if options['analyze']:
            self.analyze_performance()

        if options['recommendations']:
            self.show_recommendations()

        if options['statistics']:
            self.show_statistics()

        if options['connection_info']:
            self.show_connection_info()

        if options['clear_cache']:
            self.clear_caches()

        if options['clear_logs']:
            self.clear_logs()

        if not any(options.values()):
            self.stdout.write(
                self.style.WARNING('No action specified. Use --help for options.')
            )

    def analyze_performance(self):
        """Analyze query performance"""
        self.stdout.write('\n📊 Query Performance Analysis')
        self.stdout.write('-' * 30)

        try:
            performance = db_optimization_service.analyze_query_performance()

            if 'message' in performance:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  {performance['message']}")
                )
                return

            self.stdout.write(f"Total Queries: {performance['total_queries']}")
            self.stdout.write(f"Total Execution Time: {performance['total_execution_time']:.4f}s")
            self.stdout.write(f"Average Execution Time: {performance['average_execution_time']:.4f}s")

            if performance['slowest_queries']:
                self.stdout.write('\n🐌 Slowest Queries:')
                for i, query in enumerate(performance['slowest_queries'][:5], 1):
                    self.stdout.write(
                        f"  {i}. {query['query_name']}: {query['execution_time']:.4f}s"
                    )

            if performance['query_statistics']:
                self.stdout.write('\n📈 Query Statistics:')
                for name, stats in list(performance['query_statistics'].items())[:5]:
                    self.stdout.write(
                        f"  {name}: {stats['count']} calls, "
                        f"avg: {stats['avg_time']:.4f}s, "
                        f"max: {stats['max_time']:.4f}s"
                    )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error analyzing performance: {e}")
            )

    def show_recommendations(self):
        """Show index recommendations"""
        self.stdout.write('\n💡 Index Recommendations')
        self.stdout.write('-' * 30)

        try:
            recommendations = db_optimization_service.get_index_recommendations()

            if not recommendations:
                self.stdout.write(
                    self.style.SUCCESS('✅ No specific recommendations at this time')
                )
                return

            for i, rec in enumerate(recommendations, 1):
                self.stdout.write(f"\n{i}. {rec['type']}")
                self.stdout.write(f"   Table: {rec['table']}")
                self.stdout.write(f"   Column: {rec['column']}")
                self.stdout.write(f"   Recommendation: {rec['recommendation']}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting recommendations: {e}")
            )

    def show_statistics(self):
        """Show database statistics"""
        self.stdout.write('\n📊 Database Statistics')
        self.stdout.write('-' * 30)

        try:
            stats = db_optimization_service.get_database_statistics()

            # Employee statistics
            emp_stats = stats['employees']
            self.stdout.write(f"\n👥 Employees:")
            self.stdout.write(f"   Total: {emp_stats['total']}")
            self.stdout.write(f"   Active: {emp_stats['active']}")

            if emp_stats['by_department']:
                self.stdout.write("   Top Departments:")
                for dept in emp_stats['by_department'][:3]:
                    dept_name = dept['department__dept_name'] or 'Unknown'
                    self.stdout.write(f"     - {dept_name}: {dept['count']}")

            # Task statistics
            task_stats = stats['tasks']
            self.stdout.write(f"\n📋 Tasks:")
            self.stdout.write(f"   Total: {task_stats['total']}")
            self.stdout.write(f"   Active: {task_stats['active']}")
            self.stdout.write(f"   Completed: {task_stats['completed']}")
            self.stdout.write(f"   Overdue: {task_stats['overdue']}")

            # Meeting statistics
            meeting_stats = stats['meetings']
            self.stdout.write(f"\n🤝 Meetings:")
            self.stdout.write(f"   Total: {meeting_stats['total']}")
            self.stdout.write(f"   Upcoming: {meeting_stats['upcoming']}")
            self.stdout.write(f"   This Month: {meeting_stats['this_month']}")

            # Inventory statistics
            inv_stats = stats['inventory']
            self.stdout.write(f"\n📦 Inventory:")
            self.stdout.write(f"   Total Products: {inv_stats['total_products']}")
            self.stdout.write(f"   Low Stock: {inv_stats['low_stock']}")

            # Purchase order statistics
            po_stats = stats['purchase_orders']
            self.stdout.write(f"\n🛒 Purchase Orders:")
            self.stdout.write(f"   Total: {po_stats['total']}")
            self.stdout.write(f"   Pending: {po_stats['pending']}")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting statistics: {e}")
            )

    def show_connection_info(self):
        """Show database connection information"""
        self.stdout.write('\n🔗 Database Connection Info')
        self.stdout.write('-' * 30)

        try:
            conn_info = db_optimization_service.get_connection_info()

            for alias, info in conn_info.items():
                self.stdout.write(f"\n{alias.upper()} Database:")
                self.stdout.write(f"   Engine: {info['engine']}")
                self.stdout.write(f"   Name: {info['name']}")
                self.stdout.write(f"   Host: {info['host']}")
                self.stdout.write(f"   Port: {info['port']}")

                if alias == info['active_db']:
                    self.stdout.write(
                        self.style.SUCCESS("   Status: ACTIVE ✅")
                    )
                else:
                    self.stdout.write("   Status: Inactive")

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error getting connection info: {e}")
            )

    def clear_caches(self):
        """Clear all optimization caches"""
        self.stdout.write('\n🧹 Clearing Caches')
        self.stdout.write('-' * 30)

        try:
            # Clear Django cache
            cache.clear()

            # Clear data integration cache
            data_integration_service.clear_all_cache()

            self.stdout.write(
                self.style.SUCCESS('✅ All caches cleared successfully')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error clearing caches: {e}")
            )

    def clear_logs(self):
        """Clear query performance logs"""
        self.stdout.write('\n🗑️  Clearing Query Logs')
        self.stdout.write('-' * 30)

        try:
            db_optimization_service.clear_query_log()

            self.stdout.write(
                self.style.SUCCESS('✅ Query logs cleared successfully')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error clearing logs: {e}")
            )
