-- Rollback script for Anti-Fraud Platform Database Schema
-- Use with caution - this will remove all data and schema

-- Drop triggers first
DROP TRIGGER IF EXISTS profiles_audit_trigger ON profiles;
DROP TRIGGER IF EXISTS items_audit_trigger ON items;
DROP TRIGGER IF EXISTS fraud_rules_audit_trigger ON fraud_rules;

-- Drop functions
DROP FUNCTION IF EXISTS audit_trigger_function();
DROP FUNCTION IF EXISTS set_current_user(TEXT);
DROP FUNCTION IF EXISTS get_current_user_profile();

-- Drop tables (in reverse dependency order)
DROP TABLE IF EXISTS audit_logs CASCADE;
DROP TABLE IF EXISTS fraud_rules CASCADE;
DROP TABLE IF EXISTS fraud_events CASCADE;
DROP TABLE IF EXISTS items CASCADE;
DROP TABLE IF EXISTS profiles CASCADE;

-- Drop extensions (optional - only if not used elsewhere)
-- DROP EXTENSION IF EXISTS "uuid-ossp";
-- DROP EXTENSION IF EXISTS "pgcrypto";
