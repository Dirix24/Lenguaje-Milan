'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { test } = require('node:test');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const script = path.join(root, 'vscode-milan', 'extension.js');

test('comprueba sin ejecutar y envía argumentos directos a la terminal', async t => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'Milán '));
  t.after(() => fs.rmSync(directory, { recursive: true, force: true }));
  const filename = path.join(directory, 'saludo $.milan');
  let source = 'mostrar("Milán")\nsi verdadero\nmostrar(1)';
  const doc = {
    uri: { scheme: 'file', fsPath: filename, toString: () => filename },
    languageId: 'milan',
    lineCount: 3,
    getText: () => source,
    lineAt: line => ({ range: { line } }),
    save: async () => true
  };

  let publish, onChange, run, task, completions;
  const diagnostic = () => new Promise(resolve => { publish = resolve; });
  const noOp = () => ({ dispose() {} });
  const vscode = {
    languages: {
      createDiagnosticCollection: () => ({ set: (_uri, values) => publish(values), delete() {} }),
      registerCompletionItemProvider: (_language, provider) => { completions = provider; }
    },
    workspace: {
      textDocuments: [doc],
      getConfiguration: () => ({ get: name => name === 'interpreterPath'
        ? path.join(root, 'milan.py') : '' }),
      onDidOpenTextDocument: noOp,
      onDidChangeTextDocument: fn => { onChange = fn; },
      onDidSaveTextDocument: noOp,
      onDidCloseTextDocument: noOp,
      onDidChangeConfiguration: noOp
    },
    commands: { registerCommand: (_id, fn) => { run = fn; } },
    window: {
      activeTextEditor: { document: doc },
      showErrorMessage: assert.fail
    },
    tasks: { executeTask: async value => { task = value; } },
    TaskScope: { Workspace: 2 },
    TaskRevealKind: { Always: 1 },
    Task: class { constructor(_definition, _scope, _name, _source, execution) { this.execution = execution; } },
    ProcessExecution: class { constructor(command, args, options) { Object.assign(this, {command, args, options}); } },
    Diagnostic: class { constructor(range, message) { Object.assign(this, {range, message}); } },
    CompletionItem: class { constructor(label) { this.label = label; } },
    CompletionItemKind: { Keyword: 13 }
  };
  const moduleObject = { exports: {} };
  vm.runInNewContext(fs.readFileSync(script, 'utf8'), {
    require: name => name === 'vscode' ? vscode : require(name),
    module: moduleObject, process, setTimeout, clearTimeout
  }, { filename: script });

  const first = diagnostic();
  moduleObject.exports.activate({ subscriptions: [] });
  const errors = await first;
  assert.equal(errors.length, 1);
  assert.equal(errors[0].range.line, 1);
  assert.match(errors[0].message, /abrir el bloque/);
  assert.ok(completions.provideCompletionItems().some(item => item.label === 'incluir'));

  source = 'entrada("Sin ejecutar")';
  const updated = diagnostic();
  onChange({ document: doc });
  assert.equal((await updated).length, 0);

  await run();
  assert.equal(task.execution.args.at(-1), filename);
  assert.equal(task.execution.args.at(-2), '--');
  assert.equal(task.execution.options.cwd, directory);
});
