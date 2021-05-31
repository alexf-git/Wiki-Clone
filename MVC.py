from html.parser import HTMLParser

class view(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print('found start', tag)
    
    def handle_entag(self, tag):
        print('found end', tag)
    
    def handle_data(self, data):
        print('found data', data)

parser = view()
parser.feed('<html><head><title>Test</title></head>'
            '<body><h1>Parse me!</h1></body></html>')