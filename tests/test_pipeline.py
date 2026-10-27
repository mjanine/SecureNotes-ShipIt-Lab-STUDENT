"""Week 17 — CI pipeline checks.

Part B is a YAML file, not Python, so these tests parse
.github/workflows/ci.yml and assert it does what a real pipeline must:
trigger on pushes and PRs, run on a clean machine, install the project,
and run the WHOLE test suite (security + accessibility + performance).

If your ci.yml is correct here, it will go green on GitHub too.

INSTRUCTOR note: all of these pass against the solved ci.yml.
"""
import yaml


def load(workflow_text):
    return yaml.safe_load(workflow_text)


def _trigger_section(wf):
    # YAML 1.1 (PyYAML) reads a bare `on:` key as the boolean True.
    # Accept either spelling so students aren't tripped up by the quirk.
    if "on" in wf:
        return wf["on"]
    if True in wf:
        return wf[True]
    return None


def _all_steps(wf):
    steps = []
    for job in (wf.get("jobs") or {}).values():
        for step in (job.get("steps") or []):
            steps.append(step)
    return steps


def _run_text(wf):
    return "\n".join(s.get("run", "") for s in _all_steps(wf))

def _uses_text(wf):
    return "\n".join(s.get("uses", "") for s in _all_steps(wf))


# --- it's valid YAML ------------------------------------------------------
def test_workflow_is_valid_yaml(workflow_text):
    wf = load(workflow_text)
    assert isinstance(wf, dict), "ci.yml should parse into a YAML mapping."


# --- triggers -------------------------------------------------------------
def test_triggers_on_push_and_pull_request(workflow_text):
    section = _trigger_section(load(workflow_text))
    assert section is not None, "The workflow needs an `on:` trigger section."
    text = str(section)
    assert "push" in text, "The workflow should trigger on push."
    assert "pull_request" in text, "The workflow should trigger on pull_request."


# --- a job on a clean machine ---------------------------------------------
def test_has_at_least_one_job(workflow_text):
    jobs = load(workflow_text).get("jobs") or {}
    assert len(jobs) >= 1, "Define at least one job (e.g. a `test` job)."


def test_a_job_runs_on_ubuntu(workflow_text):
    jobs = load(workflow_text).get("jobs") or {}
    runners = " ".join(str(j.get("runs-on", "")) for j in jobs.values())
    assert "ubuntu" in runners, "A job should run on an ubuntu runner."


# --- the steps do the real work -------------------------------------------
def test_checks_out_the_code(workflow_text):
    assert "actions/checkout" in _uses_text(load(workflow_text)), \
        "Add a step that uses actions/checkout to get the code."


def test_sets_up_python(workflow_text):
    assert "actions/setup-python" in _uses_text(load(workflow_text)), \
        "Add a step that uses actions/setup-python."


def test_installs_dependencies(workflow_text):
    run = _run_text(load(workflow_text))
    assert "pip install" in run and "requirements.txt" in run, \
        "A step should run: pip install -r requirements.txt"


def test_runs_the_whole_test_suite(workflow_text):
    run = _run_text(load(workflow_text))
    assert "pytest" in run, "A step should run pytest."
    # must not quietly narrow the run to skip the Week 16 checks
    narrowed = any(x in run for x in ["test_security.py", "test_api.py -q only",
                                      "-k security", "-k api"])
    assert not narrowed, \
        "Run the FULL suite (just `pytest`), not only the security/api tests."
