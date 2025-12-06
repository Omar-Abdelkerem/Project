import csv
from run import app
import app.controllers.admin_controller as admin_controller


def write_csv(path, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['RequestID', 'Citizen', 'Type', 'Status'])
        writer.writeheader()
        writer.writerows(rows)


def test_admin_action_flash_and_csv_update(tmp_path):
    csv_path = tmp_path / "requests.csv"
    write_csv(csv_path, [{'RequestID': 'R-TST', 'Citizen': 'Test', 'Type': 'Pickup', 'Status': 'Pending'}])

    admin_controller.CSV_PATH = str(csv_path)

    client = app.test_client()
    resp = client.post('/admin/action', data={'request_id': 'R-TST', 'action': 'approve'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'approved' in resp.data.lower()

    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert rows[0].get('Status') == 'Approved' or rows[0].get('status') == 'Approved'


def test_admin_action_reject(tmp_path):
    csv_path = tmp_path / "requests_reject.csv"
    write_csv(csv_path, [{'RequestID': 'R-REJ', 'Citizen': 'TestUser', 'Type': 'Delivery', 'Status': 'Pending'}])

    admin_controller.CSV_PATH = str(csv_path)

    client = app.test_client()
    resp = client.post('/admin/action', data={'request_id': 'R-REJ', 'action': 'reject'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'reject' in resp.data.lower()

    with open(csv_path, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert rows[0].get('Status') == 'Rejected'


def test_admin_action_missing_request_id(tmp_path):
    csv_path = tmp_path / "requests_missing.csv"
    write_csv(csv_path, [{'RequestID': 'R-TEST', 'Citizen': 'User', 'Type': 'Pickup', 'Status': 'Pending'}])

    admin_controller.CSV_PATH = str(csv_path)

    client = app.test_client()
    resp = client.post('/admin/action', data={'action': 'approve'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'invalid' in resp.data.lower()


def test_admin_action_invalid_action(tmp_path):
    csv_path = tmp_path / "requests_invalid.csv"
    write_csv(csv_path, [{'RequestID': 'R-INV', 'Citizen': 'User', 'Type': 'Pickup', 'Status': 'Pending'}])

    admin_controller.CSV_PATH = str(csv_path)

    client = app.test_client()
    resp = client.post('/admin/action', data={'request_id': 'R-INV', 'action': 'invalid_action'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'unknown' in resp.data.lower()


def test_admin_filter_pending(tmp_path):
    csv_path = tmp_path / "requests_filter.csv"
    write_csv(csv_path, [
        {'RequestID': 'R-1', 'Citizen': 'Ali', 'Type': 'Pickup', 'Status': 'Pending'},
        {'RequestID': 'R-2', 'Citizen': 'Mia', 'Type': 'Delivery', 'Status': 'Approved'},
    ])

    admin_controller.CSV_PATH = str(csv_path)

    client = app.test_client()
    resp = client.post('/admin/filter', data={'filter': 'pending'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'R-1' in resp.data
    assert b'Ali' in resp.data
