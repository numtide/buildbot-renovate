from buildbot.plugins import schedulers

nightly = schedulers.Periodic(name="daily",
                              builderNames=["full-solaris"],
                              periodicBuildTimer=24*60*60)

c['schedulers'] = [nightly]
