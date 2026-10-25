#!/usr/bin/env bash
# Linux / OpenSSL 3.x. Temporary keys are removed automatically.
set -euo pipefail
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"
openssl version
printf 'Week4 SM2: 20241328 Cai Maojun\n' > message.txt
openssl genpkey -algorithm SM2 -out private.pem
openssl pkey -in private.pem -pubout -out public.pem
openssl pkeyutl -encrypt -pubin -inkey public.pem -in message.txt -out cipher1.der
openssl pkeyutl -encrypt -pubin -inkey public.pem -in message.txt -out cipher2.der
openssl pkeyutl -decrypt -inkey private.pem -in cipher1.der -out recovered.txt
cmp message.txt recovered.txt && printf 'PASS: round trip\n'
if cmp -s cipher1.der cipher2.der; then
  printf 'Unexpected identical ciphertexts\n'; exit 1
fi
openssl asn1parse -inform DER -in cipher1.der
openssl dgst -sm3 -sign private.pem -sigopt distid:20241328 -out signature.der message.txt
openssl dgst -sm3 -verify public.pem -sigopt distid:20241328 -signature signature.der message.txt
if openssl dgst -sm3 -verify public.pem -sigopt distid:wrong-id -signature signature.der message.txt; then
  printf 'Unexpected verification success with wrong ID\n'; exit 1
fi
openssl dgst -sm3 -verify public.pem -sigopt distid:20241328 -signature signature.der message.txt
printf 'Changed message\n' > changed.txt
if openssl dgst -sm3 -verify public.pem -sigopt distid:20241328 -signature signature.der changed.txt; then
  printf 'Unexpected verification success with changed message\n'; exit 1
fi
printf 'PASS: all SM2 checks\n'
