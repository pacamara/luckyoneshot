from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

# Create a Pyramid WSGI app
def main(global_config, **settings):
    config = Configurator(settings=settings)

    my_session_factory = SignedCookieSessionFactory('40HeadOfWellBredDairyCattle180TodsOfWool')
    config.set_session_factory(my_session_factory)

    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.add_route('storeImageRoute', '/lucky')

    config.scan()
    return config.make_wsgi_app()
