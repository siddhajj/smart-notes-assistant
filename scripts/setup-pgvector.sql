-- Enable pgvector extension for vector similarity search
-- This script should be run on your PostgreSQL database to enable vector operations

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create indexes for better performance on vector columns
-- These will be created automatically when tables are created, but can be added manually

-- Notes table vector indexes (will be created when running migrations)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS notes_title_embedding_idx ON notes USING ivfflat (title_embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS notes_body_embedding_idx ON notes USING ivfflat (body_embedding vector_cosine_ops) WITH (lists = 100);
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS notes_combined_embedding_idx ON notes USING ivfflat (combined_embedding vector_cosine_ops) WITH (lists = 100);

-- Tasks table vector indexes (will be created when running migrations)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS tasks_description_embedding_idx ON tasks USING ivfflat (description_embedding vector_cosine_ops) WITH (lists = 100);

-- Verify the extension is installed
SELECT * FROM pg_extension WHERE extname = 'vector';

-- Show available vector operators
\do *.*vector*