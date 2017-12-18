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
docker-compose up --build
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


## Benchmark

For benchmarking was used this [dump](https://yadi.sk/d/4CGWoVL23QjaoR)

> To load dump download it and run:
> ```
> docker-compose up db
> docker exec -i {DB_CONTAINER_ID} psql -U discuss -c 'CREATE DATABASE discuss_benchmark'
> cat discuss_dump | docker exec -i {DB_CONTAINER_ID} psql -U postgres -d discuss_benchmark
> ```
> Don't forget to switch to this DB in your settings

Test database contains `100166` comments.
Depth of a tree of the most commented comment is `101` and number of descendants is `11409`

See benchmark [results](docs/BENCHMARK.md)
