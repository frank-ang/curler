# "Curler", a Simple Load Generator.

# Build:
docker build -t simple-canary:0.0.1 .

# Run:
docker run --env-file /tmp/tmpcreds simple-canary:0.0.1

# Cloudwatch logs metric filter

Create filters for:

* SimpleCanaryDurationMetricFilter

```
[h1="INFO*", h2="Called", h3="endpoint*", endpoint,,,duration_secs,,,status_code, ...]

INFO:root:Client0: Called endpoint: http://api.sandbox01.demolab.host/hello, elapsed seconds: 0.022931, status code: 200, reason: OK

```

