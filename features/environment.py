from docker.models.containers import Container


def after_scenario(context, feature):
    test_container: Container
    test_container = context.test_container
    test_container.kill()
