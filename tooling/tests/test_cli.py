"""Tests for the ./dev command line itself."""

from __future__ import annotations

from pathlib import Path

import pytest  # type: ignore[ty:unresolved-import]

import cli
import install


class TestCli:
    def test_no_command_prints_help(self, capsys):
        assert cli.main([]) == 0
        assert "usage" in capsys.readouterr().out

    def test_bare_help_command_works(self, capsys):
        # Not just --help: CONTRIBUTING tells contributors to run `./dev help`.
        assert cli.main(["help"]) == 0
        assert "usage" in capsys.readouterr().out

    def test_unknown_command_exits_nonzero(self):
        with pytest.raises(SystemExit) as exit_info:
            cli.main(["nonsense"])
        assert exit_info.value.code != 0

    def test_every_command_is_wired_up(self):
        for name, command in cli.COMMANDS.items():
            assert callable(command.handler), name
            assert command.help, name

    def test_a_command_with_no_options_is_called_with_none(self):
        # main passes whatever the subparser declared as keyword arguments, so a
        # command that declares nothing must be callable with nothing.
        for name, command in cli.COMMANDS.items():
            if command.configure is not None:
                continue

            args = cli.build_parser().parse_args([name])
            options = {k: v for k, v in vars(args).items() if k != "command"}

            assert options == {}, name

    def test_interfaces_declares_dry_run(self):
        args = cli.build_parser().parse_args(["interfaces", "--dry-run"])
        assert args.dry_run is True

    def test_die_becomes_exit_one(self, monkeypatch, capsys):
        monkeypatch.delenv("WOW_ROOT", raising=False)
        monkeypatch.setattr(install, "ENV_FILE", Path("/nonexistent"))

        assert cli.main(["install-status"]) == 1
        assert "error:" in capsys.readouterr().err
