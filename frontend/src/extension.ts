/* eslint-disable @typescript-eslint/naming-convention */
import * as vscode from 'vscode';
import { URLSearchParams } from 'url';
import axios from 'axios';

let serverAddr: string = 'http://18.116.74.78:8080';
let sessionExpireTime = 3600000;

var sessionID: string;
var sessionTimeout: NodeJS.Timeout;


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



	authenticateSession();

	context.subscriptions.push(vscode.commands.registerCommand('codeBae.authenticate', authenticateSession));

	// Registering autocomplete item
	const provider1 = registerPredictor();
}

function registerPredictor() {
	vscode.languages.registerCompletionItemProvider('python', {
		async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext) {
			if (sessionID) {
				// Get text in current document and place current cursor position in as <cursor>
				const beforeCursor = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
				const afterCursor = document.getText(new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end));
				const docText: string = beforeCursor + "<cursor>" + afterCursor;
				let message: string = "";

				// Create properly formatted body of POST request
				let params = new URLSearchParams();
				params.append('current_file', docText);

				// Send POST request to backend
				await axios.post(serverAddr + '/predict', params, {
					headers: {
						'Content-Type': 'application/x-www-form-urlencoded',
						'Session-ID': sessionID
					}
				})
					.then(response => {
						console.log(response.data);
						// If session ID is invalid, attempt to re-authenticate session
						if (response.data.code === 403) {
							sessionID = '';
							authenticateSession();
							// TO-DO: Maybe we need to retry the suggestions after this? Might end in a recursive loop though...
						} else {
							message = response.data;	
						}
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
				
				if (message) {
					return [ new vscode.CompletionItem(message) ];
				} else {
					return [];
				}
			}
		}
	});
}

async function authenticateSession() {
	// Create properly formatted body of POST request
	let params = new URLSearchParams();
	await axios.get(serverAddr + '/session', {
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
			'API-Key': vscode.workspace.getConfiguration('codeBae').get('apiKey')
		}
	})
		.then(response => {

			if (response.data.code === 403) {
				vscode.window.showInformationMessage('CodeBae: Your API key is invalid. Please reconfigure it in settings.');
				console.log(response.data.description);
			} else {
				console.log("Session authenticated. Session ID: " + response.data);
				sessionID = response.data;				
				
				// Set timeout to re-authenticate after certain time, ensure only one timeout is running
				if (sessionTimeout) {
					clearTimeout(sessionTimeout);
				}
				sessionTimeout = setTimeout(authenticateSession, sessionExpireTime);
				
			}

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
}

// this method is called when the extension is deactivated
export function deactivate() { }
