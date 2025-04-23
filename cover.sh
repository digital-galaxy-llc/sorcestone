#!/bin/bash
PYTHONPATH=. coverage run ./runtests.py
coverage xml && coverage report