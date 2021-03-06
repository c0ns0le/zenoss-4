##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


import cgi
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.ZenMessaging.audit import audit
from Products.ZenUtils.ZenTales import talesEval
from Products.ZenUtils.Utils import convToUnits, zdecode, getDisplayType
from Products.ZenWidgets import messaging
from Products.ZenUtils.deprecated import deprecated
from Products.ZenModel.BaseReport import BaseReport

@deprecated
def manage_addDeviceReport(context, id, title = None, REQUEST = None):
    """Add a DeviceReport
    """
    dc = DeviceReport(id, title)
    context._setObject(id, dc)
    if REQUEST is not None:
        audit('UI.Report.Add', dc.id, title=title, reportType=getDisplayType(dc), organizer=context)
        messaging.IMessageSender(context).sendToBrowser(
            'Report Created',
            'Device report %s was created.' % id
        )
        return REQUEST['RESPONSE'].redirect(context.absolute_url() + '/manage_main')



class DeviceReport(BaseReport):

    meta_type = "DeviceReport"

    path = "/"
    deviceQuery = ""
    sortedHeader = ""
    sortedSence = "asc"
    groupby = ""
    columns = []
    colnames = []

    _properties = BaseReport._properties + (
        {'id':'path', 'type':'string', 'mode':'w'},
        {'id':'deviceQuery', 'type':'string', 'mode':'w'},
        {'id':'sortedHeader', 'type':'string', 'mode':'w'},
        {'id':'sortedSence', 'type':'string', 'mode':'w'},
        {'id':'groupby', 'type':'string', 'mode':'w'},
        {'id':'columns', 'type':'lines', 'mode':'w'},
        {'id':'colnames', 'type':'lines', 'mode':'w'},
    )


    # Screen action bindings (and tab definitions)
    factory_type_information = ( 
        { 
            'immediate_view' : '',
            'actions'        :
            ( 
                {'name'          : 'View Report',
                'action'        : '',
                'permissions'   : ("View",),
                },
                {'name'          : 'Edit Report',
                'action'        : 'editDeviceReport',
                'permissions'   : ("Manage DMD",),
                },
            )
         },
        )

    security = ClassSecurityInfo()

    def getBreadCrumbUrlPath(self):
        '''
        Return the url to be used in breadcrumbs for this object.
        '''
        return self.getPrimaryUrlPath() + '/editDeviceReport'


    def getDevices(self):
        """Return the device list for this report.
        """
        devs = self.getDmdRoot("Devices")
        if self.path != "/": devs = devs.getOrganizer(self.path)
        devlist = devs.getSubDevices()
        if self.deviceQuery:
            try:
                return [ dev for dev in devlist \
                            if talesEval("python:"+self.deviceQuery, dev) ]
            except Exception, e:
                return e
        return devlist
            

    def testQueryStyle(self):
        """Return red text style if query is bad.
        """
        try:
            self.getDevices()
        except:
            return "color:#FF0000"
   

    def testColNamesStyle(self):
        """Return red text style if columns and colnames not the same length.
        """
        if len(self.columns) != len(self.colnames): return "color:#FF0000"


    def reportHeader(self):
        h = []
        tname = self.getPrimaryId()
        for i, field in enumerate(self.columns):
            try:name = self.colnames[i]
            except IndexError: name = field
            h.append(self.ZenTableManager.getTableHeader(tname , field, name))
        return "\n".join(h)


    def reportHeaders(self):
        h = []
        for i, field in enumerate(self.columns):
            try:name = self.colnames[i]
            except IndexError: name = field
            
            if field == 'getId': field = 'titleOrId' 
            elif field == 'getManageIp': field = 'ipAddressAsInt' 
            h.append((field, name))
        return h

            
    def reportBody(self, batch): 
        """body of this report create from a filtered and sorted batch.
        """
        body = []
        for dev in batch:
            # If the query is invalid, dev will be an exception string
            if isinstance(dev, basestring):
                body.extend([
                    '<tr class="tablevalues">',
                    '  <td colspan="%d" align="center">' % len(self.columns),
                    '    Query error: %s' % dev,
                    '  </td>',
                    '</tr>',
                    ])
            else:
                body.append("<tr class='tablevalues'>")
                for field in self.columns:
                    body.append("<td>")
                    if field == "getId": field += "Link"

                    # Allow the ability to parse Python
                    if dev.zenPropIsPassword(field):
                        attr = '*****'
                    else:
                        attr = getattr(dev, field, 'Unknown column')
                    variables_and_funcs = {
                       'device':dev, 'dev':dev, 'attr':attr,
                       'convToUnits':convToUnits, 'zdecode':zdecode,
                    }
                    if field.startswith('python:'):
                        expression = field.replace('python:', 'attr=')
                        try:
                            exec(expression, variables_and_funcs)
                            attr = variables_and_funcs['attr']
                        except Exception, ex:
                            attr = str(ex)

                    if callable(attr):
                        try: value = attr()
                        except Exception, ex:
                             value = str(ex)
                    else: value = attr

                    if isinstance(value, (list, tuple, set)):
                        # Some calls don't return strings
                        try: value = ", ".join(value)
                        except Exception, ex:
                             value = str(ex)
                    if (not field.endswith("Link")
                            and isinstance(value, basestring)):
                        value = cgi.escape(value)
                    elif isinstance(value, basestring):
                        value = str(value)
                    body.append(value)
                    body.append("</td>")
                body.append("</tr>")
        
        return "\n".join(body)


InitializeClass(DeviceReport)
