"""
Unit Tests for Citizen Features
Tests application submission, tracking, and notifications
"""
import pytest
import os
import csv
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Import the app and controllers
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from controllers.citizen_controller import (
    generate_tracking_id,
    allowed_file,
    create_notification,
    log_audit_action
)


@pytest.fixture
def client():
    """Create a test client."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    with app.test_client() as client:
        yield client


@pytest.fixture
def temp_data_dir():
    """Create a temporary data directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


def test_generate_tracking_id():
    """Test that tracking ID is generated correctly."""
    tracking_id = generate_tracking_id()
    assert tracking_id.startswith('TRK-')
    assert len(tracking_id) == 13  # TRK- + 8 hex chars


def test_allowed_file():
    """Test file extension validation."""
    assert allowed_file('document.pdf') == True
    assert allowed_file('image.jpg') == True
    assert allowed_file('photo.png') == True
    assert allowed_file('file.txt') == False
    assert allowed_file('script.exe') == False


def test_create_notification(temp_data_dir):
    """Test notification creation."""
    # Mock the DATA_DIR
    with patch('controllers.citizen_controller.DATA_DIR', temp_data_dir):
        create_notification('user123', 'req456', 'Test message', 'info')
        
        # Check if notification was created
        notifications_file = os.path.join(temp_data_dir, 'notifications.csv')
        assert os.path.exists(notifications_file)
        
        # Read and verify
        with open(notifications_file, 'r') as f:
            reader = csv.DictReader(f)
            notifications = list(reader)
            assert len(notifications) == 1
            assert notifications[0]['UserID'] == 'user123'
            assert notifications[0]['Message'] == 'Test message'


def test_log_audit_action(temp_data_dir):
    """Test audit log creation."""
    with patch('controllers.citizen_controller.DATA_DIR', temp_data_dir):
        log_audit_action('admin1', 'ADMIN', 'APPROVE', 'Request', 'req123', 'Test action')
        
        # Check if audit log was created
        audit_file = os.path.join(temp_data_dir, 'audit_log.csv')
        assert os.path.exists(audit_file)
        
        # Read and verify
        with open(audit_file, 'r') as f:
            reader = csv.DictReader(f)
            logs = list(reader)
            assert len(logs) == 1
            assert logs[0]['ActorID'] == 'admin1'
            assert logs[0]['Action'] == 'APPROVE'


def test_citizen_dashboard_requires_login(client):
    """Test that citizen dashboard requires authentication."""
    response = client.get('/citizen/dashboard')
    assert response.status_code == 302  # Redirect to login


def test_apply_page_requires_login(client):
    """Test that apply page requires authentication."""
    response = client.get('/citizen/apply')
    assert response.status_code == 302  # Redirect to login
