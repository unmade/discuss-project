# Benchmark

Test database contains `100166` comments.
Depth of a tree of the most commented comment is `101` and number of descendants is `11409`

> Benchmarks were made with comment service running in docker (`docker-compose up`)


#### List comments for specified instance

List comments with children (`10000` comments per page).
Total number of comments for specified instance is `57642`

```
$ ab -n 10 "http://127.0.0.1/comments/list/?with_children=True&page_size=10000&content_type_id=2&object_id=1"
This is ApacheBench, Version 2.3 <$Revision: 1796539 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        nginx/1.13.7
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /comments/list/?with_children=True&page_size=10000&content_type_id=2&object_id=1
Document Length:        3520845 bytes

Concurrency Level:      1
Time taken for tests:   5.708 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      35210770 bytes
HTML transferred:       35208450 bytes
Requests per second:    1.75 [#/sec] (mean)
Time per request:       570.821 [ms] (mean)
Time per request:       570.821 [ms] (mean, across all concurrent requests)
Transfer rate:          6023.87 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:   501  571  41.6    574     652
Waiting:      476  530  34.6    519     588
Total:        502  571  41.6    574     653

Percentage of the requests served within a certain time (ms)
  50%    574
  66%    576
  75%    595
  80%    602
  90%    653
  95%    653
  98%    653
  99%    653
 100%    653 (longest request)

```

------


List comments with children (`100` comments per page)

```
$ ab -n 10 "http://127.0.0.1/comments/list/?with_children=True&page_size=100&content_type_id=2&object_id=1"
This is ApacheBench, Version 2.3 <$Revision: 1796539 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        nginx/1.13.7
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /comments/list/?with_children=True&page_size=100&content_type_id=2&object_id=1
Document Length:        34796 bytes

Concurrency Level:      1
Time taken for tests:   0.375 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      350260 bytes
HTML transferred:       347960 bytes
Requests per second:    26.68 [#/sec] (mean)
Time per request:       37.486 [ms] (mean)
Time per request:       37.486 [ms] (mean, across all concurrent requests)
Transfer rate:          912.47 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    35   37   2.6     37      44
Waiting:       34   37   2.7     37      44
Total:         35   37   2.6     37      44

Percentage of the requests served within a certain time (ms)
  50%     37
  66%     37
  75%     38
  80%     38
  90%     44
  95%     44
  98%     44
  99%     44
 100%     44 (longest request)

```

------


#### List children for specified comment

Depth of a tree of the most commented comment is `101` and number of descendants is `11409`

```
$ ab -n 10 "http://127.0.0.1/comments/29818/children/"
This is ApacheBench, Version 2.3 <$Revision: 1796539 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        nginx/1.13.7
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /comments/29818/children/
Document Length:        4044443 bytes

Concurrency Level:      1
Time taken for tests:   4.078 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      40446750 bytes
HTML transferred:       40444430 bytes
Requests per second:    2.45 [#/sec] (mean)
Time per request:       407.759 [ms] (mean)
Time per request:       407.759 [ms] (mean, across all concurrent requests)
Transfer rate:          9686.80 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:   357  408  48.8    395     506
Waiting:      319  363  43.7    369     442
Total:        357  408  48.8    395     506

Percentage of the requests served within a certain time (ms)
  50%    395
  66%    408
  75%    411
  80%    482
  90%    506
  95%    506
  98%    506
  99%    506
 100%    506 (longest request)

```

-----


#### User comment history

User has `336` comments in total

```
$ ab -n 10 "http://127.0.0.1/users/362/comments/?page_size=500"
This is ApacheBench, Version 2.3 <$Revision: 1796539 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking 127.0.0.1 (be patient).....done


Server Software:        nginx/1.13.7
Server Hostname:        127.0.0.1
Server Port:            80

Document Path:          /users/362/comments/?page_size=500
Document Length:        122756 bytes

Concurrency Level:      1
Time taken for tests:   0.247 seconds
Complete requests:      10
Failed requests:        0
Total transferred:      1229870 bytes
HTML transferred:       1227560 bytes
Requests per second:    40.48 [#/sec] (mean)
Time per request:       24.701 [ms] (mean)
Time per request:       24.701 [ms] (mean, across all concurrent requests)
Transfer rate:          4862.29 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing:    23   25   2.0     24      28
Waiting:       22   23   2.1     22      27
Total:         23   25   2.0     24      28

Percentage of the requests served within a certain time (ms)
  50%     24
  66%     24
  75%     25
  80%     28
  90%     28
  95%     28
  98%     28
  99%     28
 100%     28 (longest request)

```
