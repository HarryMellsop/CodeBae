/* eslint-disable @typescript-eslint/naming-convention */
import * as vscode from 'vscode';
import { URLSearchParams } from 'url';
import axios from 'axios';

// All characters that would trigger autocomplete suggestion
const TRIGGER_CHARS = [	" ", ".", "(", ")", "{", "}", "[", "]", ",", ":", "'",
						'"', "=", "<", ">", "/", "\\", "+", "-", "|", "&", "*",
						"%", "=", "$", "#", "@", "!",];

let serverAddr: string = 'http://0.0.0.0:8080';	// Backend server address
let sessionExpireTime = 3600000; 				// Session expire time in seconds
let completionIcon = "🄲 ";						// Icon that will preceed all CodeBae suggestions

// Variables to maintain current session state
var sessionID: string;
var sessionTimeout: NodeJS.Timeout;



/**
 * 
 * This function is called by VSCode when the extension first activates on startup.
 * It is responsible for startup functionality (authenticate session, open landing page),
 * as well as registering extension contribution points.
 * 
 * @param  {vscode.ExtensionContext} context
 */
export function activate(context: vscode.ExtensionContext) {
	console.log('CodeBae is now active!');

	// Attempt to authenticate. If successful, attempt mass upload of workspace
	if (vscode.workspace.getConfiguration('codeBae').get('apiKey')) {
		authenticateSession().then(() => {
			if (vscode.workspace.getConfiguration('codeBae').get('automaticUpload')) {
				massUpload();
			} 
		});
	}
	
	// Track currently webview panel and attempt to launch launding page
	let currentPanel: vscode.WebviewPanel | undefined = undefined;
	setupLandingPage(currentPanel, context);

	// Register command to manually open landing page
	context.subscriptions.push(
		vscode.commands.registerCommand('codeBae.openLandingPage', () => {
			setupLandingPage(currentPanel, context);
		})
	);

	// Set up automatic mass upload upon save
	context.subscriptions.push(
		vscode.workspace.onDidSaveTextDocument((document: vscode.TextDocument) => {
			if (!vscode.workspace.getConfiguration('codeBae').get('automaticUpload')) {
				return;
			}
			// Check if workspace exists
			let workspacePath : string = "";
			if (vscode.workspace.workspaceFolders !== undefined) {
				workspacePath = vscode.workspace.workspaceFolders[0].uri.path;
			} else {
				console.log("Mass file upload upon save: no workspace found, aborting.");
				return;
			}
			// Check if file in workspace
			if (document.uri.path.startsWith(workspacePath)) {
				// Call mass upload
				massUpload();
			} else {
				console.log("Mass file upload upon save: saved file not in workspace, aborting.");
			}
		})
	);
	 
	// Register command to manually attempt authentication
	context.subscriptions.push(vscode.commands.registerCommand('codeBae.authenticate', authenticateSession));

	// Register CompletionItem provider
	const provider = registerPredictor();
}

/**
 * Registers the completion item provider. The function provideCompletionItem() will
 * be invoked by VSCode whenever a user is on a python file and typing any character
 * (alphabetical, or included in TRIGGER_CHARS). The function will send the current
 * contents of the file as well as the cursor position to the backend server and wait
 * for a response. It will return the predictions as completionItems from the response.
 */
function registerPredictor() {
	vscode.languages.registerCompletionItemProvider('python', {
		async provideCompletionItems(document: vscode.TextDocument, position: vscode.Position, token: vscode.CancellationToken, context: vscode.CompletionContext) {
			
			if (sessionID) {
				// Get text in current document and place current cursor position in as <cursor>
				const beforeCursor = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
				const afterCursor = document.getText(new vscode.Range(position, document.lineAt(document.lineCount - 1).range.end));
				const docText: string = beforeCursor + "<cursor>" + afterCursor;
				
				let predictions: string[] = [];

				// Create properly formatted body of POST request
				let params = new URLSearchParams();
				params.append('current_file', docText);
				console.log("Sending request for prediction");
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
						} else {
							predictions = response.data.predictions;	
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
				
				let completionItems : vscode.CompletionItem[] = [];

				// Loop over each prediction and configure a completionItem for it.
				for (var key in predictions) {
					var prediction = predictions[key];
					var index = parseInt(key);
					if (isNaN(index)) {
						continue;
					}

					// Add icon to completion item without affecting text matching
					let completionItem = new vscode.CompletionItem(completionIcon + prediction);
					completionItem.insertText = prediction;
					completionItem.filterText = prediction;
					
					// Modify sorting metric to prioritize codebae suggestions and preselect first one
					completionItem.sortText = String.fromCharCode(0) + String.fromCharCode(index);
					completionItem.preselect = index === 0;
					
					completionItem.detail = "CodeBae";
					completionItems.push(completionItem);
				}

				return completionItems;
			}
		}
	}, ... TRIGGER_CHARS);
}

