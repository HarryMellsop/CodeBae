/* eslint-disable @typescript-eslint/naming-convention */
import * as vscode from 'vscode';
import { URLSearchParams } from 'url';
import axios from 'axios';

let serverAddr: string = 'http://18.116.74.78:8080';
let sessionExpireTime = 3600000;

var sessionID: string;
var sessionTimeout: NodeJS.Timeout;

// Reads the current working directory for .py files. Returns
// a JSON object of <string>relative path names to <string>file contents
async function readWorkingDirectory() {
	let fileDict : {[path: string]: string} = {};
	let workspacePath : string = "";
	if (vscode.workspace.workspaceFolders !== undefined) {
		workspacePath = vscode.workspace.workspaceFolders[0].uri.path;
	} else {
		console.log("No workspace found.");
		return {};
	}
	await vscode.workspace.findFiles('**/*.py').then(async (fileUris) => {
		for (let uri of fileUris) {
			await vscode.workspace.openTextDocument(uri).then((doc) => {
				let relativePath = uri.path.substr(workspacePath.length+1);
				let docText = doc.getText();
				fileDict[relativePath] = docText;
			});
		}
	});
	return fileDict;
}

// Reads workspace for .py files and sends them to backend /mass_upload endpoint
// in a JSON object formatted by [relative path : file contents]
async function massUpload() {
	let workspacename : string = vscode.workspace.name === undefined ? "" : vscode.workspace.name;
	if (workspacename === "") {
		console.log("No workspace detected.");
		return;
	}
	let files = await readWorkingDirectory();
	let jsonData: JSON = <JSON><unknown>{
		'workspace': <string>workspacename,
		'files': files
	};

	await axios.post(serverAddr + '/mass_upload', jsonData, {
		headers: {
			'Content-Type': 'application/json',
			'Session-ID': sessionID
		}
	})
		.then(response => {
			if (response.data.code === 403) {
				sessionID = '';
				authenticateSession();
				//TODO: maybe restart mass upload. the recursive loop issue still stands tho
			} else if (response.data.code >= 400) {
				console.log(response.data.code + ": " + response.data.description);
			} else {
				console.log("Mass upload of files successfully completed.");
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

/// this method is called when the extension is activated
export function activate(context: vscode.ExtensionContext) {
	console.log('CodeBae is now active!');
	authenticateSession().then(() => {
		massUpload();
	});

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
			//'API-Key': vscode.workspace.getConfiguration('codeBae').get('apiKey')
			'API-Key': '452af61abf65866b1b7b815f5306d6dd'
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
