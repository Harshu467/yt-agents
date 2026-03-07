# Schema Migrations Error - FIXED ✅

## Error Message
```
relation "supabase_migrations.schema_migrations" does not exist
```

## What This Means

This error occurs when Supabase tries to access its internal migration tracking table but can't find it. Usually this means:

- **Videos table doesn't exist** - Most common cause
- Database schema hasn't been initialized
- Permission issues preventing table access

## Root Cause

The `videos` metadata table needs to be created in your Supabase database. When code tries to insert or query records, Supabase's REST API checks for the table, and if it doesn't exist, you get this error.

---

## Quick Fix (30 seconds)

### Step 1: Check Your Setup
```bash
python3 scripts/setup_supabase_table.py
```

### Step 2: Create the Table

The script will show you the SQL. Follow these steps:

1. Go to https://app.supabase.com
2. Select your project
3. Click "SQL Editor" (left sidebar)
4. Click "New query"
5. Paste the SQL below:

```sql
CREATE TABLE IF NOT EXISTS public.videos (
  id text PRIMARY KEY,
  filename text,
  filepath text,
  topic text,
  duration real,
  file_size integer,
  created_at timestamptz DEFAULT now(),
  status text DEFAULT 'pending',
  playable boolean DEFAULT FALSE,
  url text,
  youtube_id text
);

CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_topic ON public.videos (topic);
CREATE INDEX IF NOT EXISTS idx_videos_youtube_id ON public.videos (youtube_id);
```

6. Click "Run" (or Cmd+Enter)
7. You should see: **Success. No rows returned** or similar

### Step 3: Verify
```bash
python3 scripts/setup_supabase_table.py --status

# Should show: ✓ Videos table EXISTS and is ready to use!
```

### Step 4: Try Again
```bash
python3 create_video_example.py
# or use the web dashboard
```

---

## Files Updated

### 📝 Scripts (New/Improved)
- `scripts/validate_supabase.py` - Now detects missing table
- `scripts/setup_supabase_table.py` - **NEW** - Helper script to create table

### 🔧 Code Improvements
- `utils/supabase_storage.py`:
  - Better error messages for table-not-found errors
  - `validate_configuration()` method improved
  - New `create_videos_table()` method for future automation

### 📚 Documentation
- `SUPABASE_TROUBLESHOOTING.md` - Updated with table creation steps
- `SUPABASE_ERROR_QUICK_FIX.md` - Added table creation option
- `README.md` - Links to troubleshooting guides

---

## New Tools Available

### 1. Validate Configuration
```bash
python3 scripts/validate_supabase.py
```
- Checks credentials
- Checks bucket exists
- Checks if videos table exists
- Shows specific errors

### 2. Setup Videos Table
```bash
python3 scripts/setup_supabase_table.py
```
- Shows SQL to create table
- Guides you through setup
- Can check status

### 3. Check Table Status
```bash
python3 scripts/setup_supabase_table.py --status
```
- Shows if table exists
- Shows if ready to use

---

## Error Messages Now Show

When this error happens, you'll see more helpful output:

**Before:**
```
❌ relation "supabase_migrations.schema_migrations" does not exist
```

**After:**
```
❌ Videos table doesn't exist in Supabase
   Resolution: Run create_supabase_table() first
   Or go to SQL Editor and create the table manually

📋 SQL to run:
   CREATE TABLE IF NOT EXISTS public.videos (
     ...
   )
```

---

## Prevention

After initial setup, this error shouldn't happen again. But if you need to:

1. **Check if table exists:**
   ```bash
   python3 scripts/setup_supabase_table.py --status
   ```

2. **Recreate if deleted:**
   ```bash
   # Run SQL from setup_supabase_table.py output
   ```

3. **Migrate from another database:**
   - Follow guides in MIGRATION.md

---

## Common Sequence

1. Create new Supabase project
2. Try to create video → ERROR
3. Run `python3 scripts/setup_supabase_table.py`
4. Script shows SQL
5. Paste SQL in Supabase SQL Editor
6. Run → Success
7. Try video again → Works! ✅

---

## Next Steps

1. Run the setup script:
   ```bash
   python3 scripts/setup_supabase_table.py
   ```

2. Follow the instructions it shows

3. Create the table in SQL Editor

4. Verify with:
   ```bash
   python3 scripts/setup_supabase_table.py --status
   ```

5. Try your workflow again

---

## Need More Help?

- Full guide: [SUPABASE_TROUBLESHOOTING.md](SUPABASE_TROUBLESHOOTING.md)
- Quick fixes: [SUPABASE_ERROR_QUICK_FIX.md](SUPABASE_ERROR_QUICK_FIX.md)
- Validation tool: Run `python3 scripts/validate_supabase.py`

You've got this! 🚀
