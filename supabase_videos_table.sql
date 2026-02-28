-- Supabase / Postgres table for storing video metadata
-- Run this in Supabase SQL editor or any Postgres client connected to your DB

CREATE TABLE IF NOT EXISTS public.videos (
  id text PRIMARY KEY,
  filename text,
  filepath text,
  topic text,
  duration real,
  created_at timestamptz DEFAULT now(),
  status text,
  file_size integer,
  playable boolean,
  url text,
  youtube_id text
);

CREATE INDEX IF NOT EXISTS idx_videos_created_at ON public.videos (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_videos_youtube_id ON public.videos (youtube_id);
CREATE INDEX IF NOT EXISTS idx_videos_topic ON public.videos (topic);
