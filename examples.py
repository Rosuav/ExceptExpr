# File names and line numbers are relative to the CPython source tree as of
# early Feb 2014.

# First off, there are a huge number like this:

# Lib/pdb.py:803:
        try:
            cond = args[1]
        except IndexError:
            cond = None
# Becomes:
        cond = args[1] except IndexError: None

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

# Lib/tkinter/filedialog.py:210:
            try:
                pwd = os.getcwd()
            except OSError:
                pwd = None
# Becomes:
            pwd = os.getcwd() except OSError: None

# Lib/tkinter/__init__.py:1222:
        try:
            e.widget = self._nametowidget(W)
        except KeyError:
            e.widget = W
# Becomes:
        e.widget = self._nametowidget(W) except KeyError: W

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

# Lib/lib2to3/pgen2/tokenize.py:370:
        try:
            line = readline()
        except StopIteration:
            line = ''
# Becomes:
        line = readline() except StopIteration: ''

# Lib/copy.py:79:
    try:
        issc = issubclass(cls, type)
    except TypeError: # cls is not a class
        issc = False
# Becomes:
    issc = issubclass(cls, type) except TypeError: False
# (Note that ibid line 157 has almost the same construct but defaulting to 0.)

# Lib/sysconfig.py:529:
        try:
            _CONFIG_VARS['abiflags'] = sys.abiflags
        except AttributeError:
            # sys.abiflags may not be defined on all platforms.
            _CONFIG_VARS['abiflags'] = ''
# Becomes:
        # sys.abiflags may not be defined on all platforms.
        _CONFIG_VARS['abiflags'] = sys.abiflags except AttributeError: ''

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

# -----------------------------

# More complicated/messy examples follow. Not all of them are indented/wrapped
# ideally; in fact, some of the above are a bit long, too, so they might need
# to be wrapped.

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

# Lib/tarfile.py:2198:
            try:
                g = grp.getgrnam(tarinfo.gname)[2]
            except KeyError:
                g = tarinfo.gid
            try:
                u = pwd.getpwnam(tarinfo.uname)[2]
            except KeyError:
                u = tarinfo.uid
# Becomes:
            g = grp.getgrnam(tarinfo.gname)[2] except KeyError: tarinfo.gid
            u = pwd.getpwnam(tarinfo.uname)[2] except KeyError: tarinfo.uid
# The parallel is far easier to see when it's in one line per value.

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
