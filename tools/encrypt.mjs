// Шифрует src/** в enc/ паролем из .password: PBKDF2-SHA256 -> AES-256-GCM.
// Имя файла в enc = хеш пути, чтобы по репозиторию не читались названия проектов.
// Запуск: node tools/encrypt.mjs
import { createHash, pbkdf2Sync, randomBytes, createCipheriv } from "node:crypto";
import { readFileSync, writeFileSync, readdirSync, statSync, mkdirSync, rmSync } from "node:fs";
import { join, relative, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const ITER = 250000;
const pass = readFileSync(join(root, ".password"), "utf8").trim();
// соль постоянная: иначе после каждой выкладки сохранённый в браузере ключ перестаёт подходить и пароль спрашивают заново
let salt;
try { salt = Buffer.from(JSON.parse(readFileSync(join(root, "enc", "meta.json"), "utf8")).salt, "base64"); }
catch { salt = randomBytes(16); }
const key = pbkdf2Sync(pass, salt, ITER, 32, "sha256");

function seal(buf) {
  const iv = randomBytes(12), c = createCipheriv("aes-256-gcm", key, iv);
  return Buffer.concat([iv, c.update(buf), c.final(), c.getAuthTag()]);
}
const nameOf = p => createHash("sha256").update(salt).update(p).digest("hex").slice(0, 24);
const walk = d => readdirSync(d).flatMap(f => statSync(join(d, f)).isDirectory() ? walk(join(d, f)) : [join(d, f)]);

const out = join(root, "enc");
rmSync(out, { recursive: true, force: true });
mkdirSync(out);
const files = walk(join(root, "src"));
for (const f of files) {
  const p = relative(join(root, "src"), f).split("\\").join("/");
  writeFileSync(join(out, nameOf(p)), seal(readFileSync(f)));
}
writeFileSync(join(out, "meta.json"), JSON.stringify({
  salt: salt.toString("base64"), iter: ITER, check: seal(Buffer.from("ok")).toString("base64"),
}));
console.log("encrypted:", files.length);
