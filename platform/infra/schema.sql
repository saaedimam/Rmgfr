-- Anti-Fraud Platform Database Schema
-- PostgreSQL with Row Level Security (RLS)

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create profiles table (linked to Clerk users)
CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT,
    last_name TEXT,
    avatar_url TEXT,
    role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin', 'super_admin')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create items table (example entity for CRUD operations)
CREATE TABLE items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL CHECK (length(title) >= 1 AND length(title) <= 255),
    description TEXT CHECK (length(description) <= 1000),
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    owner_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create fraud events table
CREATE TABLE fraud_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type TEXT NOT NULL,
    user_id UUID REFERENCES profiles(id) ON DELETE SET NULL,
    session_id TEXT,
    ip_address INET,
    user_agent TEXT,
    device_fingerprint TEXT,
    risk_score DECIMAL(3,2) CHECK (risk_score >= 0 AND risk_score <= 1),
    decision TEXT NOT NULL CHECK (decision IN ('allow', 'block', 'challenge')),
    reason TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create fraud rules table
CREATE TABLE fraud_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    rule_type TEXT NOT NULL CHECK (rule_type IN ('rate_limit', 'velocity', 'device', 'behavioral', 'geolocation')),
    conditions JSONB NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('allow', 'block', 'challenge', 'flag')),
    priority INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT true,
    created_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create audit log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name TEXT NOT NULL,
    record_id UUID NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by UUID REFERENCES profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_profiles_clerk_user_id ON profiles(clerk_user_id);
CREATE INDEX idx_profiles_email ON profiles(email);
CREATE INDEX idx_items_owner_id ON items(owner_id);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_created_at ON items(created_at);
CREATE INDEX idx_fraud_events_user_id ON fraud_events(user_id);
CREATE INDEX idx_fraud_events_created_at ON fraud_events(created_at);
CREATE INDEX idx_fraud_events_decision ON fraud_events(decision);
CREATE INDEX idx_fraud_events_ip_address ON fraud_events(ip_address);
CREATE INDEX idx_fraud_rules_rule_type ON fraud_rules(rule_type);
CREATE INDEX idx_fraud_rules_is_active ON fraud_rules(is_active);
CREATE INDEX idx_audit_logs_table_record ON audit_logs(table_name, record_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE fraud_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE fraud_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for profiles table
CREATE POLICY "Users can view own profile" ON profiles
    FOR SELECT USING (clerk_user_id = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update own profile" ON profiles
    FOR UPDATE USING (clerk_user_id = current_setting('app.current_user_id', true));

CREATE POLICY "Admins can view all profiles" ON profiles
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true) 
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS Policies for items table
CREATE POLICY "Users can view own items" ON items
    FOR SELECT USING (
        owner_id IN (
            SELECT id FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can insert own items" ON items
    FOR INSERT WITH CHECK (
        owner_id IN (
            SELECT id FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can update own items" ON items
    FOR UPDATE USING (
        owner_id IN (
            SELECT id FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can delete own items" ON items
    FOR DELETE USING (
        owner_id IN (
            SELECT id FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true)
        )
    );

-- RLS Policies for fraud_events table
CREATE POLICY "Users can view own fraud events" ON fraud_events
    FOR SELECT USING (
        user_id IN (
            SELECT id FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "System can insert fraud events" ON fraud_events
    FOR INSERT WITH CHECK (true);

-- RLS Policies for fraud_rules table
CREATE POLICY "Admins can manage fraud rules" ON fraud_rules
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true) 
            AND role IN ('admin', 'super_admin')
        )
    );

-- RLS Policies for audit_logs table
CREATE POLICY "Admins can view audit logs" ON audit_logs
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM profiles 
            WHERE clerk_user_id = current_setting('app.current_user_id', true) 
            AND role IN ('admin', 'super_admin')
        )
    );

-- Create functions for audit logging
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, TG_OP, row_to_json(OLD), 
                (SELECT id FROM profiles WHERE clerk_user_id = current_setting('app.current_user_id', true)));
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (table_name, record_id, action, old_values, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(OLD), row_to_json(NEW),
                (SELECT id FROM profiles WHERE clerk_user_id = current_setting('app.current_user_id', true)));
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (table_name, record_id, action, new_values, changed_by)
        VALUES (TG_TABLE_NAME, NEW.id, TG_OP, row_to_json(NEW),
                (SELECT id FROM profiles WHERE clerk_user_id = current_setting('app.current_user_id', true)));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit triggers
CREATE TRIGGER profiles_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON profiles
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER items_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON items
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER fraud_rules_audit_trigger
    AFTER INSERT OR UPDATE OR DELETE ON fraud_rules
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Create function to set current user context
CREATE OR REPLACE FUNCTION set_current_user(user_id TEXT)
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_user_id', user_id, true);
END;
$$ LANGUAGE plpgsql;

-- Create function to get current user profile
CREATE OR REPLACE FUNCTION get_current_user_profile()
RETURNS profiles AS $$
DECLARE
    user_profile profiles;
BEGIN
    SELECT * INTO user_profile
    FROM profiles
    WHERE clerk_user_id = current_setting('app.current_user_id', true);
    
    RETURN user_profile;
END;
$$ LANGUAGE plpgsql;

-- Insert default admin user (replace with actual Clerk user ID)
INSERT INTO profiles (clerk_user_id, email, first_name, last_name, role)
VALUES ('admin_user_id', 'admin@antifraudplatform.com', 'Admin', 'User', 'super_admin')
ON CONFLICT (clerk_user_id) DO NOTHING;

-- Insert sample fraud rules
INSERT INTO fraud_rules (name, description, rule_type, conditions, action, priority) VALUES
('High Velocity Login', 'Block users with more than 5 login attempts per minute', 'velocity', 
 '{"max_attempts": 5, "time_window": 60, "event_type": "login"}', 'block', 10),
('Suspicious IP', 'Flag requests from known suspicious IP addresses', 'geolocation',
 '{"blocked_ips": ["192.168.1.100", "10.0.0.50"]}', 'flag', 20),
('Device Fingerprint Mismatch', 'Challenge users with device fingerprint changes', 'device',
 '{"check_fingerprint": true, "tolerance": 0.8}', 'challenge', 30)
ON CONFLICT (name) DO NOTHING;
