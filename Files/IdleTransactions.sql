-- Detecting Database Transaction
-- SELECT pid, state, wait_event_type, wait_event, query
-- FROM pg_stat_activity
-- WHERE datname = 'GRS';

-- Show all idle transaction
-- SELECT pid, state, query
-- FROM pg_stat_activity
-- WHERE state = 'idle in transaction';

----Terminate idle transactions
-- SELECT pg_terminate_backend(pid)
-- FROM pg_stat_activity
-- WHERE state = 'idle in transaction';
