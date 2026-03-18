-- Database Setup for CardioGuard AI
-- Run this using: psql -U postgres -f setup_db.sql

-- Create Database
-- CREATE DATABASE cardioguard;
-- \c cardioguard;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_e164 VARCHAR(20) UNIQUE,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255),
    date_of_birth DATE,
    gender VARCHAR(20),
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    consent_wellness_tracking BOOLEAN DEFAULT FALSE,
    consent_family_sharing BOOLEAN DEFAULT FALSE,
    consent_asha_contact BOOLEAN DEFAULT FALSE
);

-- 2. Wellness Metrics Table (Metadata)
CREATE TABLE IF NOT EXISTS wellness_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL, -- 'heart_rate', 'blood_pressure', etc.
    source VARCHAR(50) NOT NULL, -- 'ppg_wearable', 'rppg_camera', 'user_input'
    measurement_timestamp TIMESTAMPTZ NOT NULL,
    quality_score NUMERIC(3, 2), -- 0.00 to 1.00
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Family Contacts Table
CREATE TABLE IF NOT EXISTS family_contacts (
    contact_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    contact_name VARCHAR(255) NOT NULL,
    relationship VARCHAR(50),
    phone_e164 VARCHAR(20) NOT NULL,
    whatsapp_enabled BOOLEAN DEFAULT FALSE,
    notification_level VARCHAR(20) DEFAULT 'important',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, phone_e164)
);

-- 4. ASHA Workers Table
CREATE TABLE IF NOT EXISTS asha_workers (
    asha_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name VARCHAR(255) NOT NULL,
    phone_e164 VARCHAR(20) UNIQUE NOT NULL,
    coverage_areas TEXT[],
    languages TEXT[] DEFAULT ARRAY['hi', 'en'],
    experience_years INTEGER,
    certification_level VARCHAR(50),
    average_response_time_seconds INTEGER,
    user_satisfaction_rating NUMERIC(3, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Healthcare Facilities Table
CREATE TABLE IF NOT EXISTS healthcare_facilities (
    facility_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    facility_name VARCHAR(255) NOT NULL,
    facility_type VARCHAR(50) NOT NULL, -- 'tertiary', 'secondary', 'primary'
    address TEXT NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    latitude NUMERIC(10, 8),
    longitude NUMERIC(11, 8),
    phone_number VARCHAR(20),
    services TEXT[],
    payment_options TEXT[],
    languages_spoken TEXT[],
    operating_hours JSONB,
    google_place_id VARCHAR(255),
    user_rating NUMERIC(3, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
