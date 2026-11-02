"""Exercise OpenSSL C X509 APIs through explicit ctypes bindings (not C compilation)."""
import argparse
import ctypes as C
import os
from pathlib import Path
import ssl

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--libcrypto', default=r'C:\Program Files\Git\ucrt64\bin\libcrypto-3-x64.dll')
args = parser.parse_args()
directory = os.add_dll_directory(str(Path(args.libcrypto).parent))
lib = C.CDLL(args.libcrypto)
ptr, size, integer = C.c_void_p, C.c_size_t, C.c_int
def bind(name, restype, *types):
    f = getattr(lib, name)
    f.restype, f.argtypes = restype, list(types)
    return f
version = bind('OpenSSL_version', C.c_char_p, integer)
decode = bind('d2i_X509', ptr, C.POINTER(ptr), C.POINTER(ptr), C.c_long)
cert_free = bind('X509_free', None, ptr)
get_version = bind('X509_get_version', C.c_long, ptr)
get_serial = bind('X509_get_serialNumber', ptr, ptr)
as_integer = bind('ASN1_INTEGER_get', C.c_long, ptr)
get_subject = bind('X509_get_subject_name', ptr, ptr)
get_issuer = bind('X509_get_issuer_name', ptr, ptr)
name_line = bind('X509_NAME_oneline', ptr, ptr, ptr, integer)
store_new = bind('X509_STORE_new', ptr)
store_free = bind('X509_STORE_free', None, ptr)
add_cert = bind('X509_STORE_add_cert', integer, ptr, ptr)
ctx_new = bind('X509_STORE_CTX_new', ptr)
ctx_free = bind('X509_STORE_CTX_free', None, ptr)
ctx_init = bind('X509_STORE_CTX_init', integer, ptr, ptr, ptr, ptr)
verify = bind('X509_verify_cert', integer, ptr)
get_error = bind('X509_STORE_CTX_get_error', integer, ptr)
get_depth = bind('X509_STORE_CTX_get_error_depth', integer, ptr)
error_string = bind('X509_verify_cert_error_string', C.c_char_p, C.c_long)
get_param = bind('X509_STORE_CTX_get0_param', ptr, ptr)
set_host = bind('X509_VERIFY_PARAM_set1_host', integer, ptr, C.c_char_p, size)
set_purpose = bind('X509_VERIFY_PARAM_set_purpose', integer, ptr, integer)
stack_new = bind('OPENSSL_sk_new_null', ptr)
stack_push = bind('OPENSSL_sk_push', integer, ptr, ptr)
stack_free = bind('OPENSSL_sk_free', None, ptr)
def read_cert(name):
    der = ssl.PEM_cert_to_DER_cert((ROOT / 'evidence' / name).read_text(encoding='ascii'))
    buf = C.create_string_buffer(der)
    cursor = ptr(C.addressof(buf))
    cert = decode(None, C.byref(cursor), len(der))
    assert cert, name
    return cert
def name_string(name):
    buf = C.create_string_buffer(512)
    assert name_line(name, buf, len(buf))
    return buf.value.decode('utf-8')
lines = ['Library: ' + version(0).decode(), 'Binding: ctypes -> native OpenSSL C API']
root, intermediate, leaf = [read_cert(n) for n in ['root-cert.pem', 'intermediate-cert.pem', 'server-cert.pem']]
store, chain = store_new(), stack_new()
assert store and chain
try:
    assert add_cert(store, root) == 1
    assert stack_push(chain, intermediate) == 1
    lines += [f'X509 version raw={get_version(leaf)} (v3)', f'Serial={as_integer(get_serial(leaf))}', 'Subject=' + name_string(get_subject(leaf)), 'Issuer=' + name_string(get_issuer(leaf))]
    for label, use_chain, host, expected in [('complete chain', True, b'lab.example.test', 1), ('missing intermediate', False, b'lab.example.test', 0), ('wrong hostname', True, b'wrong.example.test', 0)]:
        ctx = ctx_new()
        assert ctx
        try:
            assert ctx_init(ctx, store, leaf, chain if use_chain else None) == 1
            param = get_param(ctx)
            assert set_host(param, host, len(host)) == 1
            assert set_purpose(param, 2) == 1  # X509_PURPOSE_SSL_SERVER
            ret = verify(ctx)
            code, depth = get_error(ctx), get_depth(ctx)
            lines.append(f'{label}: ret={ret}, error={code}, depth={depth}, detail={error_string(code).decode()}')
            assert ret == expected
        finally:
            ctx_free(ctx)
finally:
    stack_free(chain)  # only the stack; certificate ownership remains here
    store_free(store)
    for cert in [leaf, intermediate, root]:
        cert_free(cert)
    directory.close()
lines.append('ALL 3 API CHECKS PASSED; contexts, store, stack and certificates released.')
text = '\n'.join(lines) + '\n'
print(text)
(ROOT / 'evidence' / 'x509-api-log.txt').write_text(text, encoding='utf-8')
