'use strict';
const vscode = require('vscode');
const path = require('node:path');
const { execFile, spawn } = require('node:child_process');
const { promisify } = require('node:util');
const exec = promisify(execFile);

const WORDS = [
  'funcion', 'function', 'devolver', 'return', 'si', 'if', 'sino', 'else', 'elif',
  'mientras', 'while', 'para', 'for', 'en', 'in', 'verdadero', 'falso', 'true', 'false',
  'y', 'o', 'no', 'and', 'or', 'not', 'mostrar', 'print', 'entrada', 'input',
  'rango', 'range', 'longitud', 'len', 'incluir', 'include',
  'leer_archivo', 'read_file', 'escribir_archivo', 'write_file'
];

function settings(context, uri) {
  const config = vscode.workspace.getConfiguration('milan', uri);
  const custom = config.get('pythonPath');
  const candidates = custom ? [[custom]] : process.platform === 'win32'
    ? [['py', '-3'], ['python'], ['python3']] : [['python3'], ['python']];
  return {
    candidates,
    script: config.get('interpreterPath') || context.asAbsolutePath('interpreter/milan.py')
  };
}

async function findPython(candidates) {
  for (const [command, ...args] of candidates) {
    try {
      await exec(command, [...args, '-c', 'import sys; sys.exit(sys.version_info < (3, 10))'],
        { windowsHide: true, timeout: 5000 });
      return [command, args];
    } catch {
      // Try the next launcher if Python is unavailable or too old.
    }
  }
  throw new Error('Instala Python 3.10 o superior y reinicia VS Code.');
}

function activate(context) {
  const diagnostics = vscode.languages.createDiagnosticCollection('milan');
  const checks = new Map();
  const pythonCache = new Map();
  const python = candidates => {
    const key = JSON.stringify(candidates);
    if (!pythonCache.has(key)) {
      pythonCache.set(key, findPython(candidates).catch(error => {
        pythonCache.delete(key);
        throw error;
      }));
    }
    return pythonCache.get(key);
  };

  function cancel(uri) {
    const key = uri.toString();
    const check = checks.get(key);
    if (check) {
      checks.delete(key);
      clearTimeout(check.timer);
      clearTimeout(check.deadline);
      check.child?.kill();
    }
  }

  function update(doc) {
    if (doc.languageId !== 'milan') return;
    cancel(doc.uri);
    const key = doc.uri.toString();
    const check = {};
    checks.set(key, check);
    check.timer = setTimeout(async () => {
      const { candidates, script } = settings(context, doc.uri);
      try {
        const [command, prefix] = await python(candidates);
        if (checks.get(key) !== check) return;
        const args = [...prefix, '-X', 'utf8', script, '--check', '--json', '--stdin'];
        if (doc.uri.scheme === 'file') args.push('--', doc.uri.fsPath);
        const child = spawn(command, args, { windowsHide: true });
        check.child = child;
        check.deadline = setTimeout(() => {
          child.kill();
          report('Se agotó el tiempo para revisar el programa.');
        }, 5000);
        let stderr = '';
        child.stderr.setEncoding('utf8').on('data', data => {
          if (stderr.length < 65536) stderr += data;
        });
        child.stdout.resume();
        child.on('error', error => report(error.message));
        child.stdin.on('error', () => {});
        child.stdin.end(doc.getText());
        child.on('close', code => {
          if (checks.get(key) !== check) return;
          if (code === 0) return report();
          let result;
          try {
            result = JSON.parse(stderr);
          } catch {
            return report('No se pudo iniciar la revisión. Comprueba la instalación de Milán.');
          }
          const inModule = result.source && result.source !== '<milan>' &&
            path.relative(doc.uri.fsPath, result.source) !== '';
          report(inModule ? `${result.source} · línea ${result.line || '?'} · ${result.message}`
            : result.message, inModule ? 1 : result.line);
        });
      } catch (error) {
        report(error.message);
      }
    }, 250);

    function report(message, line) {
      if (checks.get(key) !== check) return;
      checks.delete(key);
      clearTimeout(check.deadline);
      const range = doc.lineAt(Math.min(doc.lineCount - 1, Math.max(0, (line || 1) - 1))).range;
      diagnostics.set(doc.uri, message ? [new vscode.Diagnostic(range, message)] : []);
    }
  }

  context.subscriptions.push(
    diagnostics,
    { dispose: () => vscode.workspace.textDocuments.forEach(doc => cancel(doc.uri)) },
    vscode.workspace.onDidOpenTextDocument(update),
    vscode.workspace.onDidChangeTextDocument(event => update(event.document)),
    vscode.workspace.onDidChangeConfiguration(event => {
      if (event.affectsConfiguration('milan')) vscode.workspace.textDocuments.forEach(update);
    }),
    vscode.workspace.onDidSaveTextDocument(doc => {
      if (doc.languageId === 'milan') vscode.workspace.textDocuments.forEach(update);
    }),
    vscode.workspace.onDidCloseTextDocument(doc => {
      cancel(doc.uri);
      diagnostics.delete(doc.uri);
    }),
    vscode.languages.registerCompletionItemProvider('milan', {
      provideCompletionItems() {
        return WORDS.map(word => new vscode.CompletionItem(word, vscode.CompletionItemKind.Keyword));
      }
    }),
    vscode.commands.registerCommand('milan.runFile', async () => {
      const doc = vscode.window.activeTextEditor?.document;
      if (!doc || doc.languageId !== 'milan' || doc.uri.scheme !== 'file') {
        vscode.window.showWarningMessage('Abre y guarda un archivo .milan local para ejecutarlo.');
        return;
      }
      if (!await doc.save()) return;
      const { candidates, script } = settings(context, doc.uri);
      try {
        const [command, prefix] = await python(candidates);
        const execution = new vscode.ProcessExecution(
          command, [...prefix, '-X', 'utf8', script, '--', doc.uri.fsPath],
          { cwd: path.dirname(doc.uri.fsPath) }
        );
        const task = new vscode.Task({ type: 'milan' }, vscode.TaskScope.Workspace,
          'Ejecutar archivo actual', 'Milán', execution, []);
        task.presentationOptions = { reveal: vscode.TaskRevealKind.Always, focus: true };
        await vscode.tasks.executeTask(task);
      } catch (error) {
        vscode.window.showErrorMessage(error.message);
      }
    })
  );
  vscode.workspace.textDocuments.forEach(update);
}

module.exports = { activate };
