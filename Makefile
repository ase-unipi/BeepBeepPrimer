
.PHONY: all run redis celery

all: redis celery run

run:
	STRAVA_CLIENT_ID=29639
	STRAVA_CLIENT_SECRET=a80429b277ed2b47a80ba49cb8f32b7decf8cb87
	python monolith/app.py

redis:
	if [ `ps aux | grep redis | grep server | wc -l` -lt 3 ]; then \
		redis-server & \
	fi

celery:
	if [ `ps aux | grep celery | grep monolith | wc -l` -lt 3 ]; then \
		celery worker -A monolith.background & \
	fi

stop:
	killall -q redis-server celery python
