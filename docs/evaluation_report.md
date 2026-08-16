# Evaluation Report — Text-to-SQL system

**Date:** 2026-08-16
**Test set:** `backend/evaluation.py` (20 questions)
**Runner:** `backend/run_evaluation.py`
**Score: 7/20**

## How scoring works
- Clear questions: PASS iff the system did NOT ask for clarification
  AND the returned rows exactly match the golden query's rows.
- Ambiguous questions: PASS iff it asked for clarification AND picking
  an option resolved to an answer.

## Results by category

| # | Category | Question | Result | Why |
|---|---|---|---|---|
| 1 | count | customers registered | PASS | |
| 2 | count-filter | orders delivered | FAIL | judge over-asked |
| 3 | count-filter | orders cancelled | PASS | |
| 4 | filter | customers in Mumbai | PASS | |
| 5 | filter-sum | credit card total | FAIL | `None` — 'credit card' vs 'credit_card' |
| 6 | sum | total revenue | PASS | |
| 7 | avg | average order amount | FAIL | judge over-asked |
| 8 | group-by | amount per status | PASS | |
| 9 | group-by-date | revenue per month | FAIL | judge over-asked |
| 10 | top-1 | city with most customers | FAIL | right answer, wrong columns |
| 11 | sort-limit | 5 most recent orders | FAIL | rule "recent" over-flagged |
| 12 | sort-limit | top 5 by amount | FAIL | rule "top" over-flagged (known) |
| 13 | join | amounts + names | FAIL | row cap 100 vs 400 |
| 14 | date-window | new customers last month | FAIL | judge: "last month" ambiguous |
| 15 | date | customers signed up today | FAIL | judge over-asked |
| 16 | no-data | customers in Antarctica | FAIL | rate limit hit mid-run |
| 17 | clarify-rule | best customers | FAIL | asked but choice re-asked |
| 18 | clarify-rule | last month's best | PASS | |
| 19 | clarify-rule | most popular payment | PASS | |
| 20 | clarify-gemini | favourite customers | FAIL | asked but choice re-asked |

## Failure categories

1. **Judge over-conservatism** (#2, #7, #9, #14, #15):
   Gemini treats "average", "per month", "last month", "today" as
   ambiguous. Tune the judgment my capabilities or only trust rules.
2. **Rule-list over-flagging** (#11, #12): "recent", "top" fire even
   when the metric is specified. Known limitation.
3. **Real correctness bug** (#5): 'credit card' vs 'credit_card' —
   valid SQL, wrong answer. The self-correction loop cannot catch
   this (no error). Mitigation: include exact column VALUES in the
   schema description.
4. **Clarify loop can chain** (#17, #20): resolved questions containing
   "highest" get re-flagged. Need a max-clarify-rounds limit.
5. **Strictness artifacts** (#10, #13): answer was correct but column
   set differed / row cap truncated. Consider partial credit.
6. **Environment** (#16): free-tier rate limit exhausted mid-run.

## Next actions (T4.3)
- Add max 2 clarification rounds, then answer with a sensible default.
- Include sample column VALUES in the schema my capabilities.
- Consider dropping/loosening rules for "recent", "top" when a metric
  is specified.
