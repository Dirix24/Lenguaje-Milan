const vscode = require('vscode');
const path = require('path');
const fs = require('fs');
function activate(context) {
  context.subscriptions.push(vscode.commands.registerCommand('milan.runFile', async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor || editor.document.languageId !== 'milan') return;
    await editor.document.save();
    const config = vscode.workspace.getConfiguration('milan');
    const folder = vscode.workspace.getWorkspaceFolder(editor.document.uri);
    const script = config.get('interpreterPath') || (folder && path.join(folder.uri.fsPath, 'milan.py'));
    if (!script || !fs.existsSync(script)) {
      vscode.window.showErrorMessage('Configura milan.interpreterPath con la ruta a milan.py.');
      return;
    }
    const quote = s => JSON.stringify(s);
    const terminal = vscode.window.createTerminal('Milán');
    terminal.show();
    terminal.sendText([config.get('pythonPath', 'python3'), script, editor.document.uri.fsPath].map(quote).join(' '));
  }));
}
module.exports = { activate };
