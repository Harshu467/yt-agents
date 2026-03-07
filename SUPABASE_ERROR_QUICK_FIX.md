# 🚀 Supabase Upload Error - Quick Fix

## Error: "Failed to upload video to Supabase storage"
## Also: "relation \"videos\" does not exist"

### ⚡ Quick Fixes (Try These First)

**1. Missing credentials?**
```bash
# Add to .env or terminal:
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='your_service_role_key'

# Test:
python3 scripts/validate_supabase.py
```

**2. Wrong key type?**
- ❌ Don't use "anon" key
- ✅ Use "service_role" key
- Go to: https://app.supabase.com → Settings → API

**3. Bucket doesn't exist?**
- Go to: Storage → Buckets
- Create new bucket named: `videos`
- Set to Public

**4. Videos table missing?** ⭐ NEW
```bash
# Check and create table:
python3 scripts/setup_supabase_table.py
```
This will show you the SQL to run in SQL Editor.

**5. Get credentials right now:**

```bash
# 1. Go to https://app.supabase.com
# 2. Click your project
# 3. Settings → API → Copy:
#    - "Project URL" → SUPABASE_URL
#    - "service_role" secret → SUPABASE_KEY
# 4. Set them:
export SUPABASE_URL='https://your-project.supabase.co'
export SUPABASE_KEY='eyJhbGciOiJIUzI1NiIsInR...'
# 5. Verify:
python3 scripts/validate_supabase.py
```

### 📖 Full Troubleshooting Guide

See [SUPABASE_TROUBLESHOOTING.md](SUPABASE_TROUBLESHOOTING.md) for detailed instructions.

### 🔍 Diagnostics

```bash
# Complete validation:
python3 scripts/validate_supabase.py

# Setup videos table:
python3 scripts/setup_supabase_table.py

# Check table status:
python3 scripts/setup_supabase_table.py --status

# View detailed setup help:
python3 scripts/validate_supabase.py --setup
```

### 🆘 Still Not Working?

1. ✅ Run validation script → check all ✓
2. ✅ Run setup table script → follow instructions
3. ✅ Read full troubleshooting guide
4. ✅ Switch to Firebase (FIREBASE_SETUP.md)
5. ✅ Use local storage for development

---

**Most common issues:**
1. Missing credentials → Run validation script
2. Videos table missing → Run setup table script
3. Wrong key type → Check Settings → API

Try these in order, usually fixed in <5 minutes!