/**
 * Attempts to authenticate session using the provided API Key. If successful, sessionID
 * will be a non-empty string. Otherwise, it will be empty.  Authentication is necessary
 * to send any other requests to backend as a session token is needed.
 * 
 * @param  {string|undefined=''} apiKey
 */
async function authenticateSession(apiKey : string | undefined = '') {
	if (!apiKey) {
		apiKey = vscode.workspace.getConfiguration('codeBae').get('apiKey');
	}

	// Create properly formatted body of POST request
	let params = new URLSearchParams();

	// Send authentication request.
	console.log("Making request to authenticate...");
	await axios.get(serverAddr + '/session', {
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
			'API-Key': apiKey
		}
	})
		.then(response => {
			if (response.data.code === 403) {
				vscode.window.showInformationMessage('CodeBae: Your API key is invalid.');
				console.log(response.data.description);
				sessionID = "";
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

/**
 * Reads the current working directory for .py files. Returns
 * a JSON object of <string>relative path names to <string>file contents
 */
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

/**
 *  Reads workspace for .py files and sends them to backend /mass_upload endpoint
 * in a JSON object formatted by [relative path : file contents]
 */
async function massUpload() {
	let workspacename : string = vscode.workspace.name === undefined ? "" : vscode.workspace.name;
	if (workspacename === "") {
		console.log("No workspace detected.");
		return;
	}

	console.log("Reading working directory.");

	let files = await readWorkingDirectory();
	let jsonData: JSON = <JSON><unknown>{
		'workspace': <string>workspacename,
		'files': files
	};

	console.log("Sending post request for mass upload.");
	await axios.post(serverAddr + '/mass_upload', jsonData, {
		headers: {
			'Content-Type': 'application/json',
			'Session-ID': sessionID
		},
		maxContentLength: Infinity,
    	maxBodyLength: Infinity
	})
		.then(response => {
			if (response.data.code === 403) {
				sessionID = '';
				authenticateSession();
			} else if (response.data.code >= 400) {
				console.log(response.data.code + ": " + response.data.description);
			} else {
				console.log("mass upload successfully completed.");
				vscode.window.showInformationMessage("Mass upload of files successfully completed.");
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

/**
 * Initializes the curre
 * 
 * @param  {vscode.WebviewPanel|undefined} currentPanel
 * @param  {vscode.ExtensionContext} context
 */
function setupLandingPage(currentPanel: vscode.WebviewPanel | undefined, context: vscode.ExtensionContext) {
	if (currentPanel) {
		// If we already have a panel, do nothing
		
	  } else {
		// Otherwise, create a new panel
		currentPanel = vscode.window.createWebviewPanel(
		  'codeBae',
		  'CodeBae',
		  vscode.ViewColumn.One,
		  {
			  enableScripts: true
		  }
		);

		// Initialize html and set tab icon
		currentPanel.webview.html = getWebviewContent(currentPanel.webview, context);
		currentPanel.iconPath = vscode.Uri.joinPath(context.extensionUri, "media", "icon.png");

		// If the panel was opened, post message to webview to reload configuration fields from VSCode settings
		currentPanel.onDidChangeViewState(
			e => {
				if (currentPanel) {
					currentPanel.webview.postMessage({ command: 'loadAPIKey', text: vscode.workspace.getConfiguration('codeBae').get('apiKey') });
					currentPanel.webview.postMessage({ command: 'updateAutomaticUpload', text: vscode.workspace.getConfiguration('codeBae').get('automaticUpload') });
				}
			},
			null,
			context.subscriptions
		);

		// Setup listener to update configurations if updated on webview
		currentPanel.webview.onDidReceiveMessage(
		  	message => {
				switch (message.command) {
			  		case 'saveAPIKey':
				  		vscode.workspace.getConfiguration('codeBae').update('apiKey', message.text, true);
				  		authenticateSession(message.text).then(() => {
							if (sessionID) {
								vscode.window.showInformationMessage("CodeBae: API Key successfully authenticated!");
							}
						});
						return;
					case 'uploadFiles':
						if (sessionID) {
							vscode.window.showInformationMessage("CodeBae: Uploading workspace files...");
							massUpload().then(() => {
								vscode.window.showInformationMessage("CodeBae: Done uploading workspace files!");
							});
						} else {
							vscode.window.showErrorMessage("CodeBae: You need to have an authenticated API Key before uploading.");
						}
						return;
					case 'onAutoUploadClick':
	  					let currentAutoUploadToggle : boolean | undefined = vscode.workspace.getConfiguration('codeBae').get('automaticUpload');
				  		vscode.workspace.getConfiguration('codeBae').update('automaticUpload', !currentAutoUploadToggle);
						return;
				}
		  },
		  undefined,
		  context.subscriptions
		);

		// Reset when the current panel is closed
		currentPanel.onDidDispose(
		  () => {
			currentPanel = undefined;
		  },
		  null,
		  context.subscriptions
		);
	  }

}
/**
 * Returns HTML content for the webview panel
 * 
 * @param  {vscode.Webview} webview
 * @param  {vscode.ExtensionContext} context
 */
function getWebviewContent(webview: vscode.Webview, context: vscode.ExtensionContext) {
	const styleMainUri = webview.asWebviewUri(
		vscode.Uri.joinPath(context.extensionUri, "media", "landingpage.css")
	  );
	  const styleVSCodeUri = webview.asWebviewUri(
		vscode.Uri.joinPath(context.extensionUri, "media", "vscode.css")
	  );
	  const logoUri = webview.asWebviewUri(
		vscode.Uri.joinPath(context.extensionUri, "media", "logo.png")
	  );
	  const iconUri = webview.asWebviewUri(
		vscode.Uri.joinPath(context.extensionUri, "media", "icon.png")
	  );

	  let apiKey = vscode.workspace.getConfiguration('codeBae').get('apiKey');
	  let automaticUploadEnabled = vscode.workspace.getConfiguration('codeBae').get('automaticUpload');
	return `<!DOCTYPE html>
  <html lang="en">
  <head>
	  <meta charset="UTF-8">
	  <meta name="viewport" content="width=device-width, initial-scale=1.0">
	  <title>Code Bae</title>
	  <link href="${styleVSCodeUri}" rel="stylesheet">
	  <link href="${styleMainUri}" rel="stylesheet">
	  <link href="${iconUri}" rel="icon" >
  </head>
  <body>
  <div class="main">
		<img src="${logoUri}" width="200" />
		<hr> 
		<div class="inner">
			<p>
				CodeBae provides intelligent auto-complete suggestions based on your existing codebase.
			</p>
		<div class="setting">
			<h3>API Key</h3>
			<p> The API Key to authenticate you to use CodeBae's features. </p>
			<div class="textentry">
				<input type="text" id="api-key" placeholder="Enter API Key"" name="api-key" value="${apiKey}">
				<button class="save" type="button" onclick="saveHandler()">Save</button>
			</div>
		</div>
		<div class="setting">
			<h3>Model Training</h3>
			<p>To have CodeBae provide you intelligent suggestions, you will need to upload your workspace files.
			<button class="train" type="button" onclick="uploadFiles()">Upload Workspace Files</button>
		</div>
		<div class="setting">
			<h3>Automatic Upload</h3>
			<input type="checkbox" id="automatic" onclick="onAutoUploadClick()">
				<p class="checkbox-description">Automatically upload workspace files as you work to have CodeBae continuously learn from your coding patterns.</p>
			</input>
	  	</div>
	</div>
	<script>
		const vscode = acquireVsCodeApi();
		document.getElementById("automatic").checked = ${automaticUploadEnabled}
		function saveHandler() {
			vscode.postMessage({
				command: 'saveAPIKey',
				text: document.getElementById("api-key").value
			})
		}
		function uploadFiles() {
			vscode.postMessage({
				command: 'uploadFiles'
			})
		}
		function onAutoUploadClick() {
			vscode.postMessage({
				command: 'onAutoUploadClick'
			})
		}

		window.addEventListener('message', event => {
            const message = event.data; // The JSON data our extension sent

            switch (message.command) {
                case 'loadAPIKey':
					document.getElementById("api-key").value = message.text;
				case 'updateAutomaticUpload':
					document.getElementById("automatic").checked = message.text
            }
        });
    </script>
	</body>
  </html>`;
  }

// this method is called when the extension is deactivated
export function deactivate() { }
