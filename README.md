# SpringFleetBench

**A pilot benchmark for evaluating automated Spring Boot upgrades across a fleet of services.**

SpringFleetBench gives migration tools the same set of service repositories and checks whether each result meets declared build, test, and compatibility requirements. The first suite is intentionally small and synthetic; it is a prototype for the evaluation format, not evidence that any migration strategy is superior.

## Why a fleet benchmark?

An upgrade can compile in one service and still fail across a service fleet because services use different Java levels, build tools, API contracts, and dependency combinations. SpringFleetBench is designed to evaluate the complete fleet run, including per-service outcomes and all-services success.

The **research hypothesis** is that fleet-level upgrade success and cross-service compatibility are under-measured compared with single-repository migration success. This needs a literature and repository review before it can be described as a novel contribution. Existing Java migration benchmarks and Spring migration tools are related work; see [docs/related-work.md](docs/related-work.md).

## Current status

- Pilot suite: two small, synthetic Maven service fixtures; current checks cover declared edits and do not yet build the Java projects.
- Runner: copies each fixture to a temporary workspace, invokes a candidate command, checks expected migration properties, and writes JSON results.
- Checks: file content assertions and optional build/test commands.
- No model API, third-party Python runtime package, or credentials required by the runner.
- **Not yet a validated public benchmark:** real repository fixtures, pinned tool versions, dependency matrices, API compatibility checks, and independent runs are future work.

## Run

Requirements: Python 3.10 or newer.

```bash
PYTHONPATH=src python -m springfleetbench inspect suites/pilot/suite.json
```

Run the included mechanical baseline against both services:

```bash
PYTHONPATH=src python -m springfleetbench run \
  --suite suites/pilot/suite.json \
  --candidate "python $PWD/scripts/pilot_candidate.py" \
  --output results/pilot.json
```

This script only applies the exact edits required by the synthetic pilot checks. It is a smoke-test baseline, not a real migration product or a competitive result.

Run a candidate migration command for each service. The runner sets `SFB_REPO_DIR` to the copied service repository and runs the command with that directory as its working directory:

```bash
PYTHONPATH=src python -m springfleetbench run \
  --suite suites/pilot/suite.json \
  --candidate 'your-migration-command' \
  --output results/my-run.json
```

Use only candidate commands you trust: the runner executes them as local subprocesses. The pilot has no network isolation or container sandbox. Build/test commands in the suite can also download dependencies.

The result includes each task's command exit status, validation checks, elapsed time, and a fleet summary. Compare tools only with the same suite revision, environment, and limits. Do not compare a run against checks tuned after seeing its output.

## Develop

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Roadmap

1. Validate the novelty hypothesis against migration benchmarks, tools, and papers.
2. Add pinned, license-reviewed public repositories with reproducible before/after snapshots.
3. Add API compatibility checks and runtime smoke tests across dependent services.
4. Report per-service and all-services success, repair effort, build time, and regressions.
5. Publish a protocol and invite independent baseline submissions before presenting a leaderboard.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions should include the fixture provenance and license, exact tool/version, command, environment, and expected checks.

## License

MIT. See [LICENSE](LICENSE).
