# Daily Interview Data Analytics Question Challenge - 2026-01-06

## Question
You are a Senior Data Analyst tasked with optimizing the recruitment funnel. You have access to a table `application_stages` which logs the progression of each application through various interview stages.

Your goal is to identify the top 3 interview stages that have the highest rejection rates. A 'rejection rate' for a stage is defined as the percentage of applications that reached that stage and were subsequently marked with a `status` of 'Rejected' *at that specific stage*, out of all applications that completed that stage (i.e., have a non-'Pending' status for that stage).

**Table Schema:**

`application_stages`
- `application_id` VARCHAR (Primary Key, uniquely identifies an application for a specific job opening)
- `candidate_id` VARCHAR (Identifies the candidate)
- `stage_name` VARCHAR (e.g., 'Phone Screen', 'Technical Interview 1', 'Hiring Manager Interview', 'Onsite Loop', 'Offer')
- `status` VARCHAR (Indicates the final outcome for the application at that stage, e.g., 'Passed', 'Rejected', 'Pending', 'Withdrew', 'Hired')
- `start_date` DATE
- `end_date` DATE

Write a SQL query to return the `stage_name`, the total number of applications rejected at that stage, the total number of applications that completed that stage, and the calculated rejection percentage, ordered by rejection percentage in descending order, for the top 3 stages.

## Explanation
The solution first defines a Common Table Expression (CTE) called `StageOutcomes`. This CTE calculates two key metrics for each `stage_name`:
1.  `rejected_at_stage_count`: This counts the number of applications whose `status` for that specific stage was 'Rejected'. A `SUM(CASE WHEN ... THEN 1 ELSE 0 END)` is used for this conditional counting.
2.  `total_applications_completed_stage`: This counts the total number of *unique* applications that reached and completed that stage with any final outcome (i.e., not 'Pending'). The `WHERE status IN ('Passed', 'Rejected', 'Withdrew', 'Hired')` clause ensures we only consider applications that have a definitive outcome for the stage, and `COUNT(DISTINCT application_id)` is used to ensure each application is counted once per stage.

After computing these counts for all stages, the main query selects these metrics along with the calculated `rejection_percentage`. The percentage is calculated by dividing `rejected_at_stage_count` by `total_applications_completed_stage`, casting one of the operands to `DECIMAL` to ensure floating-point division, and multiplying by 100.0. A `WHERE` clause filters out stages with zero completed applications to prevent division by zero errors. Finally, the results are ordered by `rejection_percentage` in descending order, and `LIMIT 3` is applied to get the top 3 stages.