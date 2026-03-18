"""运行快速演示"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.quick_demo import quick_demo

if __name__ == "__main__":
    quick_demo()