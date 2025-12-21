"""
Quick test script to verify login functionality
Run this to check if your account exists and credentials match
"""
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_CSV = os.path.join(BASE_DIR, "data", "users.csv")

def test_login(email, password):
    """Test if login credentials work."""
    print(f"\nTesting login for: {email}")
    print(f"   Password entered: '{password}'")
    print(f"   Password length: {len(password)}")
    
    if not os.path.exists(USERS_CSV):
        print("ERROR: users.csv not found!")
        return False
    
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_email = row.get('email', '').strip()
            user_password = row.get('password_hash', '').strip()
            user_name = row.get('name', '').strip()
            user_role = row.get('role', '').strip()
            
            # Check email match (case-insensitive)
            if user_email.lower() == email.lower():
                print(f"\n[FOUND] User: {user_name}")
                print(f"   Email in CSV: '{user_email}'")
                print(f"   Password in CSV: '{user_password}'")
                print(f"   Password length in CSV: {len(user_password)}")
                print(f"   Role: {user_role}")
                
                # Check password match
                if user_password == password:
                    print(f"\n[SUCCESS] PASSWORD MATCHES! Login should work!")
                    return True
                else:
                    print(f"\n[ERROR] Password mismatch!")
                    print(f"   Expected: '{user_password}'")
                    print(f"   Got:      '{password}'")
                    print(f"   Are they the same? {user_password == password}")
                    if user_password != password:
                        print(f"   Character by character comparison:")
                        max_len = max(len(user_password), len(password))
                        for i in range(max_len):
                            c1 = user_password[i] if i < len(user_password) else 'N/A'
                            c2 = password[i] if i < len(password) else 'N/A'
                            if c1 != c2:
                                print(f"     Position {i}: CSV='{c1}' (ord={ord(c1) if c1 != 'N/A' else 0}) vs Input='{c2}' (ord={ord(c2) if c2 != 'N/A' else 0})")
                    return False
    
    print(f"\n[ERROR] User with email '{email}' not found in CSV!")
    return False

def list_all_users():
    """List all users in the CSV."""
    print("\nAll users in users.csv:")
    print("-" * 80)
    
    if not os.path.exists(USERS_CSV):
        print("❌ users.csv not found!")
        return
    
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            print(f"{i}. {row.get('name', 'N/A')}")
            print(f"   Email: {row.get('email', 'N/A')}")
            print(f"   Password: {row.get('password_hash', 'N/A')}")
            print(f"   Role: {row.get('role', 'N/A')}")
            print()

if __name__ == '__main__':
    print("=" * 80)
    print("LOGIN TEST SCRIPT")
    print("=" * 80)
    
    # List all users
    list_all_users()
    
    # Test specific accounts
    print("\n" + "=" * 80)
    print("TESTING SPECIFIC ACCOUNTS")
    print("=" * 80)
    
    # Test admin
    test_login('admin@system.com', 'admin123')
    
    # Test delivery
    test_login('agent@system.com', 'agent123')
    
    # Test a citizen account
    test_login('o@gmail.com', '123456')
    
    print("\n" + "=" * 80)
    print("To test your account, run:")
    print("  python test_login.py")
    print("Or modify this script to test your email/password")
    print("=" * 80)
