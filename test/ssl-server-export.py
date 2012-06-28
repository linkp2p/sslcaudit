import M2Crypto
import socket

CERTFILE = "certs/www.example.com-cert.pem"
KEYFILE = "certs/www.example.com-key.pem"
DHFILE = "../sslcaudit/files/dh512.pem"  # openssl dhparam -check -text -5 512 -out dh512.pem
RSAFILE = "../sslcaudit/files/rsa512.pem" # openssl genrsa -out rsa512.pem 512
PROTOCOL = "sslv3"
HOST = "0.0.0.0"
PORT = 4433

def main():
    print "[i] Initializing context ..."
    ctx = M2Crypto.SSL.Context(protocol=PROTOCOL, weak_crypto=True)
    ctx.load_cert_chain(certchainfile=CERTFILE, keyfile=KEYFILE)
    ctx.set_options(M2Crypto.m2.SSL_OP_ALL)
    ctx.set_tmp_rsa(M2Crypto.RSA.load_key(RSAFILE))     # e.g. openssl s_client -connect localhost:4433 -cipher EXP-RC4-MD5  <- won't work without RSA params (EXP-RC4-MD5 SSLv3 Kx=RSA(512) Au=RSA Enc=RC4(40) Mac=MD5 export)
    ctx.set_tmp_dh(DHFILE)                              # e.g. openssl s_client -connect localhost:4433 -cipher EXP-EDH-RSA-DES-CBC-SHA  <- won't work without DH params (EXP-EDH-RSA-DES-CBC-SHA SSLv3 Kx=DH(512) Au=RSA Enc=DES(40) Mac=SHA1 export)
    # still problematic: openssl s_client -connect localhost:4433 -cipher EXP-EDH-DSS-DES-CBC-SHA (EXP-EDH-DSS-DES-CBC-SHA SSLv3 Kx=DH(512) Au=DSS Enc=DES(40) Mac=SHA1 export)
    ctx.set_cipher_list("ALL")

    print "[i] Initializing socket ..."
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(1)
    conn, addr = sock.accept()

    print "[i] SSL handshake ..."
    ssl_conn = M2Crypto.SSL.Connection(ctx=ctx, sock=conn)
    ssl_conn.setup_ssl()
    try:
        ssl_conn_res = ssl_conn.accept_ssl()
    except Exception, ex:
        print "[x] SSL connection failed: '%s'" % str(ex)
    else:
        if ssl_conn_res == 1:
            print "[i] SSL connection accepted"
        else:
            print "[x] SSL handshake failed: '%s'" % ssl_conn.ssl_get_error(ssl_conn_res)

if __name__ == "__main__":
    main()
