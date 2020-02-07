from flask import Blueprint


# see https://github.com/pallets/flask/issues/593
class EnhancedBlueprint(Blueprint):
    def register_blueprint(self, blueprint, **options):
        def deferred(state):
            url_prefix = options.get('url_prefix')
            if url_prefix is None:
                url_prefix = blueprint.url_prefix
            if 'url_prefix' in options:
                del options['url_prefix']

            state.app.register_blueprint(blueprint, url_prefix, **options)

        self.record(deferred)
