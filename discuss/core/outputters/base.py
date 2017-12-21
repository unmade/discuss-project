class Outputter:

    def __init__(self):
        self.outputters = {}
        self.mimetypes = {}

    def add_outputter(self, output_format, mimetype, func):
        self.outputters[output_format] = func
        self.mimetypes[output_format] = mimetype

    def output(self, output_format, items):
        return self.outputters[output_format](items)
