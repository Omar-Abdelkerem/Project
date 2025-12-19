"""
Application Repository - Handles all data operations for applications
"""

import csv
import os
from datetime import datetime
from models.application import Application


class ApplicationRepository:
    def __init__(self, csv_path='data/applications.csv'):
        """
        Initialize repository with CSV file path
        
        Args:
            csv_path: Path to the applications CSV file
        """
        self.csv_path = csv_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create CSV file with headers if it doesn't exist"""
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        
        # Create file with headers if it doesn't exist
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'tracking_id', 'user_id', 'user_name', 'application_type',
                    'description', 'status', 'document_path', 'created_at',
                    'updated_at', 'notes'
                ])
    
    def generate_tracking_id(self):
        """
        Generate unique tracking ID in format: APP-YYYYMMDD-XXXX
        
        Returns:
            str: Unique tracking ID
        """
        date_str = datetime.now().strftime('%Y%m%d')
        
        # Get all existing applications to find the next number
        applications = self.get_all()
        
        # Filter applications from today
        today_apps = [app for app in applications 
                     if app.tracking_id.startswith(f'APP-{date_str}')]
        
        # Get next number
        next_num = len(today_apps) + 1
        
        return f'APP-{date_str}-{next_num:04d}'
    
    def save(self, application):
        """
        Save new application to CSV
        
        Args:
            application: Application object to save
            
        Returns:
            bool: True if successful
        """
        try:
            with open(self.csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'tracking_id', 'user_id', 'user_name', 'application_type',
                    'description', 'status', 'document_path', 'created_at',
                    'updated_at', 'notes'
                ])
                writer.writerow(application.to_dict())
            return True
        except Exception as e:
            print(f"Error saving application: {str(e)}")
            return False
    
    def get_all(self):
        """
        Get all applications from CSV
        
        Returns:
            list: List of Application objects
        """
        applications = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    applications.append(Application.from_dict(row))
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error reading applications: {str(e)}")
            return []
        
        return applications
    
    def get_by_user_id(self, user_id):
        """
        Get all applications for a specific user
        
        Args:
            user_id: User ID to filter by
            
        Returns:
            list: List of Application objects for this user
        """
        all_apps = self.get_all()
        return [app for app in all_apps if app.user_id == user_id]
    
    def get_by_tracking_id(self, tracking_id):
        """
        Get application by tracking ID
        
        Args:
            tracking_id: Tracking ID to search for
            
        Returns:
            Application: Application object or None if not found
        """
        all_apps = self.get_all()
        for app in all_apps:
            if app.tracking_id == tracking_id:
                return app
        return None
    
    def update_status(self, tracking_id, new_status, notes=None):
        """
        Update application status and notes
        
        Args:
            tracking_id: Tracking ID of application to update
            new_status: New status value
            notes: Optional admin notes
            
        Returns:
            bool: True if successful
        """
        try:
            applications = self.get_all()
            updated = False
            
            # Find and update the application
            for app in applications:
                if app.tracking_id == tracking_id:
                    app.status = new_status
                    app.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    if notes:
                        app.notes = notes
                    updated = True
                    break
            
            if not updated:
                return False
            
            # Write all applications back to CSV
            with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'tracking_id', 'user_id', 'user_name', 'application_type',
                    'description', 'status', 'document_path', 'created_at',
                    'updated_at', 'notes'
                ])
                writer.writeheader()
                for app in applications:
                    writer.writerow(app.to_dict())
            
            return True
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            return False
    
    def get_statistics(self):
        """
        Get application statistics
        
        Returns:
            dict: Statistics including counts by status
        """
        applications = self.get_all()
        
        stats = {
            'total': len(applications),
            'pending': 0,
            'in_review': 0,
            'approved': 0,
            'rejected': 0
        }
        
        for app in applications:
            status_lower = app.status.lower().replace(' ', '_')
            if status_lower in stats:
                stats[status_lower] += 1
        
        return stats
