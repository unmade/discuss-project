from core.outputters.base import Outputter


class CommentOutputter(Outputter):

    def __init__(self):
        super().__init__()
        self.add_outputter('xml', 'text/xml', self.to_xml)

    def to_xml(self, items):
        yield '<?xml version="1.0" encoding="UTF-8"?><root>'
        for item in items:
            parent = f'<parent_id>{item["parent_id"]}</parent_id>' if item['parent_id'] else '<parent_id />'
            yield (
                f'<id>{item["id"]}</id>'
                f'{parent}'
                f'<content>{item["content"]}</content>'
                f'<created_at_str>{item["created_at_str"]}</created_at_str>'
                '<author>'
                f'    <email>{item["author__email"]}</email>'
                f'    <username>{item["author__username"]}</username>'
                '</author>'
            )
        yield '</root>'
