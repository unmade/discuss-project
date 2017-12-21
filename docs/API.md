# Table of contents
* [API](#api)
  * [Comments](#comments)
  * [Users](#users)
* [Real-Time Notifications](#real-time-notifications)
  * [Connect, subscribe on channel](#connect-subscribe-on-channel)

# API

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


### /comments/list/export/

**Method: GET**

Exports comments as file, accepts same parameters as `/comments/list/`.
Additionally you could provide output file format in `output` (default `xml`).


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

**Method: PATCH**

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

**Method: DELETE**

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

**Method: GET**

Returns user actions


### /users/:id/comments/

**Method: GET**

Returns user comment history


### /users/token/

**Method: POST**

Returns token for user to authorize itself in notification system

Payload example:
```js
{
    "username": "fdooch",
    "email": "mail@me.com"
}
```


# Real-Time Notifications

Service provides WebSocket-based notification system.
To start receiving notifications client should subsribe to thread channel.
Each thread has channel as follow:
`thread:{content_type_id}_{object_id}`.


## Connect, subscribe on channel

Internally, notification system relies on `centrifugo` real-time messagin server.
Check out its [Client protocol description](https://fzambia.gitbooks.io/centrifugal/content/server/client_protocol.html)

To obtain token for user send POST-request to `/users/token/`:


WebSocket endpoint is:
```
ws://api.comments.com/centrifugo/connection/websocket
```

Available commands are:
- `connect` - send authorization parameters to Centrifugo so your connection could start subscribing on channels.
- `subsribe` - allows to subscribe on channel after client successfully connected
- `unsubscribe` - allows to unsubscribe from channel
- `history` - returns channel history information

See this [simple example](../discuss/notifier.py).
