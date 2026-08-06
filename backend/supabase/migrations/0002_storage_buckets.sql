-- Private storage buckets. No public read policies are created: the backend
-- accesses these exclusively with the service-role key and hands out
-- short-lived signed URLs to the frontend on demand.

insert into storage.buckets (id, name, public)
values ('chat-uploads', 'chat-uploads', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('run-outputs', 'run-outputs', false)
on conflict (id) do nothing;
