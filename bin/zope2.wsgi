from Zope2.Startup.run import configure
from Zope2 import startup
configure('/opt/zenoss/etc/zope.conf')
startup()
# mod_wsgi looks for the special name 'application'.
from ZPublisher.WSGIPublisher import publish_module as application
