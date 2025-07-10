# -*- coding: utf-8 -*-
import requests
import hashlib
from .exceptions import HttpError
from . import __version__, __api_version__
import logging
logger = logging.getLogger(__name__)

class RequestApi:
	__base_url = 'https://senler.ru/api/'

	def __init__(self, secret):
		self.__session = requests.Session()
		self.__secret = str(secret).strip()
		self.__session.headers['User-Agent'] = f'SenlerPythonClient/{__version__}'

	def _calculate_hash(self, data):
		str_data = str()
		for key in data.keys():
			item = data[key]
			if isinstance(item, list) or isinstance(item, tuple):
				str_data += ''.join(item)
			else:
				str_data += str(item)
		str_data += self.__secret
		return hashlib.md5(str_data.encode('utf-8')).hexdigest()

	def send(self, method_name, data):
		data['v'] = str(__api_version__)
		data['access_token'] = self.__secret
		url = self.__base_url + str(method_name)
		logger.error(url)
		logger.error(data)

		if url == 'https://senler.ru/api/Deliveries/Stat' and data['m']=='get':
			logger.error('get')
			multipart_payload = {key: (None, val) for key, val in data.items()}

			result = requests.post(url, files=multipart_payload)
			logger.error(result.text)
		else:
			request = requests.Request(
				method="GET",
				url=url,
				params=data
			)
			prepared_request = self.__session.prepare_request(request)

			try:
				result = self.__session.post(url, data, timeout=300)
			except (ConnectionError, TimeoutError, requests.exceptions.ReadTimeout):
				raise HttpError('Error with connection to senler.ru API server')
		if result.status_code == 404:
			raise HttpError(f'Method {method_name} not found!')
		return result

	@property
	def url(self):
		return self.__base_url
