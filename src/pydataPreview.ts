import * as vscode from 'vscode';

import { Disposable } from './disposable';
import { OSUtils, getPythonPath, isLargerThanOne, toCLikeArray, toMultiDimArray, show2DArr, multiArrayToString, wrapWithSqBr } from './utils';
import {Options, PythonShell} from 'python-shell';

type PreviewState = 'Disposed' | 'Visible' | 'Active';

enum FileType {
    NUMPY,
    PICKLE,
    PYTORCH
}


export class PyDataPreview extends Disposable {
  private _previewState: PreviewState = 'Visible';

  constructor(
    private readonly extensionRoot: vscode.Uri,
    private readonly resource: vscode.Uri,
    private readonly webviewEditor: vscode.WebviewPanel
  ) {
    super();
    const resourceRoot = resource.with({
      path: resource.path.replace(/\/[^/]+?\.\w+$/, '/'),
    });

    webviewEditor.webview.options = {
      enableScripts: true,
      localResourceRoots: [resourceRoot, extensionRoot],
    };

    this._register(
      webviewEditor.webview.onDidReceiveMessage((message) => {
        switch (message.type) {
          case 'reopen-as-text': {
            vscode.commands.executeCommand(
              'vscode.openWith',
              resource,
              'default',
              webviewEditor.viewColumn
            );
            break;
          }
        }
      })
    );

    this._register(
      webviewEditor.onDidChangeViewState(() => {
        this.update();
      })
    );

    this._register(
      webviewEditor.onDidDispose(() => {
        this._previewState = 'Disposed';
      })
    );

    const watcher = this._register(
      vscode.workspace.createFileSystemWatcher(resource.fsPath)
    );
    this._register(
      watcher.onDidChange((e) => {
        if (e.toString() === this.resource.toString()) {
          this.reload();
        }
      })
    );
    this._register(
      watcher.onDidDelete((e) => {
        if (e.toString() === this.resource.toString()) {
          this.webviewEditor.dispose();
        }
      })
    );

    this.webviewEditor.webview.html = PyDataPreview.getWebviewContents(this.resource.path, false);
    this.update();
  }

  private reload(): void {
    if (this._previewState !== 'Disposed') {
      this.webviewEditor.webview.postMessage({ type: 'reload' });
    }
  }

  private update(): void {
    if (this._previewState === 'Disposed') {
      return;
    }

    if (this.webviewEditor.active) {
      this._previewState = 'Active';
      return;
    }
    this._previewState = 'Visible';
  }

  public static getWebviewContents(resourcePath : string, tableViewFlag : boolean, tableCss=''): string {
    var path = resourcePath;
    switch (OSUtils.isWindows()) {
      case true: 
        path = path.slice(1, );
        console.log('[+] Windows -> cut path', path);
        break;
      default:
        console.log('[+] NOT Windows', path);
    }
    // extract the suffix
    const fileSuffix = path.toString().split('.').at(-1);
    const ft : FileType = this.suffixToType(fileSuffix as string);

    const content = callPythonToRead(ft, path);

    // Introduce css file
    var resourceLink = '';
    if (tableCss !== '') {
      resourceLink = `<link rel="stylesheet" href="${tableCss}">`;
    }

    // Replace , with ,\n for reading
    // var re = /,/gi;
    // content = content.replace(re, `,\n`);
    const head = `<!DOCTYPE html>
    <html dir="ltr" mozdisallowselectionprint>
    <head>
    <meta charset="utf-8">
    ${resourceLink}
    </head>`;
    const tail = ['</html>'].join('\n');
    const output =  head + `<body>              
    <div id="x">` + content + `</div></body>` + tail;
    console.log(output);
    return output;
  }

  public static suffixToType(suffix : string) {
    switch (suffix) {
        case 'npz': return FileType.NUMPY;
        case 'npy': return FileType.NUMPY;
        case 'pkl': return FileType.PICKLE;
        case 'pth': return FileType.PYTORCH;
        default: return FileType.NUMPY;
    }
  }
}


async function callPythonToRead(fileType: FileType, filePath : string) : Promise<any> {
    const pythonPath = await getPythonPath();
    let options : Options = {
        mode: 'text',
        pythonPath: pythonPath,
        pythonOptions: ['-u'],
        scriptPath: './pyscripts',
        args: [fileType.toString(), filePath]
    };
    
    var content;

    PythonShell.run('read_files.py', options, function (err, results) {
        if (err) {throw err;}
        // results is an array consisting of messages collected during execution
        console.log('results: %j', results);
        content = results;
    });
    return content;
}