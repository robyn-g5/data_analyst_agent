-- Initial schema for the team analytics chat app.
-- RLS is enabled with NO policies on every table: the frontend never queries
-- Postgres directly for app data, only through the FastAPI backend using the
-- service-role key (which bypasses RLS). This is a deliberate default-deny
-- posture appropriate for a single shared-team workspace.

create extension if not exists pgcrypto;

create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  display_name text,
  created_at timestamptz not null default now()
);

create table if not exists allowed_emails (
  id uuid primary key default gen_random_uuid(),
  email text not null unique,
  invited_by uuid references auth.users(id),
  created_at timestamptz not null default now()
);

create table if not exists runs (
  id uuid primary key default gen_random_uuid(),
  status text not null default 'pending'
    check (status in ('pending','awaiting_clarification','validating',
                       'mapping_columns','analyzing','generating_narrative',
                       'building_dashboard','complete','failed')),
  step text,
  run_date date not null default current_date,
  created_by uuid references auth.users(id),
  config jsonb,
  error_message text,
  validation_report_path text,
  analysis_results_path text,
  report_md_path text,
  dashboard_html_path text,
  config_path text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz
);

create table if not exists chat_messages (
  id uuid primary key default gen_random_uuid(),
  author_id uuid references auth.users(id),
  role text not null check (role in ('user','assistant','system')),
  content text not null default '',
  run_id uuid references runs(id),
  created_at timestamptz not null default now()
);

create table if not exists chat_attachments (
  id uuid primary key default gen_random_uuid(),
  message_id uuid not null references chat_messages(id) on delete cascade,
  run_id uuid references runs(id),
  original_filename text not null,
  storage_path text not null,
  role_guess text check (role_guess in ('paid_media','growth_funnel','product_usage','unknown')),
  size_bytes bigint,
  created_at timestamptz not null default now()
);

create index if not exists chat_messages_created_at_idx on chat_messages (created_at);
create index if not exists chat_attachments_run_id_idx on chat_attachments (run_id);
create index if not exists runs_run_date_created_at_idx on runs (run_date desc, created_at desc);

alter table profiles enable row level security;
alter table allowed_emails enable row level security;
alter table runs enable row level security;
alter table chat_messages enable row level security;
alter table chat_attachments enable row level security;

-- Keep profiles populated automatically on signup.
create or replace function handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
  insert into public.profiles (id, email)
  values (new.id, new.email)
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure handle_new_user();
