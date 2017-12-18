# Table of contents
* [Comments](#comments)
* [Users](#users)


## Comments

### /comments/list/

**Method: GET**

Returns list of comments

| Name             | Type    | Description |
| :-------------   | :------ | :------- |
| with_children    | bool    | Includes children |
| page_size        | int     | Sets page size |
| content_type_id  | int     | Filters comments by content_type_id |
| object_id        | int     | Filters comments by object_id |
| username         | str     | Filters comments by username |
| created_0        | date    | Filters comments created after provided date |
| created_1        | date    | Filters comments created before provided date |


### /comments/list/download/

**Method: GET**

Exports comments as file. It accepts same parameters as `/comments/list/`.
Additionally you could provide output file format in `output` param (default `xml`).


### /comments/:id/history/

**Method: GET**

Returns history for comment with specified id



### /comments/:id/children/

**Method: GET**

Returns children for comment with specified id


### /comments/create/

**Method: POST**

Creates new comment

Payload example:
```js
{
    "comment": {
        "content_type_id": 1,
        "object_id": 1,
        "content": "12345",
        "parent": null
    },
    "auth_user": {
        "username": "fdooch",
        "email": "mail@me.com"
    }
}
```


### /comments/:id/update/

Updates content of comment with specified id

Payload example:
```js
{
    "comment": {
        "content": "12345"
    },
    "auth_user": {
        "username": "fdooch",
        "email": "mail@me.com"
    }
}
```



### /comments/:id/delete/

Deletes comment with specified id

Payload example:
```js
{
    "auth_user": {
        "username": "fdooch",
        "email": "mail@me.com"
    }
}
```


## Users

### /users/:id/actions/

Returns user actions


### /users/:id/history/

Returns user comment history
