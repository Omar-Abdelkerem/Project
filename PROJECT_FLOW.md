# 🆔 My ID System - Complete Flow

## ✅ CORRECTED FLOW (Based on SRS)

### **System Purpose:**
National ID Card issuance system (NOT bank cards)

---

## 🔄 Complete User Flow

### **1. Citizen Flow:**

#### **Step 1: Register**
- Citizen goes to `/register`
- Enters: Name, National ID (14 digits), Email, Phone, Password
- Account created with role: `CITIZEN`

#### **Step 2: Login**
- Citizen logs in with email/password
- Redirected to `/citizen/dashboard`

#### **Step 3: Apply for National ID Card**
- Citizen clicks "Apply for New ID Card"
- Fills form:
  - **Application Type:** 
    - New ID Card
    - ID Card Replacement
    - ID Card Renewal
    - ID Card Update
  - **Additional Information:** Description
  - **Required Documents:** Upload PDF/JPG/PNG (max 5MB)
- System generates **Tracking ID** (e.g., TRK-ABC12345)
- Application saved with status: **Pending**
- Notification created: "Application submitted successfully"

#### **Step 4: View Applications**
- Citizen sees all their applications in dashboard
- Shows: Tracking ID, Type, Status, Submitted Date
- Can click "View Details" to see full information

#### **Step 5: Track Application**
- Citizen can track by Tracking ID
- Shows: Current status, status history/timeline
- Real-time updates

---

### **2. Admin Flow:**

#### **Step 1: Login**
- Admin logs in: `admin@system.com` / `admin123`
- Redirected to `/admin`

#### **Step 2: Review Applications**
- Admin sees all applications
- Can filter: All, Pending, In Process
- For **Pending** applications, sees Approve/Reject buttons

#### **Step 3: Approve Application**
- Admin clicks "Approve"
- System:
  1. Updates request status: **Pending → Approved**
  2. **Automatically creates Delivery record**
  3. Assigns delivery to a delivery agent
  4. Creates notification for citizen: "Application approved! Delivery arranged."
  5. Logs audit action

#### **Step 4: Reject Application**
- Admin clicks "Reject"
- System:
  1. Updates request status: **Pending → Rejected**
  2. Creates notification for citizen: "Application rejected"
  3. Logs audit action

---

### **3. Delivery Agent Flow:**

#### **Step 1: Login**
- Delivery agent logs in: `agent@system.com` / `agent123`
- Redirected to `/delivery`

#### **Step 2: View Assigned Deliveries**
- Agent sees all deliveries assigned to them
- Shows: Delivery ID, Request ID, Status

#### **Step 3: Update Delivery Status**

**Status Flow:**
```
Pending → Out for Delivery → Delivered (or Failed)
```

**Actions:**
- **If Pending:** Click "Out for Delivery"
  - Status: Pending → Out for Delivery
  - Timestamp saved: `OutForDeliveryAt`
  - Notification: "Your ID card is out for delivery"

- **If Out for Delivery:** Click "Delivered" or "Failed"
  - **Delivered:**
    - Status: Out for Delivery → Delivered
    - Timestamp saved: `DeliveredAt`
    - Request status syncs: → Completed
    - Notification: "Your National ID card has been delivered!"
  
  - **Failed:**
    - Status: Out for Delivery → Failed
    - Timestamp saved: `FailedAt`
    - Request status syncs: → Failed
    - Notification: "Delivery failed. Contact support."

- **If Delivered/Failed:** No buttons (final status, cannot change)

---

## 📊 Status Flow Diagram

```
Citizen Submits Application
         ↓
    [Pending]
         ↓
    Admin Reviews
         ↓
    ┌─────┴─────┐
    │           │
[Approved]  [Rejected]
    │
    ↓
Delivery Created
    │
[Pending] (Delivery)
    │
    ↓
[Out for Delivery]
    │
    ├───────────┐
    │           │
[Delivered] [Failed]
    │           │
[Completed] [Failed]
```

---

## 🎯 Key Points

1. **Application Types** (for National ID):
   - New ID Card
   - ID Card Replacement
   - ID Card Renewal
   - ID Card Update

2. **Statuses:**
   - **Request Status:** Pending, Approved, Rejected, In Process, Completed, Failed
   - **Delivery Status:** Pending, Out for Delivery, Delivered, Failed

3. **Tracking ID:**
   - Generated automatically when citizen submits
   - Format: `TRK-XXXXXXXX`
   - Used for tracking application

4. **Notifications:**
   - Created automatically on status changes
   - Visible in citizen dashboard
   - Types: success, error, info

5. **Audit Logs:**
   - All admin actions logged
   - All delivery status updates logged
   - Includes: timestamp, actor, action, details

---

## ✅ What's Fixed

- ✅ Removed all "bank card" references
- ✅ Changed application types to National ID card types
- ✅ Updated all text to focus on National ID only
- ✅ Made flow clear: Apply → Approve → Deliver
- ✅ Fixed terminology throughout

---

**The system now correctly represents a National ID card issuance system!** 🆔
