-- CREATE USER "evalApp" WITH PASSWORD 'app1234';
-- GRANT USAGE ON SCHEMA evaluation TO "evalApp";
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA evaluation TO "evalApp";
-- GRANT UPDATE(id) ON ALL TABLES IN SCHEMA evaluation TO "evalApp";
-- ALTER DEFAULT PRIVILEGES IN SCHEMA evaluation GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO "evalApp";
-- ALTER DEFAULT PRIVILEGES IN SCHEMA your_schema GRANT UPDATE(id) ON TABLES TO "evalApp";

-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA evaluation TO "evalApp";
-- CREATE TABLE evaluation."SupervisorReplacements" (
-- 	"ID" SERIAL PRIMARY KEY,
-- 	"AbsentSupervisor" TEXT NOT NULL,
-- 	"AbsentSupervisorID" TEXT NOT NULL,
-- 	"ReplacementSupervisor" TEXT NOT NULL,
-- 	"ReplacementSupervisorID" TEXT NOT NULL,
-- 	"StartDate" DATE NOT NULL,
-- 	"EndDate" DATE NOT NULL
-- )

-- GRANT USAGE, SELECT ON SEQUENCE evaluation."EvaluationTable_EvaluationID_seq" TO "evalApp";
-- GRANT UPDATE ON SEQUENCE evaluation."EvaluationTable_EvaluationID_seq" TO "evalApp";

GRANT USAGE, SELECT ON SEQUENCE evaluation."SupervisorReplacements_ID_seq" TO "evalApp";
GRANT UPDATE ON SEQUENCE evaluation."SupervisorReplacements_ID_seq" TO "evalApp";

-- SELECT * FROM information_schema.tables 
-- WHERE table_schema = 'evaluation' AND table_name = 'CaseAssignment';

-- Check If the sequence exists
-- SELECT * FROM information_schema.sequences 
-- WHERE sequence_schema = 'evaluation' AND sequence_name = 'SupervisorReplacements_ID_seq';

-- SELECT column_name, column_default
-- FROM information_schema.columns
-- WHERE table_schema = 'evaluation' AND table_name = 'CaseAssignment';

