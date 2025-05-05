> Buildbot + Renovate = `buildbot_renovate`

> [!CAUTION]
> This is not functional as of now for anything but our own internal repository.

> [!NOTE]
> This plugin relies on [buildbot-nix](https://github.com/nix-community/buildbot-nix.) to work and assumes it's available and running.

This is a [Buildbot](https://www.buildbot.net/) plugin which integrates [Renovate](https://github.com/renovatebot/renovate/) with Buildbot and attempts to replicate the experience one might get with hosted Mend Renovate, without having to use the SaaS or host the Mend Renovate server in a Kubernetes cluster. It supports the following out of the additions to `renovate` the CLI program:

1. Stateful job queue for prioritization of job importance - no
2. Embedded job scheduler to remove the need to set up and monitor cron - kinda
3. Webhook listener to enable dynamic reactions to repository events - yes, if a bit too eager
4. Administration APIs for probing the system state or triggering jobs - no

(2) is supported "by accident" due to runnning inside of buildbot, so you can in fact monitor `renovate` runs, by looking at buildbot's web interface. (3) is supported fully, but it currently doesn't do any debouncing nor does it do some filtering on the events before triggering a build inside of Buildbot. As such every little change in a renovate monitored repository will result in a new build being triggered and `renovate` running.

## How to actually set it up

TODO
