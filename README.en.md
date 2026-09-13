# Visio Academic Diagrams

**Evidence-linked paper understanding and manual Microsoft Visio research-diagram workflows.**

Version 0.2.0. Chinese-first instructions. [Full Chinese README](README.md) · [Skill](SKILL.md) · [Examples](examples/README.md) · [Validation](VALIDATION.md).

## Workflow

Read the supplied source and declare coverage. Build a paper model with stable content IDs, relations and evidence locators. Select a figure purpose and typed semantic graph. Resolve the required Visio capabilities and version. Specify nominal geometry and manual construction steps. Review the actual figure and conditional publication requirements.

A paper can have multiple views: a reading mind map, an executable algorithm flowchart, a concept/evidence map or a proof-dependency graph. The same content IDs link those views without conflating their edge semantics.

## Scope

The registry contains 26 feature families and 220 capabilities/topics: 54 with document-backed operation routes and 166 lookup-only entries. All GUI-test flags are false. There are 57 source records with explicit reading depth and inherited/new review labels. These numbers are not exhaustive counts of Visio features or proof of paper-comprehension accuracy.

Declared support is explicit, inferred, proposed or unknown. Source-explicit hypotheses remain hypotheses. The validators check structure and declared provenance, not whether evidence actually entails a statement, a theorem is correct, or a causal interpretation is justified.

## Use

Keep the entire `visio-academic-diagrams` directory. For supported local Codex environments place it in `.agents/skills/` within a project or `$HOME/.agents/skills/`. Invoke `$visio-academic-diagrams`. An ordinary file-reading chat can instead read the extracted package on request. Neither method implies permanent memory or installation as an account-wide plugin.[A01][A02]

Example request: “Read my paper, declare source coverage, create an evidence-linked content model, then design a reading mind map and a separate method flowchart. Preserve uncertainty. Give precise Visio instructions with object IDs, menu paths, dimensions, expected results and checks.”

## Test and publish

Python 3.10+, standard library only:

```bash
python scripts/validate_package.py
python -m unittest discover -s tests -v
python scripts/lookup_capability.py "ShapeSheet"
python scripts/publish_github.py --owner YOUR_GITHUB_LOGIN
```

Publishing is a dry run by default. `--public --execute` explicitly creates a new repository through your locally authenticated GitHub CLI. The script uses an isolated allowlisted staging directory; it never overwrites an existing repository. See [publishing](docs/GITHUB-PUBLISH.md).

74 local unit tests and four model/plan/layout bundles pass. This is not a real-paper benchmark or a Visio rendering test. No live GitHub upload has been tested for this release. Original content is [MIT-licensed](LICENSE); external sources retain their own rights. [Source register](references/source-register.md).
