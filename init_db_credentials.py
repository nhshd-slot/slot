# This file was shamelessly ripped off from https://developers.google.com/api-client-library/python/start/get_started


#!/usr/bin/python
#
# Copyright 2012 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import BaseHTTPServer
import urlparse
import config


from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
  """Child class of BaseHTTPRequestHandler that only handles GET request."""

  # Create a flow object. This object holds the client_id, client_secret, and
  # scope. It assists with OAuth 2.0 steps to get user authorization and
  # credentials. For this example, the client ID and secret are command-line
  # arguments.
  flow = OAuth2WebServerFlow(config.google_client_id,
                             config.google_client_secret,
                             'https://spreadsheets.google.com/feeds/',
                             redirect_uri='http://localhost:8080/')

  def do_GET(self):
    """Handler for GET request."""
    print '\nNEW REQUEST, Path: %s' % (self.path)
    print 'Headers: %s' % self.headers

    # To use this server, you first visit
    # http://localhost:8080/?fake_user=<some_user_name>. You can use any name you
    # like for the fake_user. It's only used as a key to store credentials,
    # and has no relationship with real user names. In a real system, you would
    # only use logged-in users for your system.
    if self.path.startswith('/init'):
      # Initial page entered by user
      self.handle_initial_url()

    # When you redirect to the authorization server below, it redirects back
    # to to http://localhost:8080/?code=<some_code> after the user grants access
    # permission for your application.
    elif self.path.startswith('/?code='):
      # Page redirected back from auth server
      self.handle_redirected_url()
    # Only the two URL patterns above are accepted by this server.
    else:
      # Either an error from auth server or bad user entered URL.
      self.respond_ignore()

  def handle_initial_url(self):
    """Handles the initial path."""

    # Call a helper function defined below to get the credentials for this user.
    credentials = self.get_credentials('nhshd')

    # If there are no credentials for this fake user or they are invalid,
    # we need to get new credentials.
    if credentials is None or credentials.invalid:
      # Call a helper function defined below to respond to this GET request
      # with a response that redirects the browser to the authorization server.
      self.respond_redirect_to_auth_server()
    else:
      try:

        """Responds to the current request that has an unknown path."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write('Credentials saved')

      except AccessTokenRefreshError:
        # This may happen when access tokens expire. Redirect the browser to
        # the authorization server
        self.respond_redirect_to_auth_server()

  def handle_redirected_url(self):
    """Handles the redirection back from the authorization server."""
    # The server should have responded with a "code" URL query parameter. This
    # is needed to acquire credentials.
    code = self.get_code_from_url_param()

    #
    # This is an important step.
    #
    # We take the code provided by the authorization server and pass it to the
    # flow.step2_exchange() function. This function contacts the authorization
    # server and exchanges the "code" for credentials.
    credentials = RequestHandler.flow.step2_exchange(code)

    # Call a helper function defined below to save these credentials.
    self.save_credentials('nhshd', credentials)

    # Call a helper function defined below to get calendar data for this user.
    return "Creds saved"

  def respond_redirect_to_auth_server(self):
    """Respond to the current request by redirecting to the auth server."""
    #
    # This is an important step.
    #
    # We use the flow object to get an authorization server URL that we should
    # redirect the browser to. We also supply the function with a redirect_uri.
    # When the auth server has finished requesting access, it redirects
    # back to this address. Here is pseudocode describing what the auth server
    # does:
    #   if (user has already granted access):
    #     Do not ask the user again.
    #     Redirect back to redirect_uri with an authorization code.
    #   else:
    #     Ask the user to grant your app access to the scope and service.
    #     if (the user accepts):
    #       Redirect back to redirect_uri with an authorization code.
    #     else:
    #       Redirect back to redirect_uri with an error code.
    uri = RequestHandler.flow.step1_get_authorize_url()

    # Set the necessary headers to respond with the redirect. Also set a cookie
    # to store our fake_user name. We will need this when the auth server
    # redirects back to this server.
    print 'Redirecting %s to %s' % ('nhshd', uri)
    self.send_response(301)
    self.send_header('Cache-Control', 'no-cache')
    self.send_header('Location', uri)
    self.end_headers()

  def respond_ignore(self):
    """Responds to the current request that has an unknown path."""
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.send_header('Cache-Control', 'no-cache')
    self.end_headers()
    self.wfile.write(
      'This path is invalid or user denied access:\n%s\n\n' % self.path)
    self.wfile.write(
      'User entered URL should look like: http://localhost:8080/')

  def respond_calendar_data(self, calendar_output):
    """Responds to the current request by writing calendar data to stream."""
    self.send_response(200)
    self.send_header('Content-type', 'text/plain')
    self.send_header('Cache-Control', 'no-cache')
    self.end_headers()
    self.wfile.write(calendar_output)

  def get_credentials(self, fake_user):
    """Using the fake user name as a key, retrieve the credentials."""
    storage = Storage('credentials-%s.dat' % (fake_user))
    return storage.get()

  def save_credentials(self, fake_user, credentials):
    """Using the fake user name as a key, save the credentials."""
    storage = Storage('credentials-%s.dat' % (fake_user))
    storage.put(credentials)


  def get_code_from_url_param(self):
    """Get the code query parameter from the current request."""
    parsed = urlparse.urlparse(self.path)
    code = urlparse.parse_qs(parsed.query)['code'][0]
    print 'Code from URL: %s' % code
    return code

def main():
  try:
    server = BaseHTTPServer.HTTPServer(('', 8080), RequestHandler)
    print 'Starting server. Use Control+C to stop.'
    server.serve_forever()
  except KeyboardInterrupt:
    print 'Shutting down server.'
    server.socket.close()

if __name__ == '__main__':
  main()