BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 609abfc5a291

CREATE TYPE feedbacksource AS ENUM ('email', 'slack', 'app', 'other');

CREATE TABLE feedback (
    id UUID NOT NULL, 
    text VARCHAR(5000) NOT NULL, 
    source feedbacksource NOT NULL, 
    customer_email VARCHAR, 
    category VARCHAR(50) DEFAULT 'uncategorized' NOT NULL, 
    priority VARCHAR(50) DEFAULT 'medium' NOT NULL, 
    reviewed BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id)
);

CREATE INDEX ix_feedback_category ON feedback (category);

CREATE INDEX ix_feedback_created_at ON feedback (created_at);

CREATE INDEX ix_feedback_reviewed ON feedback (reviewed);

CREATE INDEX ix_feedback_source ON feedback (source);

INSERT INTO alembic_version (version_num) VALUES ('609abfc5a291') RETURNING alembic_version.version_num;

COMMIT;

