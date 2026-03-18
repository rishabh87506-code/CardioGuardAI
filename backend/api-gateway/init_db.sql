-- Create Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone_e164 VARCHAR(20),
    tenant_id UUID DEFAULT '00000000-0000-0000-0000-000000000000',
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Wellness Metrics Table
CREATE TABLE IF NOT EXISTS wellness_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value NUMERIC NOT NULL,
    source VARCHAR(100),
    quality_score NUMERIC,
    metadata JSONB DEFAULT '{}',
    measurement_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Index for performance
CREATE INDEX IF NOT EXISTS idx_wellness_metrics_user_type ON wellness_metrics(user_id, metric_type);
CREATE INDEX IF NOT EXISTS idx_wellness_metrics_timestamp ON wellness_metrics(measurement_timestamp DESC);
