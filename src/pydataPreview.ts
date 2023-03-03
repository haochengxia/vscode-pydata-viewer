import * as vscode from 'vscode';

import { Disposable } from './disposable';
import { getOption, OSUtils } from './utils';
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

  public getWebviewContents(resourcePath : string) {
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
    const ft : FileType = PyDataPreview.suffixToType(fileSuffix as string);
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
    
    let options : Options = {
        mode: 'text',
        pythonPath: pythonPath,
        pythonOptions: ['-u'],
        // scriptPath: __dirname + '/pyscripts/',
        args: [ft.toString(), path]
    };
    
    const handle = this;
    var content : string = 'init';
    PythonShell.runString(READ_FILES_SCRIPT, 
      options, function (err, results) {
        if (err) {console.log(err);}
        // results is an array consisting of messages collected during execution
        console.log('results: %j', results);
        var r = results as Array<string>;
        content = r.join('<br>');
        const head = `<!DOCTYPE html>
        <html dir="ltr" mozdisallowselectionprint>
        <head>
        <meta charset="utf-8">
        </head>`;
        const tail = ['</html>'].join('\n');
        const output =  head + `<body>              
        <div id="x">` + content + `</div></body>` + tail;
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

  public static suffixToType(suffix : string) {
    switch (suffix) {
        case 'npz': return FileType.NUMPY;
        case 'npy': return FileType.NUMPY;
        case 'pkl': return FileType.PICKLE;
        case 'pck': return FileType.PICKLE;
        case 'pickle': return FileType.PICKLE;
        case 'pth': return FileType.PYTORCH;
        case 'pt': return FileType.PYTORCH;
        default: return FileType.NUMPY;
    }
  }
}

const READ_FILES_SCRIPT =
`
import sys
file_type = int(sys.argv[1])
file_path = sys.argv[2]

from enum import Enum
class FileType(Enum):
    NUMPY = 0
    PICKLE = 1
    PYTORCH = 2

def print_ndarray(array):
    if not isinstance(array, np.ndarray):
        array = np.array(array)
    if array.dtype == np.dtype("O"):
        if not array.shape:
            array = array.item()
            if isinstance(array, dict):
                print("{")
                for k, v in array.items():
                    print("'<b><i>{}</i></b>':".format(k))
                    if isinstance(v, np.ndarray):
                        print("<b><i>shape: {}</i></b>".format(v.shape))
                    print("{},".format(v))
                print("}")
            else:
                print(array)
        else:
            if len(array) > 5:
                print("[")
                for item in array[:5]:
                    print_ndarray(item)
                    print(',')
                print("...,")
                print_ndarray(array[-1])
                print("]")
            else:
                for item in array:
                    print_ndarray(item)
    else:
        print("<b><i>shape: {}</i></b>".format(array.shape))
        print(array)

if file_type == FileType.NUMPY.value:
    # Solve numpy files .npy or .npz
    try:
        import numpy as np
        if file_path.endswith('npz'):
            content = np.load(file_path, allow_pickle=True)
            print('{')
            for f in content.files:
                print("'<b><i>{}</i></b>':".format(f))
                print_ndarray(content[f])
                # print(',')
            print('}')
        else:
            content = np.load(file_path, allow_pickle=True)
            print_ndarray(content)
    except Exception as e:
        print(e)
elif file_type == FileType.PICKLE.value:
    # Solve pickle files .pkl
    try:
        import pickle
        f = open(file_path, 'rb')
        content = pickle.load(f)
        print(content)
    except Exception as e:
        print(e)
elif file_type == FileType.PYTORCH.value:
    # Solve pytorch files .pth
    try:
        import torch
        content = torch.load(file_path)
        print(content)
    except Exception as e:
        print(e)
else:
    print('Unsupport file type.')
`;
