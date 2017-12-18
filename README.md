# Comment Service

Simple comment service to externally hosts comments posted by users.

It features:
- threaded comments
- comment history
- user comment history
- export to `xml`
- real-time notification system


## QuickStart

Clone repo and run:
```
docker-compose build
docker-compose up
```


## API

Learn more about [API](docs/API.md)


## Development

Set up `.env` file with settings suitable for local development, for example:

```
DJANGO_DEBUG=True
DJANGO_SETTINGS_MODULE=discuss.settings.local
```

Start docker containers:
```
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build
```


### Testing

To run test:
```
docker-compose -f docker-compose.yml -f docker-compose.test.yml run test
```


### Extending available export formats

By default only export available only in `xml` format.

You could easily add more formats.
All you need to do is to modify `discuss.comment.outputters.CommentOutputter`:

```python
# comment.outputters

class CommentOutputter(Outputter):

    def __init__(self):
        super().__init__()
        # register formats here
        self.add_outputter('xml', 'text/xml', self.to_xml)
        self.add_outputter('csv', 'text/csv', self.to_csv)

    def to_xml(self, items):
        ...

    def to_csv(self, items):
        yield 'id,parent_id,content,created_at_str,author_email,author_username\n'
        for item in items:
            yield (
                f'{item["id"]},'
                f'{item["parent_id"]},'
                f'{item["content"]},'
                f'{item["created_at_str"]},'
                f'{item["author__email"]},'
                f'{item["author__username"]}\n'
            )

```

As you can see, you should define generator which yields chunks of data.