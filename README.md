# Admin Dashboard for Request Management

## Overview

This Flask application provides a web-based admin dashboard for managing citizen service requests (Pickup, Delivery, Return). It enables administrators to approve, reject, or filter requests with real-time CSV persistence.

## Features

- **Dashboard View**: Display all requests in a responsive table with request ID, citizen name, service type, and status
- **Status Filtering**: Filter requests by status (All, Pending, In Process) using dedicated button controls
- **Approval Workflow**: Approve or reject pending requests with a single click
- **Change Action**: Modify prior approval/rejection decisions using a "Change" button
- **Dispatched Label**: Automatically shows "Dispatched" status for delivery and pickup items
- **Flash Messages**: User-friendly success/error feedback after each action
- **Logging & Error Handling**: Comprehensive logging of all operations with graceful error recovery
- **Responsive Design**: Mobile-friendly UI with rounded buttons and centered layout

## Architecture

### Technology Stack
- **Backend**: Flask (Python web framework)
- **Data Storage**: CSV file (lightweight, no database setup required)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: pytest with temporary CSV fixtures

### Project Structure
```
My_Id/
├── run.py                          # Application entry point
├── app/
│   ├── __init__.py
│   ├── controllers/
│   │   └── admin_controller.py    # Request handling routes
│   ├── repositories/
│   │   └── request_repository.py  # Data access layer
│   ├── models/
│   │   └── request.py             # Request model class
│   ├── core/
│   │   └── file_singleton.py      # Singleton CSV reader
│   ├── data/
│   │   └── requests.csv           # Data persistence file
│   ├── static/
│   │   └── admin.css              # Stylesheet with animations
│   └── templates/
│       └── admin/
│           └── admin.html         # Dashboard UI
└── tests/
    ├── test_admin_actions.py      # Controller tests
    └── test_request_repository.py # Repository tests
```

## Getting Started

### Prerequisites
- Python 3.7+
- pip package manager

### Installation

1. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   # or
   source .venv/bin/activate  # On macOS/Linux
   ```

2. **Install Flask**:
   ```bash
   pip install flask pytest
   ```

3. **Navigate to project directory**:
   ```bash
   cd My_Id
   ```

### Running the Application

Start the Flask development server:
```bash
python run.py
```

The application will be available at: **http://127.0.0.1:5000/admin**

### Running Tests

Execute the test suite to verify functionality:
```bash
pytest tests/ -v
```

For test coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Usage

### Admin Dashboard
1. Open **http://127.0.0.1:5000/admin**
2. View all requests in the table below the filter buttons

### Filtering Requests
- Click **"View All Requests"** to see all entries
- Click **"Pending Requests"** to see only requests awaiting approval
- Click **"In Process Requests"** to see active requests

### Approving/Rejecting Requests
1. Locate a request with status "Pending"
2. Click **"Approve"** to mark as approved (or **"Reject"** to reject)
3. Observe the flash message confirming the action
4. CSV file updates automatically

### Changing Prior Decisions
1. For approved/rejected requests (non-Delivery/Pickup), a **"Change"** button appears
2. Click **"Change"** to reveal the Approve/Reject buttons again
3. Select a new action to override the previous decision
4. Click **"Cancel"** to hide the action buttons

### Dispatched Status
- Requests with type "Delivery" or "Picked up" automatically show **"Dispatched"** label instead of a Change button

## CSV Data Format

The `requests.csv` file stores request data with the following columns:

```csv
RequestID,Citizen,Type,Status
R-1001,Ali Mohamed,Pickup,Approved
R-1002,Mariam F.,Delivery,In Process
R-1003,Ahmed Hassan,Return,Pending
```

- **RequestID**: Unique identifier (e.g., R-1001)
- **Citizen**: Name of the requesting citizen
- **Type**: Service type (Pickup, Delivery, Return)
- **Status**: Current status (Pending, In Process, Approved, Rejected)

## Code Examples

### Approve a Request
```python
from app.controllers.admin_controller import update_request_status
update_request_status("R-1001", "Approved")
```

### Filter Pending Requests
```python
from app.controllers.admin_controller import filter_requests
pending = filter_requests("pending")
for req in pending:
    print(f"{req['RequestID']}: {req['Citizen']}")
```

### Access CSV Data
```python
from app.repositories.request_repository import RequestRepository
repo = RequestRepository("app/data/requests.csv")
all_requests = repo.get_all()
repo.update_status("R-1001", "Approved")
```

## Error Handling

The application includes robust error handling for:
- **Missing Request ID or Action**: Logs warning and displays error flash message
- **Invalid Actions**: Validates action is either "approve" or "reject"
- **File Not Found**: Catches FileNotFoundError when CSV is missing
- **IO Errors**: Handles write failures with detailed logging

All errors are logged to the console for debugging.

## Logging

Application logs are printed to stdout during development. Key log levels:
- **INFO**: Successfully completed actions (e.g., request approved)
- **WARNING**: Potential issues (e.g., request not found, missing parameters)
- **ERROR**: Failed operations (e.g., CSV write failure)
- **DEBUG**: Detailed operation tracking (e.g., CSV written with N rows)

Example log output:
```
INFO:app.controllers.admin_controller:Processing approve for request_id=R-1001
INFO:app.controllers.admin_controller:Successfully updated R-1001 to Approved
DEBUG:app.controllers.admin_controller:CSV file written successfully with 5 rows
```

## Customization

### Adding Custom Fields
Extend the CSV schema by adding new columns. Update the test `write_csv()` function:
```python
writer = csv.DictWriter(f, fieldnames=['RequestID', 'Citizen', 'Type', 'Status', 'Priority'])
```

### Styling
Modify `app/static/admin.css` to customize colors, layout, or animations:
```css
.pill-btn {
    background: #yourcolor;
    transition: all 0.3s ease;
}
```

### Adding Routes
Extend `app/controllers/admin_controller.py` to add new endpoints:
```python
@admin_bp.route("/admin/export", methods=["GET"])
def export_csv():
    # Custom export logic
    pass
```

## Future Enhancements

- [ ] Migrate from CSV to SQLite/PostgreSQL database
- [ ] Add user authentication and role-based access control
- [ ] Implement audit trail for approval history
- [ ] Add email notifications on request status change
- [ ] Support file uploads for request attachments
- [ ] Add pagination for large request lists
- [ ] Convert to AJAX for inline row updates without page reload

## Testing

The application includes comprehensive test coverage:

### Test Cases
1. **test_admin_action_flash_and_csv_update**: Verify approve action updates CSV and shows flash
2. **test_admin_action_reject**: Verify reject action works correctly
3. **test_admin_action_missing_request_id**: Ensure error handling for missing parameters
4. **test_admin_action_invalid_action**: Validate unknown actions are rejected
5. **test_admin_filter_pending**: Verify filtering by status works

### Running Specific Tests
```bash
pytest tests/test_admin_actions.py::test_admin_action_approve -v
```

## Troubleshooting

### Application won't start
- Ensure Flask is installed: `pip install flask`
- Check Python path: `python --version` should be 3.7+
- Verify working directory: `cd My_Id`

### CSV file not found
- Ensure `app/data/requests.csv` exists
- Check file path in `admin_controller.py`: `CSV_PATH = ...`

### Tests failing
- Ensure pytest is installed: `pip install pytest`
- Check that app can be imported: `python -c "from run import app; print('OK')"`

### Flash messages not showing
- Verify `app.secret_key` is set in `run.py`
- Check template includes `get_flashed_messages()` block

## License

This project is provided as-is for educational purposes.

## Contact & Support

For questions or issues, contact the development team or file an issue in the project repository.