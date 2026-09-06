# opencode-job-hunt

OpenWork skills that run a local job search end to end without inventing facts
or hiding partial results.

The repository provides seven skills:

- `job-setup` configures the workspace, profile, search criteria, and boards.
- `job-scan` searches enabled boards and maintains a deduplicated ledger.
- `cover-letter` evaluates an advert and writes a tailored resume and letter.
- `interview-prep` creates interview briefs and records debriefs.
- `interview-rehearsal` runs a realistic practice interview.
- `job-report` reports applications, interviews, and declarations.
- `board-request` records a board for which no adapter exists yet.

All Python code uses the standard library and supports Python 3.9 or newer.
Your profile, configuration, ledger, and applications remain ordinary files in
a separate job-hunt workspace.

## Requirements

- [OpenWork](https://github.com/different-ai/openwork)
- Python 3.9 or newer
- A CV or profile from which the skills can establish factual career history

Optional document tooling:

- `pandoc` and `xelatex` for PDFs
- Noto Sans for the supplied PDF templates
- `pdftotext` and `pdfinfo` from Poppler for reading and checking PDFs
- ImageMagick and Pillow for an optional signature image

OpenWork supplies the browser tools used by browser-only boards. Sign in to job
boards yourself in OpenWork's browser. The skills never ask for or enter your
login credentials and never submit an application without confirmation.

## Install into OpenWork

Clone the repository somewhere that will not move:

```bash
git clone https://github.com/antomicblitz/opencode-job-hunt.git ~/repos/opencode-job-hunt
cd ~/repos/opencode-job-hunt
python3 bin/openwork-setup.py install --workspace ~/OpenWork
```

The installer creates one loader:

```text
~/OpenWork/.opencode/plugins/job-hunt.js
```

It does not edit `~/OpenWork/opencode.jsonc` or global OpenCode configuration.
The loader points to this checkout, so do not delete or move the repository
while it is installed.

Quit and restart OpenWork after installation. Then run:

```text
/job-setup
```

To target another local OpenWork workspace, pass its root to `--workspace`.

## Status

```bash
python3 bin/openwork-setup.py status --workspace ~/OpenWork
```

Status verifies the loader, adapter, and skills directory. If the checkout was
moved, run `install` from its new location to refresh the loader.

## Update

```bash
cd ~/repos/opencode-job-hunt
git pull --ff-only
python3 bin/openwork-setup.py status --workspace ~/OpenWork
```

Restart OpenWork after updating skills or plugin code.

## Uninstall

Uninstall before deleting the checkout:

```bash
cd ~/repos/opencode-job-hunt
python3 bin/openwork-setup.py uninstall --workspace ~/OpenWork
```

The command removes only the loader owned by this installer. It does not remove
job-search data and refuses to delete an unrelated file. Quit and restart
OpenWork once more.

## First run

`/job-setup` asks where job-search data should live, then builds the candidate
profile and configuration. Every requested input must include the URL or command
that produces it, and rejected input must include the reason and correction.

By default, data lives at:

```text
~/Documents/job_applications/
├── config.yml
├── candidate.md
├── commute.md
├── repos.md
├── profile/
├── job-pipeline.md
└── YYYYMMDD_Company-Role/
    ├── job-ad.md
    ├── resume.md
    └── cover-letter.md
```

Set `JOB_HUNT_HOME` in the environment used to launch OpenWork to choose a
stable alternative location:

```bash
export JOB_HUNT_HOME="$HOME/work/job-search"
```

The OpenWork adapter sets `JOB_HUNT_ROOT` automatically. That variable points
to this code checkout; `JOB_HUNT_HOME` points to personal job-search data. They
are deliberately different.

## Browser behavior

Most board adapters use plain HTTP and do not need a browser. For boards that
do, the skills use OpenWork's native browser tools and your existing browser
session. They do not bypass access controls or anti-bot challenges.

The canonical access policy is [`shared/robots-policy.md`](shared/robots-policy.md).
Board-specific behavior is documented under [`shared/boards/`](shared/boards/).

## Privacy

The plugin does not upload your profile or applications. Network requests go to
the job boards being searched and to services explicitly configured for that
board. A `board-request` may create a GitHub issue only after showing the exact
content and receiving confirmation.

Never commit your job-hunt data. It may contain addresses, phone numbers,
employment history, and application records.

## Diagnostics

Run the diagnostic only when something appears unavailable:

```bash
bin/doctor.sh
```

It reports optional document tools and the resolved data workspace. Browser
availability must be tested inside OpenWork; ask it to open a harmless public
page and describe the result.

## Development

Run the test suite:

```bash
python3 -m unittest discover -s tests -v
```

Byte-compile Python sources:

```bash
python3 -m compileall -q bin skills tests
```

The adapter contract is intentionally small: expose the skills, register
`/job-setup`, and set `JOB_HUNT_ROOT`. Installation is workspace-local and has
one generated artifact. Keep those boundaries when contributing.

New board adapters must follow
[`shared/boards/README.md`](shared/boards/README.md). Never guess a DOM, hide a
partial result, or include real personal data in a test fixture.

## License

MIT — see [LICENSE](LICENSE).
