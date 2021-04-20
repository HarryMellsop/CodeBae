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

	// TODO: Change this to be whatever message we get from the backend
	var message = "Hello World from Codebae";
	
	// Registering autocomplete item
	const provider1 = vscode.languages.registerCompletionItemProvider('python', {
		provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext) {
			
			const messageCompletion = new vscode.CompletionItem("Hello World");
			const messageCompletion2 = new vscode.CompletionItem("HI Josh");

			//make get req to httpbin which just reflects the data
			axios.get('https://httpbin.org/').then(response => {
				console.log(response.data);
			});

			return [
				messageCompletion,
				messageCompletion2
			];
		}
	});
}

// this method is called when your extension is deactivated
export function deactivate() {}
