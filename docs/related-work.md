# Related work and novelty hypothesis

This is an initial map, not a systematic literature review. Search results and project status change; verify sources and dates before making a novelty claim.

| Work | Overlap | Possible distinction to investigate |
|---|---|---|
| [Spring Boot Migrator](https://github.com/spring-projects-experimental/spring-boot-migrator) | Automates Spring Boot migration recipes | SpringFleetBench evaluates candidate tools rather than applying one migration recipe |
| [Amazon MigrationBench](https://github.com/amazon-science/MigrationBench) | Repository-level Java upgrade benchmark | Investigate whether fleet-wide service interactions and API compatibility are evaluated |
| [ScarfBench](https://github.com/scarfbench/benchmark) | AI-driven enterprise Java framework migration benchmark | Investigate its task scope and whether multi-repository fleet outcomes are measured |
| [OpenRewrite](https://github.com/openrewrite/rewrite) | Automated source refactoring and migration recipes | A transformation engine is a baseline under test, not itself the proposed benchmark |

## Hypothesis

The pilot explores whether a benchmark that scores upgrades across a set of dependent Spring Boot services—using repository-level build/test results plus cross-service API compatibility and fleet-wide success—provides information that single-repository migration scores do not.

This is **not** a claim that no such benchmark exists. A stronger claim requires reviewing the cited systems, relevant papers, and additional public repositories, then publishing a transparent comparison table.
