@set PYTHON=/opt/zenoss/bin/python
@set INSTANCE_HOME=/opt/zenoss
@set CONFIG_FILE=%INSTANCE_HOME%\etc\zope.conf
@set ZDCTL=/opt/zenoss/zopehome\zopectl

"%ZDCTL%" -C "%CONFIG_FILE%" %1 %2 %3 %4 %5 %6 %7
