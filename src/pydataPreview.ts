import * as vscode from 'vscode';

import { Disposable } from './disposable';
import { getOption, getPyScriptsPath, OSUtils } from './utils';
import { Options, PythonShell } from 'python-shell';

type PreviewState = 'Disposed' | 'Visible' | 'Active';

enum FileType {
  NUMPY,
  PICKLE,
  PYTORCH,
  COMPRESSED_PICKLE
}


export class PyDataPreview extends Disposable {
  private _previewState: PreviewState = 'Visible';

  constructor(
    private readonly context: vscode.ExtensionContext,
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

    this.getWebviewContents(this.resource.path);
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

  public getWebviewContents(resourcePath: string) {
    var path = resourcePath;
    switch (OSUtils.isWindows()) {
      case true:
        path = path.slice(1,);
        console.log('[+] Windows -> cut path', path);
        break;
      default:
        console.log('[+] NOT Windows', path);
    }
    // extract the suffix
    var fileSuffix = path.toString().split('.').at(-1);
    if (fileSuffix === 'gz' || fileSuffix === 'tar') {
      const fileSuffix2 = path.toString().split('.').at(-2);
      fileSuffix = fileSuffix2 + '.' + fileSuffix;
    }
    const ft: FileType = PyDataPreview.suffixToType(fileSuffix as string);
    console.log('[*] File type is: ', ft);

    // Call python
    console.log('starting python....');
    var pythonPath = PythonShell.defaultPythonPath;
    console.log('default python path', pythonPath);
    const customPythonPath = getOption("vscode-pydata-viewer.pythonPath") as string;
    if (customPythonPath !== "default") {
      pythonPath = customPythonPath;
      console.log("[+] custom python path:", customPythonPath);
    }

    let options: Options = {
      mode: 'text',
      pythonPath: pythonPath,
      pythonOptions: ['-u'],
      encoding: 'utf8',
      // scriptPath: __dirname + '/pyscripts/',
      args: [ft.toString(), path]
    };

    const handle = this;
    var content: string = 'init';

    const workspace = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(resourcePath));
    var scriptPath = getOption("vscode-pydata-viewer.scriptPath") as string;
    if (scriptPath === "default") {
      scriptPath = getPyScriptsPath("read_files.py", this.context);
    } else {
      scriptPath = scriptPath.replace('${workspaceFolder}', workspace? workspace.uri.fsPath : "");
    }

    console.log("current deployed script", scriptPath);
    PythonShell.run(scriptPath,
      options, function (err, results) {
        if (err) { console.log(err); }
        // results is an array consisting of messages collected during execution
        console.log('results: %j', results);
        var r = results as Array<string>;
        // display the blank and line break with html labels
        for (var i=1; i<r.length; i++) {
          if (r[i].startsWith('<img')) {
            continue;
          }
          r[i] = r[i].replaceAll(" ", "&nbsp;");
        }
        content = r.join('<br>');
        const head = `<!DOCTYPE html>
        <html dir="ltr" mozdisallowselectionprint>
        <head>
        <meta charset="utf-8">
        </head>`;
        const tail = ['</html>'].join('\n');
        const output = head + `<body>              
        <div id="x" style='font-family: Menlo, Consolas, "Ubuntu Mono",
        "Roboto Mono", "DejaVu Sans Mono",
        monospace'>` + content + `</div></body>` + tail;
        console.log(output);
        handle.webviewEditor.webview.html = output;
        handle.update();
      });

    // Replace , with ,\n for reading
    // var re = /,/gi;
    // content = content.replace(re, `,\n`);
    // const head = `<!DOCTYPE html>
    // <html dir="ltr" mozdisallowselectionprint>
    // <head>
    // <meta charset="utf-8">
    // </head>`;
    // const tail = ['</html>'].join('\n');
    // const output =  head + `<body>              
    // <div id="x">` + content + `</div></body>` + tail;
    // console.log(output);
    // return output;
  }

  public static suffixToType(suffix: string) {
    switch (suffix) {
      case 'npz': return FileType.NUMPY;
      case 'npy': return FileType.NUMPY;
      case 'pkl': return FileType.PICKLE;
      case 'pck': return FileType.PICKLE;
      case 'pickle': return FileType.PICKLE;
      case 'pkl.gz': return FileType.COMPRESSED_PICKLE;
      case 'pth': return FileType.PYTORCH;
      case 'pt': return FileType.PYTORCH;
      case 'ckpt': return FileType.PYTORCH;
      default: return FileType.NUMPY;
    }
  }
}
