.PHONY: build build-images deploy cleanup test

build:
	pip install -r requirements.txt

build-images:
	docker build -t nexapod-server:latest -f Infrastruture/Dockerfile.server .
	docker build -t nexapod-client:latest -f Infrastruture/Dockerfile.client .

deploy:
	./scripts/deploy.sh

cleanup:
	./scripts/cleanup.sh

test:
	pytest
