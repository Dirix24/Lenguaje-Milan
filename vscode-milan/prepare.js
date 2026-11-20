'use strict';
const { copyFileSync, mkdirSync } = require('node:fs');
const path = require('node:path');

const target = path.join(__dirname, 'interpreter');
mkdirSync(target, { recursive: true });
copyFileSync(path.join(__dirname, '..', 'milan.py'), path.join(target, 'milan.py'));
copyFileSync(path.join(__dirname, '..', 'LICENSE'), path.join(__dirname, 'LICENSE'));
