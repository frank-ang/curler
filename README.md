# Build:
docker build -t simple-canary:0.0.1 .

# Run:
docker run --env-file /tmp/tmpcreds simple-canary:0.0.1