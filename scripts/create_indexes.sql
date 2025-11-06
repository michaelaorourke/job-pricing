-- Create indexes separately after tables are created
-- Run this after create_database.sql

\c hranalyticsdb;

-- Indexes for benchmarks table
CREATE INDEX IF NOT EXISTS idx_benchmarks_lookup ON compensation.benchmarks (job_family, level, zone);
CREATE INDEX IF NOT EXISTS idx_benchmarks_location ON compensation.benchmarks (geography, zone);
CREATE INDEX IF NOT EXISTS idx_benchmarks_source ON compensation.benchmarks (source_type, data_date);

-- Indexes for salary_ranges table
CREATE INDEX IF NOT EXISTS idx_salary_ranges_job ON compensation.salary_ranges (job_family, level, zone);
CREATE INDEX IF NOT EXISTS idx_salary_ranges_created ON compensation.salary_ranges (created_at DESC);

-- Indexes for job_analyses table
-- CREATE INDEX IF NOT EXISTS idx_job_analyses_embedding ON compensation.job_analyses USING ivfflat (embedding vector_cosine_ops); -- Uncomment after pgvector
CREATE INDEX IF NOT EXISTS idx_job_analyses_family_level ON compensation.job_analyses (job_family, detected_level);
CREATE INDEX IF NOT EXISTS idx_job_analyses_created ON compensation.job_analyses (created_at DESC);

-- Indexes for conversations table
CREATE INDEX IF NOT EXISTS idx_conversations_session ON compensation.conversations (session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user ON compensation.conversations (user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON compensation.conversations (updated_at DESC);

-- Indexes for openai_cache table
CREATE INDEX IF NOT EXISTS idx_openai_cache_hash ON compensation.openai_cache (prompt_hash);
CREATE INDEX IF NOT EXISTS idx_openai_cache_expire ON compensation.openai_cache (expires_at);

-- Indexes for audit_logs table
CREATE INDEX IF NOT EXISTS idx_audit_user_time ON compensation.audit_logs (user_id, created_at DESC);

-- Indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON compensation.users (email);