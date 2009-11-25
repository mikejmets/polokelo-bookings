from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from models.hostinfo import Photograph


class FullSizeImage(webapp.RequestHandler):
    def get(self):
        photo = Photograph.get(self.request.get('photokey'))
        if photo:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(photo.fullsize)
        else:
            self.response.out.write('No image')

class ThumbNailImage(webapp.RequestHandler):
    def get(self):
        photo = Photograph.get(self.request.get('photokey'))
        if photo:
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(photo.thumbnail)
        else:
            self.response.out.write('No image')


application = webapp.WSGIApplication([
                            ('/viewer/fullsize', FullSizeImage),
                            ('/viewer/thumbnail', ThumbNailImage),
                            ], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
