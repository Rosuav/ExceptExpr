# File names and line numbers are relative to the CPython source tree as of
# early Feb 2014.

# First off, there are a huge number like this:

# Lib/pdb.py:865:
            try:
                reply = input('Clear all breaks? ')
            except EOFError:
                reply = 'no'
# Becomes:
            reply = input('Clear all breaks? ') except EOFError: 'no'

# Lib/pdb.py:433:
        try:
            func = getattr(self, 'do_' + cmd)
        except AttributeError:
            func = self.default
# Becomes:
        func = getattr(self, 'do_' + cmd) except AttributeError: self.default

# Lib/pdb.py:461:
        try:
            ret = self._complete_expression(text, line, begidx, endidx)
        except Exception:
            ret = []
# Becomes:
        ret = self._complete_expression(text, line, begidx, endidx) except Exception: []

# Lib/pdb.py:644:
                try:
                    func = eval(arg,
                                self.curframe.f_globals,
                                self.curframe_locals)
                except:
                    func = arg
# Could become:
                func = (eval(arg,
                            self.curframe.f_globals,
                            self.curframe_locals)
                    except: arg)

# Lib/tkinter/__init__.py:1228:
        try:
            e.delta = getint(D)
        except ValueError:
            e.delta = 0
# Becomes:
        e.delta = getint(D) except ValueError: 0

# Lib/pprint.py:87:
        try:
            rv = self.obj.__lt__(other.obj)
        except TypeError:
            rv = NotImplemented
# Becomes:
        rv = self.obj.__lt__(other.obj) except TypeError: NotImplemented

# Lib/copy.py:79:
    try:
        issc = issubclass(cls, type)
    except TypeError: # cls is not a class
        issc = False
# Becomes:
    issc = issubclass(cls, type) except TypeError: False
# (Note that ibid line 157 has almost the same construct but defaulting to 0.)

# Lib/email/_header_value_parser.py:1644:
        try:
            token, value = get_encoded_word(value)
        except errors.HeaderParseError:
            # XXX: need to figure out how to register defects when
            # appropriate here.
            token, value = get_atext(value)
# Becomes:
        # XXX: need to figure out how to register defects when
        # appropriate here.
        token, value = get_encoded_word(value) except errors.HeaderParseError: get_atext(value)

# All sorts of different exceptions, but all following the same pattern:
#     x = y except SomeError: z
# and z is usually a constant, too.

# Similarly, there are many cases where a return value is calculated this way.

# Lib/xml/dom/minidom.py:489:
    def item(self, index):
        try:
            return self[list(self._attrs.keys())[index]]
        except IndexError:
            return None
# Becomes:
    def item(self, index):
        return self[list(self._attrs.keys())[index]] except IndexError: None

# Lib/xml/dom/minidom.py:573:
    def getNamedItem(self, name):
        try:
            return self._attrs[name]
        except KeyError:
            return None
# Not sure why this isn't done with .get() - maybe _attrs isn't a dict.
# Strong incentive to use explicit and convenient exception catching here.
    def getNamedItem(self, name):
        return self._attrs[name] except KeyError: None

# Lib/xml/etree/ElementPath.py:288:
def find(elem, path, namespaces=None):
    try:
        return next(iterfind(elem, path, namespaces))
    except StopIteration:
        return None
# Becomes:
def find(elem, path, namespaces=None):
    return next(iterfind(elem, path, namespaces)) except StopIteration: None

# Lib/tkinter/__init__.py:1182:
        def getint_event(s):
            """Tk changed behavior in 8.4.2, returning "??" rather more often."""
            try:
                return int(s)
            except ValueError:
                return s
# Becomes:
        def getint_event(s):
            """Tk changed behavior in 8.4.2, returning "??" rather more often."""
            return int(s) except ValueError: s

# ---------------------

# Lib/ipaddress.py:343:
            try:
                ips.append(ip.ip)
            except AttributeError:
                ips.append(ip.network_address)
# Becomes:
            ips.append(ip.ip except AttributeError: ip.network_address)
# This narrows the scope of exception catching; an AttributeError raised
# during the first append() will now not cause the second to be performed.
# As a semantic change, this should NOT be done mechanically; but it shows
# an additional advantage of the proposal. The expression form is nearly
# equivalent to this:
            try:
                _ = ip.ip
            except AttributeError:
                _ = ip.network_address
            ips.append(_)
# The reduction of scope should be an improvement. There are many cases
# where it could be applied. Look with intelligence at these; they are
# semantic changes, and meant to be indicative rather than clear-cut. I
# may have picked up some that shouldn't be touched.

# Lib/imghdr.py:148:
            try:
                print(what(filename))
            except OSError:
                print('*** not found ***')
# Becomes:
            print(what(filename) except OSError: '*** not found ***')

# Lib/tempfile.py:130:
    try:
        dirlist.append(_os.getcwd())
    except (AttributeError, OSError):
        dirlist.append(_os.curdir)
# Becomes:
    dirlist.append(_os.getcwd() except (AttributeError, OSError): _os.curdir)

# Lib/difflib.py:1452:
                try:
                    lines.append(next(diff_lines_iterator))
                except StopIteration:
                    lines.append('X')
# Becomes:
                lines.append(next(diff_lines_iterator) except StopIteration: 'X')

# Lib/asyncore.py:264:
            try:
                status.append('%s:%d' % self.addr)
            except TypeError:
                status.append(repr(self.addr))
# Becomes:
            status.append('%s:%d' % self.addr except TypeError: repr(self.addr))


# -----------------------------

# More complicated/messy examples follow. Not all of them are indented/wrapped
# ideally; in fact, some of the above are a bit long, too, so they might need
# to be wrapped.

