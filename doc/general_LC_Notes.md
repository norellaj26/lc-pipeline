
| What needs to happen between issue and expiry    | Typical days |
|--------------------------------------------------|--------------|
| Beneficiary receives the LC                      | 1-3 days |
| Goods are produced/prepared for shipment         | varies (weeks-months) |
| Goods are shipped                                | 1-7 days |
| Shipping documents prepared (B/L, invoice, etc.) | 3-7 days |
| Documents presented to bank                      | within "presentation period" |
| Bank examines documents                          | 5 banking days max (UCP 600 Art. 14b) |

Where the 21 days comes from:
You're remembering the presentation period, not validity. UCP 600 Article 14(c) says:

"A presentation including one or more original transport documents...
must be made by or on behalf of the beneficiary not later than 21 calendar days after the date of shipment, 
but in any event not later than the expiry date of the credit."

Realistic minimum LC validity in real-world banking:

| Scenario                                      | Typical validity |
|-----------------------------------------------|------------------|
| Same-city, simple goods, urgent deal          | 30 days minimum |
| Standard international trade                  | 60-180 days |
| Complex/large shipments (machinery, projects) | 180-540 days |
| Standby LCs (financial guarantees)            | Often 1 year+ |

# Pipeline Improvements Backlog

## Validators
- [ ] DATE009: Detect zero-validity LCs (issue_date == expiry_date)
- [ ] DATE010: Configurable minimum validity (default 30 days)
- [ ] Investigate documents_required column — only 1 unique value (suspicious test data)

## Architecture
- [ ] Make MIN_VALIDITY configurable in validation_rules.py
- [ ] Add business rules section separate from technical rules
The principle: real engineers don't fix everything they notice immediately — they document and prioritize. 
- A backlog is a sign of maturity, not procrastination.
- When you finish your Python journey and come back to enhance the pipeline,
- you'll have a clear list waiting.


| Topic                       | Key fact |
|-----------------------------|----------|
| UCP 600                     | The "rulebook" governing letters of credit globally |
| Article 14(c)               | 21-day default presentation period after shipment |
| Article 14(b)               | Banks have 5 banking days max to examine documents |
| Validity periods            | No technical minimum, but 30+ days is real-world standard |
| Standby LCs                 | Often 1 year+ validity — financial guarantees, not trade |
| Business vs technical rules | Validity minimums are business rules, not code rules |