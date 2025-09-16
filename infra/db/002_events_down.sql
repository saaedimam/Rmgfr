-- Down migration for 002_events.sql (drop in reverse order)
do $$ begin drop table if exists cases cascade; exception when others then null; end $$;
do $$ begin drop table if exists decisions cascade; exception when others then null; end $$;
do $$ begin drop table if exists events cascade; exception when others then null; end $$;
do $$ begin drop table if exists api_keys cascade; exception when others then null; end $$;
do $$ begin drop table if exists projects cascade; exception when others then null; end $$;
do $$ begin drop table if exists orgs cascade; exception when others then null; end $$;
do $$ begin drop type if exists case_status cascade; exception when others then null; end $$;
do $$ begin drop type if exists decision_outcome cascade; exception when others then null; end $$;
do $$ begin drop type if exists event_type cascade; exception when others then null; end $$;
do $$ begin drop function if exists current_jwt_project_id() cascade; exception when others then null; end $$;
