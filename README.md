# Comment Service

Simple comment service to externally hosts comments posted by users.

It features:
- threaded comments
- comment history
- user comment history
- export to `xml`
- real-time notification system


## Table of contents

* [QuickStart](#quickstart)
* [API](#api)
* [Development](#development)
  * [Testing](#testing)
  * [Extending available export formats](#extending-available-export-formats)
* [Benchmark](#benchmark)


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


### Real-Time Notifications

To test real-time notifications simply run:
```
$ python3 discuss/notifier.py

Connected {'client_id': 'c8c96c8e-1a2b-488b-a444-46800799d54d'}
History: []
```

After that you could create/update/delete comment and see real-time notifications:
```
Connected {'client_id': 'c8c96c8e-1a2b-488b-a444-46800799d54d'}
History: []
Message: {'uid': 'Nh1NDMpn1Ihu640wlF379o', 'channel': 'thread:1_1', 'data': {'comment': {'id': 100167, 'content_type_id': 1, 'object_id': 1, 'content': '12345', 'parent': None, 'created_at': '2017-12-18T22:44:39.635045Z', 'author': {'username': 'fdooch', 'email': 'fdooch@example.com'}}, 'user': {'username': 'fdooch', 'email': 'fdooch@example.com'}, 'action': 0}}
```


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
