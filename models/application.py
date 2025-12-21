"""
Application Model - Represents a citizen's application/request
"""

class Application:
    def __init__(self, tracking_id, user_id, user_name, application_type, 
                 description, status="Pending", document_path=None, 
                 created_at=None, updated_at=None, notes=None):
        self.tracking_id = tracking_id
        self.user_id = user_id
        self.user_name = user_name
        self.application_type = application_type
        self.description = description
        self.status = status
        self.document_path = document_path
        self.created_at = created_at
        self.updated_at = updated_at
        self.notes = notes
    
    def to_dict(self):
        return {
            'tracking_id': self.tracking_id,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'application_type': self.application_type,
            'description': self.description,
            'status': self.status,
            'document_path': self.document_path or '',
            'created_at': self.created_at,
            'updated_at': self.updated_at or '',
            'notes': self.notes or ''
        }
    
    @staticmethod
    def from_dict(data):
        return Application(
            tracking_id=data.get('tracking_id'),
            user_id=data.get('user_id'),
            user_name=data.get('user_name'),
            application_type=data.get('application_type'),
            description=data.get('description'),
            status=data.get('status', 'Pending'),
            document_path=data.get('document_path'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            notes=data.get('notes')
        )
    
    def __repr__(self):
        return f"<Application {self.tracking_id} - {self.status}>"