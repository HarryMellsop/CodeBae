import * as vscode from 'vscode';
import { URLSearchParams } from 'url';
import axios from 'axios';

// Reads the current working directory for .py files
async function readWorkingDirectory() {
	await vscode.workspace.findFiles('**/*.py').then((fileUris) => {
		for (let uri of fileUris) {
			vscode.workspace.openTextDocument(uri).then((doc) => {
				console.log(doc.getText());
			});
		}
	});
}
/// this method is called when the extension is activated
export function activate(context: vscode.ExtensionContext) {
	console.log('CodeBae is now active!');
	
	// Registering autocomplete item
	const provider1 = vscode.languages.registerCompletionItemProvider('python', {
		async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext) {
			// Get text in current document and place current cursor position in as <cursor>
			const beforeCursor = document.getText(new vscode.Range(new vscode.Position(0,0), position));
			const afterCursor = document.getText(new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end));
			const docText : string = beforeCursor + "<cursor>" + afterCursor;
			let message : string = "";

			// Create properly formatted body of POST request
			let params = new URLSearchParams();
			params.append('current_file', docText);

			// Send POST request to backend
			await axios.post('http://18.116.74.78:8080/predict', params, {
				// Set Content-Type of request
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}})
				.then(response => {
					console.log(response.data);
					message = response.data;
				})
				.catch(err => {
					if (err.response) {
						console.log('RESPONSE ERR: ' + err.message);
					} else if (err.request) {
						console.log('REQUEST ERR: ' + err.message);
					} else {
						console.log('ERR: ' + err.message);
					}
				});
			const messageCompletion = new vscode.CompletionItem("H" + message);

			return [
				messageCompletion
			];
		}
	});
}

// this method is called when the extension is deactivated
export function deactivate() {}
