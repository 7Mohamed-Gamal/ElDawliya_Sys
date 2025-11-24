"""
Management command to set up caching infrastructure
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.core.cache import cache
import redis
import sys


class Command(BaseCommand):
    help = 'Set up caching infrastructure (Redis or database cache tables)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-db-cache',
            action='store_true',
            help='Force setup of database cache tables even if Redis is available',
        )
        parser.add_argument(
            '--test-redis',
            action='store_true',
            help='Test Redis connection',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all cache data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up caching infrastructure...'))

        if options['test_redis']:
            self.test_redis_connection()
            return

        if options['clear_cache']:
            self.clear_all_cache()
            return

        # Check if Redis is available
        redis_available = self.check_redis_availability()
        
        if redis_available and not options['force_db_cache']:
            self.setup_redis_cache()
        else:
            self.setup_database_cache()

        self.stdout.write(self.style.SUCCESS('Cache setup completed successfully!'))

    def check_redis_availability(self):
        """Check if Redis is available and configured"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', None)
            if not redis_url:
                self.stdout.write(
                    self.style.WARNING('Redis URL not configured in settings')
                )
                return False

            redis_client = redis.from_url(redis_url)
            redis_client.ping()
            self.stdout.write(
                self.style.SUCCESS('✓ Redis connection successful')
            )
            return True
        except ImportError:
            self.stdout.write(
                self.style.WARNING('Redis package not installed')
            )
            return False
        except (redis.ConnectionError, redis.TimeoutError) as e:
            self.stdout.write(
                self.style.WARNING(f'Redis connection failed: {e}')
            )
            return False
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected Redis error: {e}')
            )
            return False

    def test_redis_connection(self):
        """Test Redis connection and display info"""
        try:
            redis_url = getattr(settings, 'REDIS_URL', None)
            if not redis_url:
                self.stdout.write(
                    self.style.ERROR('Redis URL not configured')
                )
                return

            redis_client = redis.from_url(redis_url)
            
            # Test connection
            redis_client.ping()
            self.stdout.write(
                self.style.SUCCESS('✓ Redis connection successful')
            )
            
            # Get Redis info
            info = redis_client.info()
            self.stdout.write('\nRedis Information:')
            self.stdout.write(f"  Version: {info.get('redis_version', 'Unknown')}")
            self.stdout.write(f"  Mode: {info.get('redis_mode', 'Unknown')}")
            self.stdout.write(f"  Connected clients: {info.get('connected_clients', 0)}")
            self.stdout.write(f"  Used memory: {info.get('used_memory_human', '0B')}")
            self.stdout.write(f"  Total commands processed: {info.get('total_commands_processed', 0)}")
            
            # Test basic operations
            test_key = 'eldawliya_test_key'
            test_value = 'test_value'
            
            redis_client.set(test_key, test_value, ex=60)
            retrieved_value = redis_client.get(test_key).decode('utf-8')
            
            if retrieved_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS('✓ Redis read/write test successful')
                )
                redis_client.delete(test_key)
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Redis read/write test failed')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Redis test failed: {e}')
            )

    def setup_redis_cache(self):
        """Set up Redis caching"""
        self.stdout.write('Setting up Redis cache...')
        
        try:
            # Test cache operations
            cache.set('test_key', 'test_value', 60)
            value = cache.get('test_key')
            
            if value == 'test_value':
                self.stdout.write(
                    self.style.SUCCESS('✓ Redis cache is working correctly')
                )
                cache.delete('test_key')
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Redis cache test failed')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Redis cache setup failed: {e}')
            )

    def setup_database_cache(self):
        """Set up database cache tables"""
        self.stdout.write('Setting up database cache tables...')
        
        try:
            # Create cache tables
            cache_tables = [
                'cache_table',
                'session_cache_table', 
                'query_cache_table',
                'dashboard_cache_table'
            ]
            
            for table_name in cache_tables:
                try:
                    call_command('createcachetable', table_name, verbosity=0)
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Created cache table: {table_name}')
                    )
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        self.stdout.write(
                            self.style.WARNING(f'Cache table {table_name} already exists')
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'Failed to create {table_name}: {e}')
                        )
            
            # Test database cache
            cache.set('test_key', 'test_value', 60)
            value = cache.get('test_key')
            
            if value == 'test_value':
                self.stdout.write(
                    self.style.SUCCESS('✓ Database cache is working correctly')
                )
                cache.delete('test_key')
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Database cache test failed')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Database cache setup failed: {e}')
            )

    def clear_all_cache(self):
        """Clear all cache data"""
        self.stdout.write('Clearing all cache data...')
        
        try:
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('✓ All cache data cleared')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to clear cache: {e}')
            )

    def display_cache_stats(self):
        """Display cache statistics"""
        try:
            from core.services.cache_service import cache_service
            stats = cache_service.get_stats()
            
            self.stdout.write('\nCache Statistics:')
            for key, value in stats.items():
                self.stdout.write(f"  {key}: {value}")
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not retrieve cache stats: {e}')
            )