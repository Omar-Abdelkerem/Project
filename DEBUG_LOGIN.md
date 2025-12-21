# 🔍 Login Debugging Guide

## Common Login Issues & Solutions

### Issue 1: "Invalid email or password" but credentials are correct

**Possible Causes:**
1. **Password mismatch** - Password stored differently than entered
2. **Email case sensitivity** - Email stored with different case
3. **Whitespace issues** - Extra spaces in email/password
4. **CSV encoding issues** - Special characters not read correctly

**Solution:**
- Check the exact email and password in `data/users.csv`
- Make sure there are no extra spaces
- Try copying email/password directly from CSV

### Issue 2: Account exists but can't login

**Check:**
1. Open `data/users.csv` in a text editor
2. Find your account row
3. Verify:
   - Email matches exactly (case doesn't matter)
   - Password matches exactly (case-sensitive!)
   - No extra spaces

### Issue 3: Session not persisting

**Solution:**
- Clear browser cookies
- Restart Flask
- Check Flask secret key is set

---

## 🔧 Quick Test

### Test with existing account:
1. **Admin:** `admin@system.com` / `admin123`
2. **Delivery:** `agent@system.com` / `agent123`
3. **Citizen:** Use any account from `users.csv`

### Check your account in CSV:
```python
# Run this to see all users
import csv
with open('data/users.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"Email: {row['email']} | Password: {row['password_hash']} | Role: {row['role']}")
```

---

## 🐛 Debug Steps

1. **Check CSV file:**
   - Open `data/users.csv`
   - Find your account
   - Copy exact email and password

2. **Try login with exact credentials:**
   - Use exact email from CSV
   - Use exact password from CSV (watch for spaces!)

3. **Check Flask console:**
   - Look for error messages
   - Check if CSV is being read

4. **Clear session:**
   - Logout if logged in
   - Clear browser cookies
   - Try again

---

## ✅ Fixed in Latest Code

- ✅ Email comparison is now case-insensitive
- ✅ Better error messages
- ✅ Session persistence improved
- ✅ CSV reading with proper encoding

---

## 🆘 If Still Not Working

1. **Check your account exists:**
   ```bash
   # View users.csv
   cat data/users.csv
   ```

2. **Try resetting password:**
   - Manually edit `data/users.csv`
   - Set password to something simple like "test123"
   - Try logging in

3. **Create new account:**
   - Register again with different email
   - Try logging in immediately

4. **Check Flask logs:**
   - Look for any error messages
   - Check if CSV path is correct