# Lib/unittest/mock.py:735:
            try:
                return name, sig.bind(*args, **kwargs)
            except TypeError as e:
                return e.with_traceback(None)
# Could become:
            return ((name, sig.bind(*args, **kwargs))
                except TypeError as e: e.with_traceback(None))
# Notable because it actually uses 'as'.

# Lib/mailbox.py:1669:
        try:
            self.replace_header('Status', status_flags)
        except KeyError:
            self.add_header('Status', status_flags)
# Could become:
        (self.replace_header except KeyError: self.add_header)('Status', status_flags)
# This narrows the scope of the except clause, but at the expense of
# readability. Probably not worth it, except that it's done twice, so
# possibly it'd be worth capturing the function into a local name.
# Note that I'm not actually sure of the intended semantics here. Is
# "self.replace_header" going to raise KeyError, or is it the call to
# that function that might raise? If the latter, don't change anything.

# Lib/netrc.py:94
                            try:
                                fowner = pwd.getpwuid(prop.st_uid)[0]
                            except KeyError:
                                fowner = 'uid %s' % prop.st_uid
                            try:
                                user = pwd.getpwuid(os.getuid())[0]
                            except KeyError:
                                user = 'uid %s' % os.getuid()
                            raise NetrcParseError(
                                ("~/.netrc file owner (%s) does not match"
                                 " current user (%s)") % (fowner, user),
                                file, lexer.lineno)
# Seems to be begging for a helper function, but could become:
                            raise NetrcParseError(
                                ("~/.netrc file owner (%s) does not match"
                                 " current user (%s)") %
                                    ((pwd.getpwuid(prop.st_uid)[0]
                                        except KeyError: 'uid %s' % prop.st_uid),
                                    (pwd.getpwuid(os.getuid())[0]
                                        except KeyError: 'uid %s' % os.getuid()),
                                file, lexer.lineno)

# Lib/email/message.py:261:
                    try:
                        payload = bpayload.decode(self.get_param('charset', 'ascii'), 'replace')
                    except LookupError:
                        payload = bpayload.decode('ascii', 'replace')
# Could become:
                    payload = (bpayload.decode(self.get_param('charset', 'ascii'), 'replace')
                        except LookupError: bpayload.decode('ascii', 'replace'))
# But possibly (this is a semantic change, not sure if it's correct):
                    payload = bpayload.decode(
                        (self.get_param('charset', 'ascii') except LookupError: 'ascii'),
                        'replace')

# Lib/http/client.py:983:
                    try:
                        netloc_enc = netloc.encode("ascii")
                    except UnicodeEncodeError:
                        netloc_enc = netloc.encode("idna")
                    self.putheader('Host', netloc_enc)
# Could become:
                    self.putheader('Host',
                        netloc.encode("ascii") except UnicodeEncodeError: netloc.encode("idna")
                    )

# Lib/functools.py:681:
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            try:
                impl = registry[cls]
            except KeyError:
                impl = _find_impl(cls, registry)
            dispatch_cache[cls] = impl
        return impl
# Could become:
        try:
            impl = dispatch_cache[cls]
        except KeyError:
            impl = dispatch_cache[cls] = registry[cls] except KeyError: _find_impl(cls, registry)
        return impl
# This is a somewhat common structure: look something up in a cache; if not found, calculate it and
# cache it. It can't be easily improved by this new syntax.


# Lib/idlelib/CallTips.py:95:
        try:
            rpcclt = self.editwin.flist.pyshell.interp.rpcclt
        except AttributeError:
            rpcclt = None
# Becomes:
        rpcclt = self.editwin.flist.pyshell.interp.rpcclt except AttributeError: None
# Notable because that's one long chain of potential AttributeErrors, all covered. :)

# Lib/imaplib.py:568:
        try: typ, dat = self._simple_command('LOGOUT')
        except: typ, dat = 'NO', ['%s: %s' % sys.exc_info()[:2]]
# Becomes:
        typ, dat = self._simple_command('LOGOUT') except: ('NO', ['%s: %s' % sys.exc_info()[:2]])
# Or maybe:
        typ, dat = (self._simple_command('LOGOUT')
            except BaseException as e: ('NO', '%s: %s' % (type(e), e)))
# Or some other variation.

# Lib/asyncore.py:482:
        try:
            self_repr = repr(self)
        except:
            self_repr = '<__repr__(self) failed for object at %0x>' % id(self)

        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                self_repr,
                t,
                v,
                tbinfo
                ),
            'error'
            )
# Becomes:
        self.log_info(
            'uncaptured python exception, closing channel %s (%s:%s %s)' % (
                (repr(self) except: '<__repr__(self) failed for object at %0x>' % id(self)),
                t,
                v,
                tbinfo
                ),
            'error'
            )

# Tools/unicode/comparecodecs.py:19:
        try:
            c1 = u.encode(encoding1)
        except UnicodeError as reason:
            c1 = '<undefined>'
        try:
            c2 = u.encode(encoding2)
        except UnicodeError as reason:
            c2 = '<undefined>'
# Becomes:
        c1 = u.encode(encoding1) except UnicodeError: '<undefined>'
        c2 = u.encode(encoding2) except UnicodeError: '<undefined>'
# Again, it's easier to see the similarities and differences now.

# Doc/tools/sphinxext/c_annotations.py:52: 
                try:
                    entry = d[function]
                except KeyError:
                    entry = d[function] = RCEntry(function)
# This is a *false positive*. Just to show how easy it is to confuse things :)

# Lib/lib2to3/pgen2/driver.py:124:
            try:
                g.dump(gp)
            except OSError as e:
                logger.info("Writing failed:"+str(e))
# Technically, this could become:
            g.dump(gp) except OSError as e: logger.info("Writing failed:"+str(e))
# However, this is illogical use of the feature and should be discouraged.
