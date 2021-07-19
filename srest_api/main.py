import sys
import logging
from RestClientHandler import HTTPServer
from RestClientHandler import RestClientHandler

log = logging.getLogger(__name__)

def main():

	server_address = (sys.argv[1], int(sys.argv[2]))
	with HTTPServer(server_address, RestClientHandler) as rest_api:
		try:
			log.warning(f'Access server on.. http://{server_address[0]}:{server_address[1]}/')
			rest_api.serve_forever()
		except KeyboardInterrupt:
			log.warning('CTRL+C Detected!')

if __name__ == '__main__':
	main()

# end-of-file