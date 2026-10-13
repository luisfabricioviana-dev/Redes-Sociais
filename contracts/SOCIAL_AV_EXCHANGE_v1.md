# Social ↔ Audiovisual ↔ Learning exchange v1

Status: **CANDIDATE / CONTRACT TESTED**, not live runtime integrated.

`create_exchange(candidate)` wraps `SOCIAL_MEDIA_BRIEF_v1`, preserves canonical identity and originating channel.
`receive_av_result(exchange, package)` rejects changed content, mismatched channel, missing QA evidence identifiers, absent approval or failed claimed quality.
`ingest_tutorial(observation)` records learning only as CANDIDATE.

All transports are ordinary dictionaries (JSON serializable). No provider calls, publishing or editor mutation.
Evidence IDs are review pointers, not independent confirmation that a render meets a quality criterion.
The real Audiovisual agent must accept the brief, return render evidence tied to the same hash and provide audit artifacts.
Repository `agente-youtube` currently has no discovered existing contract under these precise identifiers; this is a proposed bridge, not a deployed adapter.

Regression: `python -m unittest discover -s tests -p 'test_*.py' -v`.
