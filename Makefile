# Makefile for AI Diet and Meal Planner

VENV = task/.venv/bin

build:
	docker build -t ai-diet-planner:latest task

up:
	docker stop ai-diet-planner 2>/dev/null || true
	docker run -d --rm --name ai-diet-planner -p 8000:8000 ai-diet-planner:latest

down:
	docker stop ai-diet-planner 2>/dev/null || true

test:
	cd task && $(VENV)/python test/tests.py

logs:
	docker logs -f ai-diet-planner

clean:
	docker rmi ai-diet-planner:latest || true

