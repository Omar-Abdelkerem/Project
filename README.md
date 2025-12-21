# Fast ID System - Flask Web Application

A comprehensive Flask-based web application for managing National ID card applications with role-based access control (Citizen, Admin, Delivery Agent).

## 🏗️ Architecture

This project follows the **Model-View-Controller (MVC)** pattern:

- **Models**: Data structures (`models/`)
- **Views**: HTML templates (`templates/`)
- **Controllers**: Business logic (`controllers/`)

## 📋 Features

### Citizen Features
- ✅ Submit new applications with Tracking ID
- ✅ Upload supporting documents (PDF, JPG, PNG, max 5MB)
- ✅ View "My Applications" dashboard
- ✅ Track application status by Tracking ID
- ✅ View status history/timeline
- ✅ Receive notifications for status changes

### Admin Features
- ✅ View all applications
- ✅ Filter by status (Pending, In Process, All)
- ✅ Approve/Reject applications
- ✅ Auto-create delivery records on approval

### Delivery Agent Features
- ✅ View assigned deliveries
- ✅ Update delivery status (Pending → Out for Delivery → Delivered/Failed)
- ✅ Timestamp tracking for each status change
- ✅ Auto-sync with Request status

### System Features
- ✅ Notification system
- ✅ Audit logging
- ✅ Session-based authentication
- ✅ Role-based access control

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SW
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open browser: `http://localhost:5000`

## 🐳 Docker Deployment

### Build Docker Image
```bash
docker build -t fast-id-system:latest .
```

### Run Container
```bash
docker run -d -p 5000:5000 --name fast-id-system fast-id-system:latest
```

### Using Docker Compose
```bash
docker-compose up -d
```

## 🧪 Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=controllers --cov=models --cov-report=html
```

## 📁 Project Structure

```
SW/
├── app.py                      # Main Flask application
├── controllers/                # MVC Controllers
│   ├── admin_controller.py
│   ├── citizen_controller.py
│   ├── delivery_controller.py
│   └── UserController.py
├── models/                     # MVC Models
│   ├── request.py
│   └── UserModel.py
├── repositories/               # Repository Pattern
│   └── request_repository.py
├── core/                       # Core utilities
│   └── file_singleton.py
├── templates/                  # MVC Views
│   ├── admin/
│   ├── citizen/
│   └── ...
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   ├── img/
│   └── uploads/
├── data/                       # CSV data storage
│   ├── users.csv
│   ├── requests.csv
│   ├── deliveries.csv
│   ├── notifications.csv
│   └── audit_log.csv
├── tests/                      # Unit tests
│   ├── test_admin_actions.py
│   └── test_citizen_features.py
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
└── README.md                  # This file
```

## 🔐 Default Users

### Admin
- Email: `admin@system.com`
- Password: `admin123`
- Role: ADMIN

### Delivery Agent
- Email: `agent@system.com`
- Password: `agent123`
- Role: DELIVERY

### Citizen
- Register at `/register` or use existing account

## 📊 Data Storage

The application uses CSV files for data storage:
- `data/users.csv` - User accounts
- `data/requests.csv` - Applications/Requests
- `data/deliveries.csv` - Delivery records
- `data/notifications.csv` - User notifications
- `data/audit_log.csv` - System audit logs

## 🔄 Workflow

1. **Citizen** submits application → Status: Pending
2. **Admin** reviews and approves → Status: Approved, Delivery created
3. **Delivery Agent** updates status → Pending → Out for Delivery → Delivered/Failed
4. **System** creates notifications and audit logs for each action

## 🛠️ Development

### MVC Pattern Implementation

- **Controllers**: Handle HTTP requests, business logic
- **Models**: Define data structures
- **Views**: HTML templates with Jinja2
- **Repositories**: Data access layer (CSV operations)

### Design Patterns Used

- ✅ **MVC Pattern** (Mandatory)
- ✅ **Repository Pattern** (Bonus)
- ✅ **Singleton Pattern** (Bonus - FileSingleton)

## 🚢 CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:
- Runs tests on push/PR
- Builds Docker image
- Validates code quality

## 📝 API Endpoints

### Citizen Routes
- `GET /citizen/dashboard` - View applications
- `GET/POST /citizen/apply` - Submit application
- `GET/POST /citizen/track` - Track application
- `GET /citizen/notifications` - View notifications

### Admin Routes
- `GET /admin` - Admin dashboard
- `POST /admin/action` - Approve/Reject
- `POST /admin/filter` - Filter requests

### Delivery Routes
- `GET /delivery` - Delivery dashboard
- `POST /delivery/update` - Update status

## 🐛 Troubleshooting

### CSV Path Issues
- Ensure `data/` directory exists
- Check file permissions

### File Upload Issues
- Ensure `static/uploads/` directory exists and is writable
- Check file size limits (5MB max)

### Session Issues
- Clear browser cookies
- Check Flask secret key configuration

## 📄 License

This project is for educational purposes.

## 👥 Team

- Member 1: Citizen Features
- Member 2: Delivery Features
- Member 3: Notifications & Testing
- Member 4: DevOps & Documentation

## 📚 Documentation

- See `PHASE5_COMPLETE_IMPLEMENTATION.md` for detailed implementation guide
- See `IMPLEMENTATION_PLAN.md` for project planning
- Technical documentation available in project docs

---

**Status**: ✅ Phase 5 Ready - All features implemented and tested
