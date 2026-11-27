// Шифрует src/data/pay.json паролем из .pay-password в pay.dat (PBKDF2-SHA256 -> AES-256-GCM).
// Запуск: node tools/pay_build.mjs
import { pbkdf2Sync, randomBytes, createCipheriv } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const ITER = 1500000;
const pass = readFileSync(join(root, ".pay-password"), "utf8").trim();
const salt = randomBytes(16), iv = randomBytes(12);
const key = pbkdf2Sync(pass, salt, ITER, 32, "sha256");
const c = createCipheriv("aes-256-gcm", key, iv);
const data = Buffer.concat([iv, c.update(readFileSync(join(root, "src/data/pay.json"))), c.final(), c.getAuthTag()]);
writeFileSync(join(root, "pay.dat"), JSON.stringify({ salt: salt.toString("base64"), iter: ITER, data: data.toString("base64") }));
console.log("pay.dat ok");
