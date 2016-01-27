def convert_url(url, lang):
	result = url
	if lang == 'en':
		result = url.replace('.html', '_en.html')
	return result