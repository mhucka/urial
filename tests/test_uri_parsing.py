import os
import pytest
import sys
from   time import time

try:
    thisdir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(thisdir, '..'))
except:
    sys.path.append('..')

from urial.__main__ import uris_in_text

def test_uris_in_text():
    assert uris_in_text('blah a://b.c blah') == ['a://b.c']
    assert uris_in_text('blah a://b.c blah', True) == ['a://b.c']
    assert uris_in_text('blah <a://b.c> blah') == ['a://b.c']
    assert uris_in_text('blah <a://b.c> blah', True) == ['a://b.c']
    assert uris_in_text('blah {a://b.c} blah') == ['a://b.c']
    assert uris_in_text('blah {a://b.c} blah', True) == ['a://b.c']
    assert uris_in_text('blah tel:+1-816-555-1212') == ['tel:+1-816-555-1212']
    assert uris_in_text('foo https://en.wikipedia.org/wiki/Bracket_(disambiguation)?') == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)']
    assert uris_in_text('foo https://en.wikipedia.org/wiki/Bracket_(disambiguation)?', True) == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)?']
    assert uris_in_text('foo (https://en.wikipedia.org/wiki/Bracket_(disambiguation)?)') == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)']
    assert uris_in_text('foo [https://en.wikipedia.org/wiki/Bracket_(disambiguation)?]') == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)']
    assert uris_in_text('foo [https://en.wikipedia.org/wiki/Bracket_(disambiguation)?]', True) == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)?']
    assert uris_in_text('foo [https://en.wikipedia.org/wiki/Bracket_(disambiguation)?]', True) == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)?']
    assert uris_in_text('[foo https://en.wikipedia.org/wiki/Bracket_(disambiguation)?]', True) == ['https://en.wikipedia.org/wiki/Bracket_(disambiguation)?']
    assert uris_in_text('x ldap://[2001:db8::7]/c=GB?a?b y') == ['ldap://[2001:db8::7]/c=GB?a?b']
    assert uris_in_text('x file://localhost/test y') == ['file://localhost/test']
    assert uris_in_text('http:test') == ['http:test']
    assert uris_in_text('x uri://a/b/c/d?q y') == ['uri://a/b/c/d?q']
    assert uris_in_text('x example://a/b/c/%7Bfoo%7D y') == ['example://a/b/c/%7Bfoo%7D']
    assert uris_in_text('x wss://example.com/foo?bar=baz y') == ['wss://example.com/foo?bar=baz']
    assert uris_in_text('x WS://ABC.COM:80/chat#one y') == ['WS://ABC.COM:80/chat#one']
    assert uris_in_text('x prefs:root=General&path=VPN/DNS y') == ['prefs:root=General&path=VPN/DNS']
    assert uris_in_text('x http://example.com/test/* y') == ['http://example.com/test/*']
    assert uris_in_text('x http://example.com/test/*. y') == ['http://example.com/test/*']
    assert uris_in_text('x http://example.com/test/*. y', True) == ['http://example.com/test/*.']
    assert uris_in_text('x http://example.com/test/*? y') == ['http://example.com/test/*']
    assert uris_in_text('x (http://example.com/test/*) y') == ['http://example.com/test/*']
    assert uris_in_text('x http://example.com/test/*. y', True) == ['http://example.com/test/*.']
    assert uris_in_text('x http://wayback.archive.org/web/*/http://www.alexa.com/topsites y') == ['http://wayback.archive.org/web/*/http://www.alexa.com/topsites']
