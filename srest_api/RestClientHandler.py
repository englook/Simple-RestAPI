import json
import logging
from urllib.parse import parse_qs
from urllib.parse import urlparse
from urllib.parse import unquote
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from socketserver import ForkingMixIn, ThreadingMixIn
from exceptions import NotFoundResponse
from exceptions import InvalidTokenAuthorization
from exceptions import BadRequestResponse
from utils import multipart_to_dict
from utils import TOKEN_AUTHORIZATION

log = logging.getLogger(__name__)


class HTTPServer(ThreadingMixIn, HTTPServer):
	block_on_close = True
	allow_reuse_address = True


class RestClientHandler(BaseHTTPRequestHandler):
	"""
	Handler responsável pela implementação do serviço.
	"""
	cache = []

	def _set_headers(self):
		self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
		self.send_header('Expires', 'Thu, 01 Jan 1970 00:00:00 GMT')
		self.send_header('Content-type', 'application/json')
		self.send_header('Pragma', 'no-cache')
		self.end_headers()

	def log_request(self, code=None, size=None):
		log.warning(f'status="{code}" method="{self.command}" path="{self.path}"')

	def do_OPTIONS(self):
		try:
			self.send_response(501)
			self._set_headers()
			self.wfile.write(self._json_reponse({"msg": "Unsupported method ('OPTIONS')"}))
		except BadRequestResponse as e:
			self.send_response(e.status)
			self.wfile.write(self._json_reponse(e.msg))

	def do_GET(self):
		try:
			if self._validate_token():
				self.send_response(200)
				self._set_headers()
				parsed = urlparse(self.path)
				dquery = parse_qs(unquote(parsed.query))
				data = self._search_data(dquery)
				self.wfile.write(data)
			else:
				e = InvalidTokenAuthorization()
				self.send_response(e.status)
				self.wfile.write(e.msg)
		except BadRequestResponse as e:
			self.send_response(e.status)
			self.wfile.write(self._json_reponse(e.msg))

	def do_POST(self):
		try:
			content_length = int(self.headers.get('content-length'))
			post_data = self.rfile.read(content_length).decode('utf-8')
			data = multipart_to_dict(post_data, self.cache)
			self.send_response(200)
			self._set_headers()
			self.cache.append(data)
			self.wfile.write(self._json_reponse(data))
		except BadRequestResponse as e:
			self.send_response(e.status)
			self.wfile.write(self._json_reponse(e.msg))

	def do_PUT(self):
		try:
			path = self.path.split('/')
			if path[1] == self.command:
				cid = int(path[-1])
			content_length = int(self.headers.get('content-length'))
			put_data = self.rfile.read(content_length).decode('utf-8')
			data = multipart_to_dict(put_data, self.cache)
			data['id'] = cid
			try:
				self.cache.pop(abs(cid-1))
			except IndexError:
				pass
			self.cache.insert(cid-1, data)
			self.send_response(201)
			self._set_headers()
			self.wfile.write(self._json_reponse(data))
		except BadRequestResponse as e:
			self.send_response(e.status)
			self.wfile.write(self._json_reponse(e.msg))

	def do_DELETE(self):
		try:
			path = self.path.split('/')
			if path[1] == self.command:
				try:
					idx = (int(path[-1]) - 1)
					self.cache.pop(idx)
				except (TypeError, IndexError) as e:
					response_error = BadRequestResponse(str(e))
					self.send_response(response_error.status)
					self.wfile.write(self._json_reponse({"msg": response_error.msg}))
					return
			self.send_response(200)
			self._set_headers()
			self.wfile.write(self._json_reponse({"msg": "delete successfully"}))
		except NotFoundResponse as e:
			self.send_response(e.status_code)
			self.wfile.write(self._json_reponse({"msg": str(e.msg)}))

	def _json_reponse(self, response):
		return json.dumps(response, default=str()).encode('utf-8')

	def _validate_token(self):
		if self.headers["Authorization"] in (TOKEN_AUTHORIZATION, "undefined"):
			return True

	def _search_data(self, dquery):

		if not dquery or not self.cache:
			data = json.dumps(self.cache, indent=4).encode('utf-8')
			return data

		data = []
		for value in self.cache:
			for q in dquery.values():
				if set(q) & set(value.values()):
					data.append(value)
		return json.dumps(data).encode('utf-8')

# end-of-file