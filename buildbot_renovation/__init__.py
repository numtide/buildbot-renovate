from buildbot.interfaces import IConfigurator
from buildbot.schedulers.forcesched import ForceScheduler
from buildbot.schedulers.timed import Periodic as PeriodicScheduler
from buildbot.plugins import util, steps
from buildbot.www.hooks.github import GitHubEventHandler
from zope.interface import implementer
from typing import Any, cast

class RenovateHandler(GitHubEventHandler):
    def getSchedulerByName(self, name: str) -> ForceScheduler:
        # we use the fact that scheduler_manager is a multiservice, with schedulers as childs
        # this allow to quickly find schedulers instance by name
        schedulers = self.master.scheduler_manager.namedServices
        if name not in schedulers:
            raise ValueError(f"unknown triggered scheduler: {name!r}")
        sch = schedulers[name]
        if type(sch) != ForceScheduler:
            raise ValueError(f"triggered scheduler is not ForceScheduler: {name!r}")
        return sch

    async def _trigger_renovate(self) -> None:
        self.getSchedulerByName("renovate-webhook").force("webhook")

    async def handle_issues(self, payload: Any, event: Any) -> tuple[list[Any], str]:
        await self._trigger_renovate()
        return [], "git"

    async def handle_issue_comment(self, payload: Any, event: Any) -> tuple[list[Any], str]:
        await self._trigger_renovate()
        return [], "git"

    async def handle_pull_request(self, payload: Any, event: Any) -> tuple[list[Any], str]: # type: ignore[override]
        await self._trigger_renovate()

        ret = cast(
            tuple[list[Any], str],
            await super().handle_pull_request(payload, event)
        )
        return ret


def f_renovate(repo_name: str, repourl: str, actually_update: bool) -> util.BuildFactory:
    f = util.BuildFactory()
    f.addStep(steps.Git(
        repourl=repourl,
        mode="incremental",
        auth_credentials=("git", util.Secret(f"github-token-{repo_name}"))
    ))
    f.addStep(steps.ShellCommand(
        command=[
            "renovate",
            repo_name,
            "--base-dir=./tmp",
            *([] if actually_update else ['--schedule=["on Tuesday except on Tuesday"]'])
        ],
        env={
            "RENOVATE_TOKEN": util.Secret(f"github-token-{repo_name}"),
            "RENOVATE_CONFIG_FILE": "renovate.json"
        }
    ))

    return f

@implementer(IConfigurator)
class BuildbotRenovation():
    def configure(self, c: dict[Any, Any]) -> None:
        renovate = PeriodicScheduler(name="renovate-daily",
                                     builderNames=["numtide/org-renovate"],
                                     periodicBuildTimer=24*60*60)  # type: ignore[no-untyped-call]
        force_renovate = ForceScheduler(
                name=f"renovate",
                builderNames=["numtide/org-renovate"],
                buttonName="Renovate",
            )
        force_renovate_webhook = ForceScheduler(
            name=f"renovate-webhook",
            builderNames=["numtide/org-renovate-webhook"],
            buttonName="Renovate Webhook",
        )

        c['schedulers'].extend([
            renovate,
            force_renovate,
            force_renovate_webhook,
        ])
        c['builders'].extend([
            util.BuilderConfig(
                name="numtide/org-renovate",
                workernames=list(map(lambda x: x.name, c['workers'])),
                factory=f_renovate("numtide/org", "https://github.com/numtide/org", True)
            ),
            util.BuilderConfig(
                name="numtide/org-renovate-webhook",
                workernames=list(map(lambda x: x.name, c['workers'])),
                factory=f_renovate("numtide/org", "https://github.com/numtide/org", False)
            )
        ])
        c['www']['change_hook_dialects']['github']['class'] = RenovateHandler
