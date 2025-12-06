ALTER TABLE evaluation."SupervisorReplacements"
ADD CONSTRAINT unique_replacement UNIQUE
(
    "AbsentSupervisorID",
    "StartDate",
    "EndDate"
);
