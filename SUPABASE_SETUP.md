# Supabase Integration Setup Guide

## 📋 Quick Start (5 minutes)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click **"New Project"**
3. Fill in:
   - **Organization**: Create new or select existing
   - **Project name**: `securemedi`
   - **Database password**: Create a strong password
   - **Region**: Select closest to your location
4. Click **"Create new project"** and wait for initialization (2-3 minutes)

### Step 2: Get API Credentials

Once project is ready:

1. Go to **Settings** → **API** in left sidebar
2. You'll see:
   - **Project URL** (Supabase URL)
   - **anon public** key (API Key)
3. Copy both values

### Step 3: Create Environment Variables

Add to your `.env` file in the project root:

```bash
# Supabase Configuration
ENABLE_SUPABASE=true
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=your_anon_public_key_here
```

**Example:**
```bash
ENABLE_SUPABASE=true
SUPABASE_URL=https://xyz123abc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 4: Create Database Tables

In Supabase Dashboard:

1. Go to **SQL Editor** in left sidebar
2. Click **"New Query"**
3. Copy and paste the SQL below
4. Click **"Run"**

#### SQL Setup Script

```sql
-- Create Doctors Table
CREATE TABLE doctors (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  wallet_address TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  email TEXT,
  specialization TEXT,
  hospital TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
  registered_on TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create Patients Table
CREATE TABLE patients (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  patient_id TEXT UNIQUE NOT NULL,
  wallet_address TEXT,
  name TEXT,
  email TEXT,
  date_of_birth DATE,
  emergency_contact TEXT,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
  registered_on TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better search performance
CREATE INDEX doctors_wallet_idx ON doctors(wallet_address);
CREATE INDEX doctors_name_idx ON doctors(name);
CREATE INDEX doctors_specialization_idx ON doctors(specialization);

CREATE INDEX patients_patient_id_idx ON patients(patient_id);
CREATE INDEX patients_wallet_idx ON patients(wallet_address);
CREATE INDEX patients_name_idx ON patients(name);
CREATE INDEX patients_email_idx ON patients(email);

-- Create Emergency Access Sessions Table
CREATE TABLE emergency_access_sessions (
  id UUID PRIMARY KEY,
  session_id UUID,
  doctor_address TEXT NOT NULL,
  patient_id TEXT NOT NULL,
  reason TEXT,
  severity TEXT,
  expected_duration_min INTEGER,
  status TEXT NOT NULL,
  requested_at TIMESTAMP WITH TIME ZONE,
  activated_at TIMESTAMP WITH TIME ZONE,
  expires_at TIMESTAMP WITH TIME ZONE,
  closed_at TIMESTAMP WITH TIME ZONE,
  closure_note TEXT,
  outcome TEXT,
  activation_note TEXT,
  blockchain_tx_hash TEXT,
  created_ip TEXT,
  updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX emergency_sessions_patient_idx ON emergency_access_sessions(patient_id);
CREATE INDEX emergency_sessions_doctor_idx ON emergency_access_sessions(doctor_address);
CREATE INDEX emergency_sessions_status_idx ON emergency_access_sessions(status);
CREATE INDEX emergency_sessions_requested_idx ON emergency_access_sessions(requested_at DESC);

-- Create persistent Audit Logs Table
CREATE TABLE audit_logs (
  id BIGSERIAL PRIMARY KEY,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  actor_address TEXT,
  actor_role TEXT,
  action TEXT NOT NULL,
  resource_id TEXT,
  resource_type TEXT,
  result TEXT NOT NULL,
  details JSONB DEFAULT '{}'::jsonb,
  ip_address TEXT,
  error_message TEXT
);

CREATE INDEX audit_logs_timestamp_idx ON audit_logs(timestamp DESC);
CREATE INDEX audit_logs_resource_id_idx ON audit_logs(resource_id);
CREATE INDEX audit_logs_actor_address_idx ON audit_logs(actor_address);
CREATE INDEX audit_logs_action_idx ON audit_logs(action);

-- Enable Row Level Security (RLS) - Optional but recommended
ALTER TABLE doctors ENABLE ROW LEVEL SECURITY;
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE emergency_access_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies (Optional - for added security)
-- Allow anonymous reads (for now, can be restricted later)
CREATE POLICY "Enable read access for all users" ON doctors
  FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON patients
  FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON emergency_access_sessions
  FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON audit_logs
  FOR SELECT USING (true);

CREATE POLICY "Enable insert access for all users" ON emergency_access_sessions
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update access for all users" ON emergency_access_sessions
  FOR UPDATE USING (true);

CREATE POLICY "Enable insert access for all users" ON audit_logs
  FOR INSERT WITH CHECK (true);
```

### Step 5: Install Dependencies

```bash
cd SecureMedi
pip install -r backend/requirements.txt
```

This will install `supabase==2.4.2`

### Step 6: Test Connection

```bash
# Run the verification script
python verify_system.py
```

You should see:
```
✓ Supabase service initialized
✓ Doctors table accessible
✓ Patients table accessible
```

---

## 📊 Using the Suite

### Backend Endpoints

All endpoints protected with `@require_role("ADMIN")`

#### Doctors

```bash
# List doctors (paginated)
GET /api/admin/registry/doctors?limit=100&offset=0

# Search doctors
GET /api/admin/registry/doctors/search?q=cardiology

# Add doctor
POST /api/admin/registry/doctors
{
  "wallet_address": "0x...",
  "name": "Dr. Smith",
  "email": "smith@hospital.com",
  "specialization": "Cardiology",
  "hospital": "City Medical"
}

# Update doctor
PUT /api/admin/registry/doctors/{doctor_id}
{
  "specialization": "Cardiology & Surgery",
  "status": "inactive"
}

# Delete doctor
DELETE /api/admin/registry/doctors/{doctor_id}

# Export as CSV
GET /api/admin/registry/doctors/export/csv
```

#### Patients

```bash
# List patients (paginated)
GET /api/admin/registry/patients?limit=100&offset=0

# Search patients
GET /api/admin/registry/patients/search?q=P001

# Add patient
POST /api/admin/registry/patients
{
  "patient_id": "P001",
  "wallet_address": "0x...",
  "name": "John Doe",
  "email": "john@email.com",
  "date_of_birth": "1990-01-15",
  "emergency_contact": "Jane Doe (+1234567890)"
}

# Update patient
PUT /api/admin/registry/patients/{patient_id}
{
  "email": "newemail@email.com",
  "status": "active"
}

# Delete patient
DELETE /api/admin/registry/patients/{patient_id}

# Export as CSV
GET /api/admin/registry/patients/export/csv
```

### Frontend Admin Dashboard

Access at: **http://localhost:3000/admin**

Features:
- 📋 List all doctors/patients
- 🔍 Search by any field
- ➕ Add new doctor/patient
- ✏️ Edit existing records
- 🗑️ Delete records
- 📥 Export to CSV
- 🔐 Admin-only access (requires ADMIN role)

---

## 🔒 Security

### Row-Level Security (Optional)

For production, enable RLS policies:

```sql
-- Only admins can insert/update/delete
CREATE POLICY "Admins can manage doctors" ON doctors
  FOR ALL USING (auth.jwt() ->> 'role' = 'admin')
  WITH CHECK (auth.jwt() ->> 'role' = 'admin');
```

### API Security

All admin endpoints:
- Require `Authorization: Bearer <JWT_TOKEN>` header
- Require `ADMIN` role
- Log all changes to audit table
- Validate all inputs
- Sanitize data

---

## 🐛 Troubleshooting

### "Supabase service not available"

**Error:**
```
Supabase service not available. Check SUPABASE_URL and SUPABASE_KEY in environment.
```

**Solution:**
1. Check `.env` file has correct values
2. Restart backend server
3. Verify credentials in Supabase dashboard

### "Connection refused"

**Error:**
```
Failed to connect to Supabase
```

**Solution:**
1. Verify SUPABASE_URL is correct (check typos)
2. Check internet connection
3. Verify API key hasn't been revoked
4. Check Supabase project is active

### Tables don't exist

**Error:**
```
relation "doctors" does not exist
```

**Solution:**
1. Run the SQL setup script again
2. Check you ran it in the correct Supabase project
3. Verify table names match exactly (case-sensitive)

### Permission denied

**Error:**
```
permission denied for schema public
```

**Solution:**
1. Ensure you're using correct database credentials
2. Check RLS policies are set correctly
3. Verify user has appropriate role

---

## 🚀 Migrate Existing Data

If you have existing JSON data:

```python
from registry.registry_manager import RegistryManager
from app.services.supabase_service import SupabaseService

registry = RegistryManager()
supabase = SupabaseService(SUPABASE_URL, SUPABASE_KEY)

# Migrate doctors
for doctor in registry.get_all_doctors():
    supabase.add_doctor(
        wallet_address=doctor['wallet_address'],
        name=doctor['name'],
        specialization=doctor.get('specialization'),
        hospital=doctor.get('hospital')
    )

# Migrate patients
for patient in registry.get_all_patients():
    supabase.add_patient(
        patient_id=patient['id'],
        wallet_address=patient.get('wallet_address'),
        name=patient.get('name'),
        email=patient.get('email')
    )
```

---

## 📱 Environment Variables Summary

| Variable | Required | Example |
|----------|----------|---------|
| `ENABLE_SUPABASE` | Yes | `true` |
| `SUPABASE_URL` | Yes | `https://xyz.supabase.co` |
| `SUPABASE_KEY` | Yes | `eyJ...` |

---

## 🎯 What's Included

✅ Supabase service layer (`backend/app/services/supabase_service.py`)
✅ Admin API routes (`backend/app/api/admin_routes.py`)
✅ Admin dashboard UI (`frontend/pages/admin.tsx`)
✅ Full CRUD operations
✅ Search and filtering
✅ CSV export
✅ Pagination
✅ Audit logging integration
✅ Role-based access control

---

## 📖 Next Steps

1. ✅ Set up Supabase project
2. ✅ Configure environment variables
3. ✅ Create database tables
4. ✅ Install Python dependencies
5. ✅ Restart backend server
6. ✅ Access admin dashboard at `/admin`
7. 📊 Migrate existing data (optional)
8. 🔒 Configure RLS policies (optional)

---

## 💡 Tips

- **Backup JSON files** before migrating to Supabase
- **Test in development** before production
- **Monitor audit logs** for all admin changes
- **Use strong API keys** and rotate them regularly
- **Enable RLS** for production environments
- **Set up automated backups** in Supabase settings

---

## 🆘 Support

- Supabase Docs: https://supabase.com/docs
- GitHub Issues: Check project issues for known problems
- Logs: Check `logs/` directory for detailed error logs

---

**Setup Time:** ~10 minutes
**Difficulty:** Easy
**Security Level:** High (with RLS enabled)
