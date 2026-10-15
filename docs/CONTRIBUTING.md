# Contributing

Pull requests and experiments are welcome. This project is exploratory and iterates quickly.

## Ways to Contribute

- Bug fixes and reliability improvements
- API contract cleanup and documentation
- Worker and queue stability improvements
- Testing coverage for auth, jobs, and state transitions
- UX improvements in the client aligned with current API contracts

## Contribution Workflow

1. Open an issue or draft PR describing the problem and intended change.
2. Keep changes scoped and focused to one concern when possible.
3. Update documentation when behavior or contracts change.
   The runtime flow and its contracts belong in [Project Overview](PROJECT_OVERVIEW.md), the canonical implementation reference; link to it instead of duplicating flow descriptions elsewhere.
4. Validate locally (API + worker + key endpoint flow) before opening PR.
5. Include clear notes about any breaking changes for the client.

## Standards

- Favor explicit, readable code over clever abstractions.
- Preserve backward compatibility when practical; if breaking, document it clearly.
- Include meaningful logs and error handling for operational visibility.
- Add or update tests for changed behavior when test tooling is available.

Queue-ordering regressions use actual RQ and an isolated Redis instance at port `16379`, database `15`. With that disposable service running, set `ORDERING_TEST_REDIS_URL=redis://127.0.0.1:16379/15` and run `python -m unittest discover -s tests -v`. These tests clear that database between cases, make no model calls, and check reversed reply completion, concurrent submissions, independent users, predecessor failures, transactional enqueue failure and reply-result expiry. Without the variable, the Redis integration cases are skipped; unit tests still run. CI provides the isolated service.
