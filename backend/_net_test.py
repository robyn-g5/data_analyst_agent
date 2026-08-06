import time

import httpx

t0 = time.time()
print("starting", flush=True)
r = httpx.get(
    "https://pbtdaeuiiufodvzwcvix.supabase.co/rest/v1/runs?select=id&limit=1",
    headers={
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBidGRhZXVpaXVmb2R2endjdml4Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4NjAzNDUxMywiZXhwIjoyMTAxNjEwNTEzfQ.3tK4G-kxS_C_KIzmysW8rpQfjaQeOvXTV7WpJbI9RA0"
    },
    timeout=8,
)
print("done", r.status_code, r.text, time.time() - t0, flush=True)
