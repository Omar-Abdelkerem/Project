import unittest
import os
import shutil
import time
from core.storage import csv_store, repository
from core.services import notification_service

class TestDomainLogic(unittest.TestCase):
    
    TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_test')
    
    def setUp(self):
        """Setup a fresh test data directory before each test."""
        if not os.path.exists(self.TEST_DATA_DIR):
            os.makedirs(self.TEST_DATA_DIR)
        
        # Patch the DATA_DIR in csv_store to use our test directory
        self.original_data_dir = csv_store.DATA_DIR
        csv_store.DATA_DIR = self.TEST_DATA_DIR
        
        # Initialize basic files
        self._init_csv('users.csv', 'userid,nationalid,name,email,phone,passwordhash,role')
        self._init_csv('applications.csv', 'appid,userid,trackingid,type,subtype,status,createdat')
        self._init_csv('documents.csv', 'docid,appid,filename,filetype,sizebytes,storagepath')
        self._init_csv('deliveries.csv', 'deliveryid,appid,courierid,trackingnumber,currentstatus,lastupdate')
        self._init_csv('notifications.csv', 'notifid,userid,templateid,medium,sentat')
        self._init_csv('audit_logs.csv', 'logid,actorid,action,targetid,details,timestamp')

    def tearDown(self):
        """Clean up test data after each test."""
        # Restore original DATA_DIR
        csv_store.DATA_DIR = self.original_data_dir
        
        # Remove test directory
        if os.path.exists(self.TEST_DATA_DIR):
            try:
                shutil.rmtree(self.TEST_DATA_DIR)
            except PermissionError:
                # Retry once if file lock lingers (Windows specific)
                time.sleep(0.1)
                shutil.rmtree(self.TEST_DATA_DIR, ignore_errors=True)

    def _init_csv(self, filename, headers):
        with open(os.path.join(self.TEST_DATA_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(headers + '\n')

    def test_create_application_persists_row(self):
        """Test that creating an application saves it to CSV."""
        user = repository.create_user({"name": "Test User", "email": "test@example.com", "role": "CITIZEN"})
        userid = user['userid']
        
        app = repository.create_application(userid, "Passport", "Renew", "Pending")
        
        # Read back
        user_apps = repository.get_applications_for_user(userid)
        self.assertEqual(len(user_apps), 1)
        self.assertEqual(user_apps[0]['appid'], app['appid'])
        self.assertEqual(user_apps[0]['type'], "Passport")
        self.assertEqual(user_apps[0]['status'], "Pending")

    def test_update_application_status_changes_csv(self):
        """Test updating application status."""
        user = repository.create_user({"name": "Test User", "role": "CITIZEN"})
        app = repository.create_application(user['userid'], "Passport", "New", "Pending")
        
        updated = repository.update_application_status(app['appid'], "Approved")
        self.assertEqual(updated['status'], "Approved")
        
        # Verify persistence
        fetched = repository.get_application_by_id(app['appid'])
        self.assertEqual(fetched['status'], "Approved")

    def test_document_upload_metadata_saved(self):
        """Test document creation."""
        user = repository.create_user({"name": "Test User", "role": "CITIZEN"})
        app = repository.create_application(user['userid'], "Passport", "New", "Pending")
        
        doc = repository.create_document(app['appid'], "photo.jpg", "image/jpeg", 1024, "/tmp/photo.jpg")
        
        docs = repository.get_documents_for_app(app['appid'])
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]['filename'], "photo.jpg")
        self.assertEqual(docs[0]['sizebytes'], "1024")

    def test_create_delivery_and_update_status(self):
        """Test delivery workflow."""
        user = repository.create_user({"name": "Test User", "role": "CITIZEN"})
        app = repository.create_application(user['userid'], "Passport", "New", "Approved")
        
        delivery = repository.create_delivery(app['appid'], "courier_1", "TRACK123", "Out for Delivery")
        self.assertEqual(delivery['currentstatus'], "Out for Delivery")
        
        updated = repository.update_delivery_status(delivery['deliveryid'], "Delivered")
        self.assertEqual(updated['currentstatus'], "Delivered")
        
        # Verify persistence
        fetched = repository.get_delivery_for_app(app['appid'])
        self.assertEqual(fetched['currentstatus'], "Delivered")

    def test_send_status_notification_creates_notification_row(self):
        """Test notification service."""
        user = repository.create_user({"name": "Test User", "role": "CITIZEN"})
        
        # Call service
        notification_service.send_status_notification(user['userid'], "APPLICATION_SUBMITTED", "email")
        
        # Verify
        notifs = repository.get_notifications_for_user(user['userid'])
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0]['templateid'], "APP_SUBMIT")
        self.assertEqual(notifs[0]['medium'], "email")

    def test_atomic_writes_no_duplicate_ids(self):
        """Test distinct IDs generation."""
        # Create multiple users and check IDs
        u1 = repository.create_user({"name": "U1"})
        u2 = repository.create_user({"name": "U2"})
        
        # Users use UUID, so mainly checking they are different
        self.assertNotEqual(u1['userid'], u2['userid'])
        
        # Create applications (use INT ids)
        a1 = repository.create_application(u1['userid'], "Type", "Sub", "Status")
        a2 = repository.create_application(u1['userid'], "Type", "Sub", "Status")
        
        self.assertNotEqual(a1['appid'], a2['appid'])
        self.assertEqual(int(a2['appid']), int(a1['appid']) + 1)

if __name__ == '__main__':
    unittest.main()
