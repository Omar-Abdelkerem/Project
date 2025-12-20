
import unittest
import os
import shutil
from app import app
from core.storage import csv_store, repository

class TestIntegration(unittest.TestCase):
    
    TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data_test_integ')
    
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Setup Test Data Dir
        if not os.path.exists(self.TEST_DATA_DIR):
            os.makedirs(self.TEST_DATA_DIR)
        
        # Patch CSV Store to use test dir
        self.original_data_dir = csv_store.DATA_DIR
        csv_store.DATA_DIR = self.TEST_DATA_DIR
        
        self._init_csv('users.csv', 'userid,nationalid,name,email,phone,passwordhash,role')
        self._init_csv('applications.csv', 'appid,userid,trackingid,type,subtype,status,createdat')
        self._init_csv('notifications.csv', 'notifid,userid,templateid,medium,sentat')
        
        # Create a user
        self.user = repository.create_user({"name": "Integration User", "role": "CITIZEN"})

    def tearDown(self):
        csv_store.DATA_DIR = self.original_data_dir
        if os.path.exists(self.TEST_DATA_DIR):
            try:
                shutil.rmtree(self.TEST_DATA_DIR)
            except:
                pass

    def _init_csv(self, filename, headers):
        with open(os.path.join(self.TEST_DATA_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(headers + '\n')

    def test_application_flow_and_notification(self):
        # 1. Apply
        response = self.client.post('/apply', data={
            'userid': self.user['userid'],
            'type': 'Passport',
            'subtype': 'New'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify app created
        apps = repository.get_applications_for_user(self.user['userid'])
        self.assertEqual(len(apps), 1)
        appid = apps[0]['appid']
        self.assertEqual(apps[0]['status'], 'Pending')
        
        # Verify Notification (APP_SUBMIT)
        notifs = repository.get_notifications_for_user(self.user['userid'])
        self.assertEqual(len(notifs), 1)
        self.assertEqual(notifs[0]['templateid'], 'APP_SUBMIT')
        
        # 2. Admin Approve
        response = self.client.post('/admin/action', data={
            'request_id': appid,
            'action': 'approve'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Verify Status
        updated_app = repository.get_application_by_id(appid)
        self.assertEqual(updated_app['status'], 'Approved')
        
        # Verify Notification (APP_APPROVE)
        notifs = repository.get_notifications_for_user(self.user['userid'])
        self.assertEqual(len(notifs), 2)
        # Check last one
        self.assertEqual(notifs[1]['templateid'], 'APP_APPROVE')

if __name__ == '__main__':
    unittest.main()
