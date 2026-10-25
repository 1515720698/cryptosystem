// Node.js >= 18. Set OPENSSL_BIN and CC if they are not on PATH.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const logsDir = path.join(root, 'evidence');
fs.mkdirSync(logsDir, {recursive:true});
const work = fs.mkdtempSync(path.join(os.tmpdir(), 'week4-sm2-'));
const openssl = process.env.OPENSSL_BIN || 'openssl';
const cc = process.env.CC || 'gcc';
const lines = ['第四周实践记录（由 AI 助手在本地执行，非学生手动操作记录）',
  `Platform: ${process.platform} ${process.arch}`, ''];
function run(exe, args, expected = 0) {
  lines.push(`$ ${path.basename(exe)} ${args.map(a => a.includes(' ') ? JSON.stringify(a) : a).join(' ')}`);
  const r = spawnSync(exe, args, {cwd:work, encoding:'utf8', env:process.env});
  if (r.error) throw r.error;
  if (r.stdout.trim()) lines.push(r.stdout.trim());
  if (r.stderr.trim()) lines.push(r.stderr.trim());
  lines.push(`[exit=${r.status}]`, '');
  if (expected === 'failure' ? r.status === 0 : r.status !== expected)
    throw Error(`Unexpected exit code ${r.status}: ${args.join(' ')}`);
  return r.stdout;
}
function check(name, ok) {
  lines.push(`${ok ? 'PASS' : 'FAIL'}: ${name}`);
  if (!ok) throw Error(name);
}
try {
  run(openssl, ['version']);
  const msg = Buffer.from('Week4 SM2: 20241328 Cai Maojun\n', 'utf8');
  fs.writeFileSync(path.join(work,'message.txt'), msg);
  run(openssl, ['genpkey','-algorithm','SM2','-out','private.pem']);
  run(openssl, ['pkey','-in','private.pem','-pubout','-out','public.pem']);
  for (const out of ['cipher1.der','cipher2.der'])
    run(openssl, ['pkeyutl','-encrypt','-pubin','-inkey','public.pem','-in','message.txt','-out',out]);
  run(openssl, ['pkeyutl','-decrypt','-inkey','private.pem','-in','cipher1.der','-out','recovered.txt']);
  check('SM2 encrypt/decrypt restores exact bytes', fs.readFileSync(path.join(work,'recovered.txt')).equals(msg));
  const cipher = fs.readFileSync(path.join(work,'cipher1.der'));
  check('Two encryptions of the same message produce different ciphertexts',
    !cipher.equals(fs.readFileSync(path.join(work,'cipher2.der'))));
  run(openssl, ['asn1parse','-inform','DER','-in','cipher1.der']);
  // Flip the last ciphertext octet: DER structure is unchanged, but C3 must reject it.
  const bad = Buffer.from(cipher); bad[bad.length - 1] ^= 1;
  fs.writeFileSync(path.join(work,'tampered.der'), bad);
  run(openssl, ['pkeyutl','-decrypt','-inkey','private.pem','-in','tampered.der','-out','rejected.txt'], 'failure');
  check('Tampered ciphertext is rejected', true);
  run(openssl, ['dgst','-sm3','-sign','private.pem','-sigopt','distid:20241328','-out','signature.der','message.txt']);
  const verify = (id, file, expected = 0) => run(openssl,
    ['dgst','-sm3','-verify','public.pem','-sigopt',`distid:${id}`,'-signature','signature.der',file], expected);
  verify('20241328','message.txt');
  verify('wrong-id','message.txt','failure');
  verify('20241328','message.txt');
  fs.writeFileSync(path.join(work,'changed.txt'), Buffer.from('Week4 SM2: message changed\n'));
  verify('20241328','changed.txt','failure');
  lines.push('PASS: Correct ID verifies; mismatched ID fails; restoring ID verifies; modified message fails.', '');
  run(cc, ['--version']);
  const exe = path.join(work, process.platform === 'win32' ? 'struct_demo.exe' : 'struct_demo');
  fs.copyFileSync(path.join(root,'code','struct_demo.c'), path.join(work,'struct_demo.c'));
  run(cc, ['-std=c11','-Wall','-Wextra','-Werror','struct_demo.c','-o',exe]);
  run(exe, []);
  lines.push('ALL CHECKS PASSED');
} finally {
  fs.writeFileSync(path.join(logsDir,'experiment-log.txt'),lines.join('\n') + '\n','utf8');
  fs.rmSync(work, {recursive:true, force:true});
  console.log(lines.join('\n'));
}
