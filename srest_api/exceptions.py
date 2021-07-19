HTTP_400_BAD_REQUEST = 400
HTTP_401_INVALID_TOKEN = 401
HTTP_404_NOT_FOUND = 404
HTTP_500_INTERNAL_SERVER_ERROR = 500


class ExceptionResponse(Exception):

	def __init__(self, msg_error, status):
		self.msg = msg_error
		self.status = status


class NotFoundResponse(ExceptionResponse):
	def __init__(self, msg):
		ExceptionResponse.__init__(self, {'error': msg}, status=HTTP_404_NOT_FOUND)


class InvalidTokenAuthorization(ExceptionResponse):
	def __init__(self, msg="401 Unauthorized".encode('utf-8')):
		ExceptionResponse.__init__(self, {'error': msg}, status=HTTP_401_INVALID_TOKEN)


class BadRequestResponse(ExceptionResponse):
	def __init__(self, msg):
		ExceptionResponse.__init__(self, {'error': msg}, status=HTTP_400_BAD_REQUEST)

# end-of-file