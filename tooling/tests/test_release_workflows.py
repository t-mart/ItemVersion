"""Safety invariants for workflows that publish releases."""

from pathlib import Path

import yaml  # type: ignore[ty:unresolved-import]


ROOT = Path(__file__).parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"
RELEASE_CALLERS = ("merge-master.yml", "refresh-data.yml")


def load_workflow(name: str) -> dict:
    return yaml.load(
        (WORKFLOWS / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader
    )


def named_step(workflow: dict, job: str, name: str) -> dict:
    return next(
        step for step in workflow["jobs"][job]["steps"] if step.get("name") == name
    )


class TestReleaseSerialization:
    def test_every_caller_uses_the_shared_release_queue(self):
        for name in RELEASE_CALLERS:
            concurrency = load_workflow(name)["concurrency"]
            assert concurrency == {
                "group": "itemversion-release",
                "cancel-in-progress": "false",
                "queue": "max",
            }


class TestCandidateRef:
    def test_release_requires_an_exact_candidate(self):
        workflow = load_workflow("release.yml")

        candidate = workflow["on"]["workflow_call"]["inputs"]["candidate-ref"]
        branch = workflow["on"]["workflow_call"]["inputs"]["candidate-branch"]
        assert candidate["required"] == "true"
        assert branch["required"] == "true"
        assert workflow["jobs"]["check"]["with"]["ref"] == "${{ inputs.candidate-ref }}"
        assert named_step(workflow, "release", "Checkout code")["with"]["ref"] == (
            "${{ inputs.candidate-ref }}"
        )

    def test_a_promoted_candidate_cannot_be_released_again(self):
        workflow = load_workflow("release.yml")
        command = named_step(
            workflow, "release", "Refuse an already promoted candidate"
        )["run"]

        assert 'git tag --points-at "$candidate"' in command
        assert 'git tag --points-at "$release_tip"' in command
        assert 'git merge-base --is-ancestor "$candidate" "$release_tip"' in command
        assert "Reconcile its publishers instead of releasing again" in command

    def test_every_caller_passes_its_recorded_candidate(self):
        expected = {
            "merge-master.yml": (
                "${{ needs.merge.outputs.candidate-sha }}",
                "${{ needs.merge.outputs.candidate-branch }}",
            ),
            "refresh-data.yml": (
                "${{ needs.commit.outputs.candidate-sha }}",
                "${{ needs.commit.outputs.candidate-branch }}",
            ),
        }

        for name, (candidate, branch) in expected.items():
            release = load_workflow(name)["jobs"]["release"]
            assert release["with"]["candidate-ref"] == candidate
            assert release["with"]["candidate-branch"] == branch


class TestReleaseOrdering:
    def test_build_and_artifact_precede_permanent_release_state(self):
        workflow = load_workflow("release.yml")
        names = [step["name"] for step in workflow["jobs"]["release"]["steps"]]

        assert names.index("Build") < names.index("Upload build")
        assert names.index("Upload build") < names.index("Preflight publishing")
        assert names.index("Preflight publishing") < names.index("Prepare master reconciliation")
        assert names.index("Prepare master reconciliation") < names.index(
            "Push release refs atomically"
        )
        assert names.index("Push release refs atomically") < names.index("Publish full release")

    def test_callers_stage_without_advancing_release(self):
        commands = {
            "merge-master.yml": named_step(
                load_workflow("merge-master.yml"),
                "merge",
                "Merge master and stage candidate",
            )["run"],
            "refresh-data.yml": named_step(
                load_workflow("refresh-data.yml"), "commit", "Commit & Stage"
            )["run"],
        }

        for command in commands.values():
            assert 'HEAD:refs/heads/${{ env.candidate_ref }}' in command
            assert "git push origin release" not in command

    def test_git_checkpoint_updates_every_ref_atomically(self):
        workflow = load_workflow("release.yml")
        command = named_step(workflow, "release", "Push release refs atomically")["run"]

        assert "git push --atomic origin" in command
        assert "release:refs/heads/release" in command
        assert "master-reconcile:refs/heads/master" in command
        assert "refs/tags/" in command

    def test_publish_results_are_rendered_in_the_run_summary(self):
        workflow = load_workflow("release.yml")
        full = named_step(workflow, "release", "Publish full release")["run"]
        prerelease = named_step(workflow, "release", "Publish pre-release")["run"]
        summary = named_step(workflow, "release", "Summarize publication")

        assert '--result-file "$RUNNER_TEMP/publish-result.json"' in full
        assert '--result-file "$RUNNER_TEMP/publish-result.json"' in prerelease
        assert "always()" in summary["if"]
        assert "GITHUB_STEP_SUMMARY" in summary["run"]
        assert "GITHUB_OUTPUT" in summary["run"]
        assert workflow["jobs"]["release"]["outputs"] == {
            "curseforge-url": "${{ steps.publication.outputs.curseforge-url }}",
            "github-url": "${{ steps.publication.outputs.github-url }}",
        }


class TestRefreshRetry:
    def test_download_is_staged_and_an_unchanged_file_is_a_success(self):
        workflow = load_workflow("refresh-data.yml")
        download = named_step(
            workflow, "commit", "Download generated lua from item-version-scrape release"
        )["run"]
        commit = named_step(workflow, "commit", "Commit & Stage")["run"]

        assert "mktemp src/ItemVersion/.ItemData.lua." in download
        assert '--output "$downloaded"' in download
        assert 'mv "$downloaded" src/ItemVersion/ItemData.lua' in download
        assert "if git diff --cached --quiet" in commit
