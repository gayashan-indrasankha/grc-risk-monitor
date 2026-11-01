# Stage 6 acceptance checklist

## Source-control hygiene
- [ ] My existing Git history and working source files remain intact.
- [ ] I reviewed the new docs before merging them into `README.md`.
- [ ] No secrets, tokens, mailbox addresses, account names or unredacted screenshots were committed.
- [ ] I checked repository `.gitignore` for SQLite databases, caches and local credentials.

## README and evidence
- [ ] README opens with concise description, synthetic-data notice, and key results.
- [ ] Mermaid architecture diagram renders in GitHub.
- [ ] Four rule descriptions match the actual SQL source.
- [ ] GitHub screenshot paths resolve to redacted images uploaded to the repository.
- [ ] I documented manual syncing between Python/CSV and Excel Online.
- [ ] Dashboard screenshot clearly shows baseline counts, charts and data warning.
- [ ] Flow screenshot is redacted and shows order of filter, email and update actions.
- [ ] 28/28 test results, synthetic fixture metrics, and limitations are accurately described.
- [ ] Repo instructions work on a fresh clone with Python 3.11 (the recorded local run used 3.11.9).

## Interview readiness
- [ ] I can explain R01-R04 without reading source code.
- [ ] I can explain DAX card values and fact/dimension relationships.
- [ ] I can explain why zero email on repeat run is **not** a general exactly-once guarantee.
- [ ] I can show a 3–5 minute demo without exposing personal details.
- [ ] CV bullet points name only technology and work I actually used.

## Optional polish
- [ ] Activate and confirm the GitHub Actions workflow on my own repository (if permitted).
- [ ] Update GitHub repo description/topics and pin it to my profile.
- [ ] Upload a short redacted demo recording or link to a public video.
