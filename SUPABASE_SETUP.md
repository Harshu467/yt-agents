**Supabase / Postgres setup for `videos` table**

This project stores video metadata in a `videos` table. Use the SQL in `supabase_videos_table.sql`.

Quick steps:

1. Open your Supabase project -> Database -> SQL Editor.
2. Paste and run the contents of `supabase_videos_table.sql`.
3. Create a storage bucket (e.g., `videos`) in Supabase Storage and set its policy (public or private).
4. For server-side inserts use the service role key (`SUPABASE_KEY`) and the REST API or PostgREST endpoints.

Example minimal RLS policy for authenticated inserts (optional):

1) Enable RLS on `videos` (if you want row-level control):
   - ALTER TABLE public.videos ENABLE ROW LEVEL SECURITY;

2) Allow inserts for authenticated users (adjust as needed):
   - CREATE POLICY "insert_videos_authenticated" ON public.videos
     FOR INSERT USING (auth.role() = 'authenticated');

Notes:
- If you call Supabase REST from server code, prefer using the service role key (keep it secret).
- The code in `utils/supabase_storage.py` expects a `videos` table and a storage bucket named `videos` by default.
