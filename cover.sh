#!/bin/bash
PYTHONPATH=. coverage run --source=sorcestone ./runtests.py
coverage xml && coverage report