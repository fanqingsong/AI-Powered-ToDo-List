-- 创建记忆存储相关的表

-- 短期记忆表（会话级别的记忆）
CREATE TABLE IF NOT EXISTS short_term_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    message_type VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 长期记忆表（跨会话的记忆）
CREATE TABLE IF NOT EXISTS long_term_memory (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    memory_type VARCHAR(50) NOT NULL, -- 'fact', 'preference', 'context', 'knowledge'
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    importance_score INTEGER DEFAULT 1, -- 1-10, 重要性评分
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 任务上下文记忆表
CREATE TABLE IF NOT EXISTS task_context_memory (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    task_id INTEGER,
    context_type VARCHAR(50) NOT NULL, -- 'creation', 'update', 'deletion', 'query'
    context_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_short_term_memory_session_id ON short_term_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_short_term_memory_user_id ON short_term_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_short_term_memory_created_at ON short_term_memory(created_at);

CREATE INDEX IF NOT EXISTS idx_long_term_memory_user_id ON long_term_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_long_term_memory_key ON long_term_memory(key);
CREATE INDEX IF NOT EXISTS idx_long_term_memory_type ON long_term_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_long_term_memory_importance ON long_term_memory(importance_score DESC);

CREATE INDEX IF NOT EXISTS idx_task_context_memory_session_id ON task_context_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_task_context_memory_task_id ON task_context_memory(task_id);

-- 创建更新时间触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为相关表添加更新时间触发器
CREATE TRIGGER update_short_term_memory_updated_at 
    BEFORE UPDATE ON short_term_memory 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_long_term_memory_updated_at 
    BEFORE UPDATE ON long_term_memory 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
