-- Sample: tokenize emails, store hash for lookup
alter table profiles add column if not exists email_hash text;
update profiles set email_hash = encode(digest(email, 'sha256'), 'hex') where email is not null;
create index if not exists idx_profiles_email_hash on profiles(email_hash);

-- retention example: events older than 400 days
create table if not exists events_archive (like events including all);
