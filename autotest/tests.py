from django.test import TestCase

# Create your tests here.

import os
filepath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(filepath)
print(__file__)

import time
start_time = time.time()

