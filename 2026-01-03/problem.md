# Daily Interview Data Analytics Question Challenge - 2026-01-03

## Question
You are a senior data analyst supporting the recruiting team. They want to deeply understand the efficiency of their hiring funnel. You've been provided with a table, `candidate_funnel`, which tracks candidates' ultimate outcomes for each stage of the interview process. Each row represents a unique candidate, and the status columns indicate whether they passed, were rejected, or never reached a particular stage.

Your task is to:
1.  Calculate the total number of candidates who *entered* each sequential interview stage.
2.  Determine the conversion rate between each consecutive stage (e.g., Application to Screening, Screening to Technical, etc.).
3.  Identify the stage with the highest drop-off percentage (which is `1 - conversion_rate`).

Assume the standard interview stages are strictly sequential: `Application` -> `Screening` -> `Technical` -> `Onsite` -> `Offer`. A candidate is considered to have "entered" a stage if they passed the previous one. For the `Application` stage, all candidates in the table are considered to have "entered" it. For the `Offer` stage, `offer_status` = 'Accepted' means they converted (were hired), otherwise they dropped off (offer rejected/declined).

Table Schema:
`candidate_funnel`
- `candidate_id` (INT): Unique identifier for each candidate.
- `application_status` (VARCHAR): 'Passed' or 'Rejected'.
- `screening_status` (VARCHAR): 'Passed', 'Rejected', or 'N/A' (if rejected before this stage).
- `technical_status` (VARCHAR): 'Passed', 'Rejected', or 'N/A'.
- `onsite_status` (VARCHAR): 'Passed', 'Rejected', or 'N/A'.
- `offer_status` (VARCHAR): 'Accepted', 'Rejected', or 'N/A'.

## Explanation
This solution calculates the funnel conversion rates and drop-off percentages between sequential interview stages.

1.  **`funnel_counts` CTE**: This Common Table Expression (CTE) is the core of the solution. It aggregates all necessary counts from the `candidate_funnel` table in a single pass.
    *   `total_applications`: Simply counts all unique candidates, representing those who 'entered' the Application stage.
    *   `passed_application`: Counts candidates who passed the Application stage, which implies they 'entered' the Screening stage. This is determined by `application_status = 'Passed'`.
    *   `passed_screening`: Counts candidates who passed both Application and Screening stages, implying they 'entered' the Technical stage.
    *   `passed_technical`: Counts candidates who passed Application, Screening, and Technical stages, implying they 'entered' the Onsite stage.
    *   `passed_onsite`: Counts candidates who passed Application, Screening, Technical, and Onsite stages, implying they 'entered' the Offer stage.
    *   `accepted_offer`: Counts candidates who ultimately accepted an offer, representing the final successful conversion (hired).

2.  **`UNION ALL` Structure**: The results from the `funnel_counts` CTE are then used to construct the final output table, with one row per stage. `UNION ALL` combines these separate queries.
    *   For each stage (`Application`, `Screening`, `Technical`, `Onsite`, `Offer`), a `SELECT` statement pulls the relevant `candidates_entered` (from the previous stage's 'passed' count), `candidates_passed_to_next_stage`, `conversion_rate`, and `drop_off_rate`.
    *   `conversion_rate` is calculated by dividing `candidates_passed_to_next_stage` by `candidates_entered`. `CAST(... AS DECIMAL)` ensures floating-point division for accurate rates. `ROUND(..., 4)` formats the rate to four decimal places.
    *   `drop_off_rate` is simply `1 - conversion_rate`.
    *   `CASE WHEN ... THEN ... ELSE 0 END` (or `ELSE 1 END` for drop-off) statements are used to handle potential division by zero (e.g., if no candidates reached a particular stage), ensuring the query doesn't error out.

3.  **Ordering**: The final `ORDER BY` clause ensures the stages are displayed in their logical sequential order (Application to Offer).

To identify the stage with the highest drop-off rate, one would examine the `drop_off_rate` column in the final result set and find the maximum value, then identify its corresponding `stage_name`.