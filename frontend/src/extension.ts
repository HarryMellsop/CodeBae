// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import axios from 'axios';
import * as vscode from 'vscode';

/// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "codebae" is now active!');
	
	// Registering autocomplete item
	const provider1 = vscode.languages.registerCompletionItemProvider('python', {
		async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext) {

			const beforeCursor = document.getText(new vscode.Range(new vscode.Position(0,0), position));
			const afterCursor = document.getText(new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end));
			const docText : string = beforeCursor + "<cursor>" + afterCursor;
			let message : string = "";

			await axios.post('54.193.42.230:8080/predict', {current_file: docText}).then(response => {
				console.log(response.data);
				message = response.data;
			});

			const messageCompletion = new vscode.CompletionItem("H" + message);

			return [
				messageCompletion
			];
		}
	});
}

// this method is called when your extension is deactivated
export function deactivate() {}
