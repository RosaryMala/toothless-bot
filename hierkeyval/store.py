import io
import json

"""
DO NOT edit objects retrieved
Alternatively, call flush() to ensure changes persisted

The improved version should probably only support custom HDict and HList
objects to prevent this kind of bug
"""
class HierarchicalStore:
    sglobal = {}
    sserver = {}
    schannel = {}
    filename = None
    fileobj = None

    def __init__(self, filename_or_obj):
        if isinstance(filename_or_obj, io.StringIO):
            self.fileobj = filename_or_obj
        elif isinstance(filename_or_obj, str):
            self.filename = filename_or_obj
            # Also attempt to load from file
            try:
                with open(self.filename, 'r') as f:
                    d = json.load(f)
                self.sglobal, self.sserver, self.schannel = d
                if not isinstance(self.sglobal, dict) \
                        or not isinstance(self.sserver, dict) \
                        or not isinstance(self.schannel, dict):
                    # if any of the data is not the right type, reset
                    self.sglobal, self.sserver, self.schannel = {}, {}, {}
            # well, we tried
            except FileNotFoundError:
                pass
            except json.decoder.JSONDecodeError:
                pass
            except TypeError:
                pass  # obj is not a list
            except ValueError:
                pass  # obj has too many/too few elements
        else:
            raise ValueError('filename_or_obj should be a filename or fileobj')
        self.dicts = [self.sglobal, self.sserver, self.schannel]

    def flush(self):
        if self.filename is None:
            # It's a StringIO obj, truncate
            self.fileobj.truncate(0)
            self.fileobj.seek(0)
            f = self.fileobj
        else:
            f = open(self.filename, 'w')
        json.dump(self.dicts, f)

    def has_key(self, namespace, mask, key):
        try:
            self.get_val(namespace, mask, key)
            return True
        except KeyError:
            return False

    def has_namespace(self, namespace, mask):
        gsc = [x != '-' for x in mask]
        for i in range(2, -1, -1):
            if gsc[i]:
                if namespace in self.dicts[i]:
                    return True
        return False

    """
    Mask is format "gsc", where a - means skip that level.
    So, to only access global, do "g--", to access just global and channel
    do "g-c", and so on.

    :param namespace: Since HStore is by plugin, specify namespace
    :param mask: String mask for retrieving keys.
    :param key: The key to get the value for.
    """
    def get_val(self, namespace, mask, key):
        if len(mask) != 3:
            raise ValueError('Mask must be len 3')
        gsc = [x != '-' for x in mask]
        # iterate in reverse order
        for i in range(2, -1, -1):
            if gsc[i]:
                try:
                    return self.dicts[i][namespace][key]
                except KeyError:
                    pass
        raise KeyError(f'Could not find {key} in namespace {namespace}.')

    """
    Set a value.

    :param namespace: Namespace
    :param level: One of 'g', 's', or 'c', the level to store at
    :param key: The key to store at
    :param val: The value to store
    """
    def set_val(self, namespace, level, key, val):
        if level == 'g':
            d = self.sglobal
        elif level == 's':
            d = self.sserver
        elif level == 'c':
            d = self.schannel
        if namespace not in d:
            d[namespace] = {}
        d[namespace][key] = val
        self.flush()


DEFAULT = HierarchicalStore('default.hkv')

def get_default():
    return DEFAULT