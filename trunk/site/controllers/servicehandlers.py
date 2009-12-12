import os
import logging
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import users

from controllers.home import BASE_PATH, PROJECT_PATH
from controllers.address import CaptureAddress, EditAddress, DeleteAddress
from controllers.owner import ViewOwner, CaptureOwner, EditOwner, DeleteOwner
from controllers.venue import ViewVenue, CaptureVenue, EditVenue, DeleteVenue
from controllers.bedroom \
    import ViewBedroom, CaptureBedroom, EditBedroom, DeleteBedroom
from controllers.bed  import ViewBed, CaptureBed, EditBed, DeleteBed
from controllers.bathroom \
    import CaptureBathroom, EditBathroom, DeleteBathroom
from controllers.berth import ViewBerth
from controllers.slot import ViewSlot
from controllers.inspection \
    import CaptureInspection, EditInspection, DeleteInspection
from controllers.complaint \
    import CaptureComplaint, EditComplaint, DeleteComplaint
from controllers.phonenumber \
        import CapturePhoneNumber, EditPhoneNumber, DeletePhoneNumber
from controllers.emailaddress \
        import CaptureEmailAddress, EditEmailAddress, DeleteEmailAddress
from controllers.photograph \
        import CapturePhotograph, EditPhotograph, DeletePhotograph
from models.hostinfo import Owner
from controllers.utils import get_authentication_urls


#from acl import Acl, AclRules
#Acl.roles_map = {
#    'admin': [
#        ('*', '*', True),
#    ],
#    'host': [
#        ('*', '*', True),
#    ],
#}
#
## Assign users to the 'host' role.
#AclRules.insert_or_update(
#    area='ownerinfo',
#    user='test@example.com', 
#    roles=['host'])
#AclRules.insert_or_update(
#    area='*',
#    user='mike@example.com', 
#    roles=['admin'])

PAGESIZE = 15
class ManageHosts(webapp.RequestHandler):
    def get(self):
        #acl = Acl(area='hostinfo',
        #          user=users.get_current_user())
        #assert acl.has_access(topic='ManageHosts', name='get') is True

        auth_url, auth_url_text = get_authentication_urls(self.request.uri)
        start = self.request.get('start', ' ')
        new_start = start
        query = Owner.all().order('referenceNumber')
        query.filter('referenceNumber >=', start)
        owners = query.fetch(PAGESIZE+1)
        if owners:
            new_start = owners[-1].referenceNumber

        filepath = os.path.join(PROJECT_PATH, 'templates', 'services', 'managehosts.html')
        self.response.out.write(template.render(filepath, 
          {
              'base_path':BASE_PATH,
              'start':new_start,
              'owners':owners,
              'user':users.get_current_user(),
              'is_admin_user':users.is_current_user_admin(),
              'auth_url':auth_url,
              'auth_url_text':auth_url_text
              }))

application = webapp.WSGIApplication([
                  ('/services/hostinfo', ManageHosts),
                  ('/services/owner/viewowner', ViewOwner),
                  ('/services/owner/captureowner', CaptureOwner),
                  ('/services/owner/editowner', EditOwner),
                  ('/services/owner/deleteowner', DeleteOwner),
                  ('/services/owner/address/captureaddress', CaptureAddress),
                  ('/services/owner/address/editaddress', EditAddress),
                  ('/services/owner/address/deleteaddress', DeleteAddress),
                  ('/services/owner/contact/capturephone', CapturePhoneNumber),
                  ('/services/owner/contact/editphone', EditPhoneNumber),
                  ('/services/owner/contact/deletephone', DeletePhoneNumber),
                  ('/services/owner/email/captureemail', CaptureEmailAddress),
                  ('/services/owner/email/editemail', EditEmailAddress),
                  ('/services/owner/email/deleteemail', DeleteEmailAddress),
                  ('/services/owner/viewvenue', ViewVenue),
                  ('/services/owner/capturevenue', CaptureVenue),
                  ('/services/owner/editvenue', EditVenue),
                  ('/services/owner/deletevenue', DeleteVenue),
                  ('/services/owner/venue/address/captureaddress', CaptureAddress),
                  ('/services/owner/venue/address/editaddress', EditAddress),
                  ('/services/owner/venue/address/deleteaddress', DeleteAddress),
                  ('/services/owner/venue/contact/capturephone', CapturePhoneNumber),
                  ('/services/owner/venue/contact/editphone', EditPhoneNumber),
                  ('/services/owner/venue/contact/deletephone', DeletePhoneNumber),
                  ('/services/owner/venue/email/captureemail', CaptureEmailAddress),
                  ('/services/owner/venue/email/editemail', EditEmailAddress),
                  ('/services/owner/venue/email/deleteemail', DeleteEmailAddress),
                  ('/services/owner/venue/capturephotograph', CapturePhotograph),
                  ('/services/owner/venue/editphotograph', EditPhotograph),
                  ('/services/owner/venue/deletephotograph', DeletePhotograph),
                  ('/services/owner/venue/viewbedroom', ViewBedroom),
                  ('/services/owner/venue/capturebedroom', CaptureBedroom),
                  ('/services/owner/venue/editbedroom', EditBedroom),
                  ('/services/owner/venue/deletebedroom', DeleteBedroom),
                  ('/services/owner/venue/capturebed', CaptureBed),
                  ('/services/owner/venue/editbed', EditBed),
                  ('/services/owner/venue/deletebed', DeleteBed),
                  ('/services/owner/venue/capturebathroom', CaptureBathroom),
                  ('/services/owner/venue/editbathroom', EditBathroom),
                  ('/services/owner/venue/deletebathroom', DeleteBathroom),
                  ('/services/owner/venue/captureinspection', CaptureInspection),
                  ('/services/owner/venue/editinspection', EditInspection),
                  ('/services/owner/venue/deleteinspection', DeleteInspection),
                  ('/services/owner/venue/capturecomplaint', CaptureComplaint),
                  ('/services/owner/venue/editcomplaint', EditComplaint),
                  ('/services/owner/venue/deletecomplaint', DeleteComplaint),
                  ('/services/owner/venue/viewbed', ViewBed),
                  ('/services/owner/venue/viewberth', ViewBerth),
                  ('/services/owner/venue/viewslot', ViewSlot),
                  ], debug=True)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
