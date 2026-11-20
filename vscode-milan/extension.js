'use strict';
const vscode = require('vscode');
const path = require('path');
const fs = require('fs');

const WORDS = [
  'funcion', 'function', 'devolver', 'return', 'si', 'if',
  'sino', 'else', 'mientras', 'while', 'para', 'for',
  'en', 'in', 'verdadero', 'falso', 'true', 'false',
  'mostrar', 'print', 'range', 'len'
];

function diagnosticsFor(document) {
  const result = [];
  const stack = [];
  const pairs = { ')': '(', ']': '[', '}': '{' };
  const open = new Set(['(', '[', '{']);
  const source = document.getText();
  let quote = null, escaped = false, comment = false;
  for (let i = 0; i < source.length; i++) {
    const ch = source[i];
    if (ch === '\n') { comment = false; continue; }
    if (comment) continue;
    if (quote) {
      if (escaped) { escaped = false; continue; }
      if (ch === '\\') { escaped = true; continue; }
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === '#') { comment = true; continue; }
    if (ch === '"' || ch === "'") { quote = ch; continue; }
    if (open.has(ch)) stack.push({ ch, i });
    if (Object.prototype.hasOwnProperty.call(pairs, ch)) {
      const top = stack[stack.length - 1];
      if (!top || top.ch !== pairs[ch]) {
        const p = document.positionAt(i);
        result.push(new vscode.Diagnostic(new vscode.Range(p, p.translate(0, 1)), 'Cierre inesperado: ' + ch, vscode.DiagnosticSeverity.Error));
      } else stack.pop();
    }
  }
  for (const item of stack) {
    const p = document.positionAt(item.i);
    result.push(new vscode.Diagnostic(new vscode.Range(p, p.translate(0, 1)), 'Falta cerrar: ' + item.ch, vscode.DiagnosticSeverity.Error));
  }
  return result;
}

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection('milan');
  context.subscriptions.push(diagnostics);
  const update = doc => {
    if (doc.languageId === 'milan') diagnostics.set(doc.uri, diagnosticsFor(doc));
  };
  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(update),
    vscode.workspace.onDidChangeTextDocument(e => update(e.document)),
    vscode.workspace.onDidCloseTextDocument(doc => diagnostics.delete(doc.uri))
  );
  vscode.workspace.textDocuments.forEach(update);

  context.subscriptions.push(vscode.languages.registerCompletionItemProvider('milan', {
    provideCompletionItems() {
      return WORDS.map(word => new vscode.CompletionItem(word, vscode.CompletionItemKind.Keyword));
    }
  }));

  context.subscriptions.push(vscode.commands.registerCommand('milan.runFile', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'milan') {
      vscode.window.showWarningMessage('Abre un archivo .milan para ejecutarlo.');
      return;
    }
    if (editor.document.isUntitled) {
      vscode.window.showWarningMessage('Guarda el archivo .milan antes de ejecutarlo.');
      return;
    }
    if (!await editor.document.save()) return;
    const config = vscode.workspace.getConfiguration('milan', editor.document.uri);
    const folder = vscode.workspace.getWorkspaceFolder(editor.document.uri);
    const script = config.get('interpreterPath', '') || (folder && path.join(folder.uri.fsPath, 'milan.py'));
    if (!script || !fs.existsSync(script)) {
      vscode.window.showErrorMessage('No se encuentra milan.py. Configura milan.interpreterPath.');
      return;
    }
    const python = config.get('pythonPath', 'python3');
    // The configured interpreter command is treated as a single executable path.
    const quote = value => process.platform === 'win32'
      ? '"' + value.replace(/"/g, '""') + '"'
      : "'" + value.replace(/'/g, "'\\''") + "'";
    const terminal = vscode.window.createTerminal({ name: 'Milán', cwd: path.dirname(editor.document.uri.fsPath) });
    terminal.show();
    terminal.sendText([python, script, editor.document.uri.fsPath].map(quote).join(' '));
  }));
}

function deactivate() {}
module.exports = { activate, deactivate };
