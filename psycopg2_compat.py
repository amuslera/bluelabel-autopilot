"""
Compatibility layer to use psycopg (v3) in place of psycopg2
"""
import sys
import psycopg

# Create a fake psycopg2 module that redirects to psycopg
class FakePsycopg2:
    def __getattr__(self, name):
        return getattr(psycopg, name)

# Install the compatibility layer
sys.modules['psycopg2'] = FakePsycopg2()
sys.modules['psycopg2.extensions'] = psycopg
sys.modules['psycopg2.extras'] = psycopg

print("✅ psycopg2 compatibility layer installed")