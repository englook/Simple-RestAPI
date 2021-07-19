TOKEN_AUTHORIZATION = "fb8af7da955944ae952c723f5829fc5d"


def multipart_to_dict(form_data, cache):
	ret = {}
	for line in form_data.split("form-data;"):
		key = line.partition('"')[2].rpartition('"')[0]
		value = line.partition('\r\n\r\n')[2].partition('\r\n')[0]
		if all((key, value)):
			ret["id"] = len(cache) + 1
			ret[key] = value
			ret["createdAt"] = str(datetime.now())
	ret['isAcvtive'] = ret.pop('ativo')
	return ret

# end-of-file