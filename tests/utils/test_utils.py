
# tests/utils/test_utils.py

import pytest
from django.test import TestCase
from django.db import connections
from django.conf import settings

class ElDawliyaTestCase(TestCase):
    """
    Base test case for ElDawliya system with common setup and teardown
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup_test_database()
        cls.setup_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.teardown_test_data()
        cls.teardown_test_database()
        super().tearDownClass()

    @classmethod
    def setup_test_database(cls):
        """
        Create a separate test database for isolated testing
        """
        test_db_name = f"{settings.DATABASES['default']['NAME']}_test"
        settings.DATABASES['default']['NAME'] = test_db_name
        connections['default'].creation.create_test_db(verbosity=0, autoclobber=True)

    @classmethod
    def teardown_test_database(cls):
        """
        Drop the test database after tests
        """
        test_db_name = settings.DATABASES['default']['NAME']
        connections['default'].creation.destroy_test_db(old_database_name=test_db_name)

    @classmethod
    def setup_test_data(cls):
        """
        Setup common test data
        """
        pass

    @classmethod
    def teardown_test_data(cls):
        """
        Clean up test data
        """
        pass

def pytest_configure(config):
    """
    Configure pytest settings
    """
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )

def pytest_runtest_setup(item):
    """
    Setup test environment before each test
    """
    if 'e2e' in item.keywords:
        # Setup for end-to-end tests
        pass

def pytest_runtest_teardown(item, nextitem):
    """
    Teardown test environment after each test
    """
    if 'e2e' in item.keywords:
        # Teardown for end-to-end tests
        pass
