-- Ensure WAL retention & pitr policy (Supabase UI or support may be required for org-wide setting)
select pg_switch_wal();
