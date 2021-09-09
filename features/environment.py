import os


def after_scenario(context, feature):
    context.test_container.kill()
