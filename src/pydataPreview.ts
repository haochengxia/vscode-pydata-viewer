import * as vscode from 'vscode';
import * as fs from 'fs';

import { Disposable } from './disposable';
import { getOption, getPyScriptsPath, OSUtils } from './utils';
import { Options, PythonShell } from 'python-shell';
import { PythonInterpreterService } from './pythonInterpreter';
import { PythonPathResolutionResult, resolvePythonPathPriority } from './pythonPathResolution';

type PreviewState = 'Disposed' | 'Visible' | 'Active';

enum FileType {
  NUMPY,
  PICKLE,
  PYTORCH,
  COMPRESSED_PICKLE
}


export class PyDataPreview extends Disposable {
  private _previewState: PreviewState = 'Visible';
  private _isFullMode: boolean = false;
  private _loadRequestId: number = 0;

  public get resourceUri(): vscode.Uri {
    return this.resource;
  }

  constructor(
    private readonly context: vscode.ExtensionContext,
    private readonly extensionRoot: vscode.Uri,
    private readonly resource: vscode.Uri,
    private readonly webviewEditor: vscode.WebviewPanel,
    private readonly interpreterService: PythonInterpreterService
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

    void this.getWebviewContents(this.resource.path);
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

  public async getWebviewContents(resourcePath: string): Promise<void> {
    const requestId = ++this._loadRequestId;

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
    const workspace = vscode.workspace.getWorkspaceFolder(vscode.Uri.file(resourcePath));
    const workspacePath = workspace ? workspace.uri.fsPath : '';
    console.log('starting python....');

    const pythonResolution = await this.resolvePythonPath(this.resource, workspacePath);
    if (!pythonResolution.path) {
      this.renderSimpleMessage(
        `Error: Unable to resolve Python interpreter.<br><br>${pythonResolution.hint}`,
        'red'
      );
      return;
    }

    const pythonPath = pythonResolution.path;
    console.log(`[PyData Viewer] Using python (${pythonResolution.source}):`, pythonPath);

    if (this.shouldValidatePathExists(pythonPath) && !this.existsPath(pythonPath)) {
      this.renderSimpleMessage(
        `Error: Python path does not exist: ${pythonPath}<br><br>${pythonResolution.hint}`,
        'red'
      );
      return;
    }

    let options: Options = {
      mode: 'text',
      pythonPath: pythonPath,
      pythonOptions: ['-u'],
      encoding: 'utf8',
      // scriptPath: __dirname + '/pyscripts/',
      args: [ft.toString(), path, this._isFullMode ? 'full' : 'truncated']
    };

    const handle = this;
    var content: string = 'init';

    var scriptPath = getOption("vscode-pydata-viewer.scriptPath") as string;
    if (scriptPath === "default") {
      scriptPath = getPyScriptsPath("read_files.py", this.context);
    } else {
      scriptPath = scriptPath.replace('${workspaceFolder}', workspacePath);
    }

    console.log("current deployed script", scriptPath);
    console.log("Python options:", JSON.stringify(options));
    PythonShell.run(scriptPath, options).then(results => {
        if (!this.shouldApplyResult(requestId)) {
          return;
        }
        // results is an array consisting of messages collected during execution
        console.log('results: %j', results);
        console.log('results length:', results?.length);
        
        if (!results || results.length === 0) {
          console.log('Warning: No results returned from Python script');
          const errorMsg = `<span style='color:orange'>Warning: No output from Python script. File may be empty or unreadable.</span>`;
          const head = `<!DOCTYPE html>
          <html dir="ltr" mozdisallowselectionprint>
          <head>
          <meta charset="utf-8">
          </head>`;
          const tail = ['</html>'].join('\n');
          const output = head + `<body>              
          <div id="x" style='font-family: Menlo, Consolas, "Ubuntu Mono",
          "Roboto Mono", "DejaVu Sans Mono",
          monospace'>` + errorMsg + `</div></body>` + tail;
          handle.safeApplyWebviewHtml(requestId, output);
          return;
        }
        
        var r = results as Array<string>;
        // display the blank and line break with html labels
        // for (var i=1; i<r.length; i++) {
        //   if (r[i].startsWith('<img')) {
        //     continue;
        //   }
        //   r[i] = r[i].replaceAll(" ", "&nbsp;");
        // }
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
        handle.safeApplyWebviewHtml(requestId, output);
    }).catch(err => {
        if (!this.shouldApplyResult(requestId)) {
          return;
        }
        console.log('Python error:', err);
        console.log('Error type:', typeof err);
        console.log('Error stack:', err?.stack);
        const head = `<!DOCTYPE html>
        <html dir="ltr" mozdisallowselectionprint>
        <head>
        <meta charset="utf-8">
        </head>`;
        const tail = ['</html>'].join('\n');
        const errorDetails = err?.message || err?.toString() || 'Unknown error';
        const interpreterPath = options.pythonPath ?? '<unknown>';
        const output = head + `<body>              
        <div id="x" style='color: red; font-family: Menlo, Consolas, "Ubuntu Mono",
        "Roboto Mono", "DejaVu Sans Mono",
        monospace'>Error: ` + errorDetails + `<br><br>Interpreter: ` + interpreterPath + `</div></body>` + tail;
        handle.safeApplyWebviewHtml(requestId, output);
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

  public toggleTruncation(): void {
    this._isFullMode = !this._isFullMode;
    void this.getWebviewContents(this.resource.path);
  }

  public refreshFromInterpreterChange(): void {
    void this.getWebviewContents(this.resource.path);
  }

  private shouldApplyResult(requestId: number): boolean {
    return this._previewState !== 'Disposed' && requestId === this._loadRequestId;
  }

  private safeApplyWebviewHtml(requestId: number, html: string): void {
    if (!this.shouldApplyResult(requestId)) {
      return;
    }
    this.webviewEditor.webview.html = html;
    this.update();
  }

  private existsPath(path: string): boolean {
    try {
      return fs.existsSync(path);
    } catch (error) {
      console.error('[PyData Viewer] Failed to check path existence:', error);
      return false;
    }
  }

  private shouldValidatePathExists(path: string): boolean {
    // If user provides a command name like "python"/"python3", let python-shell resolve it via PATH.
    // Only validate existence when this looks like an explicit file path.
    return path.includes('/') || path.includes('\\') || path.includes(':');
  }

  private renderSimpleMessage(messageHtml: string, color: string): void {
    const head = `<!DOCTYPE html>
        <html dir="ltr" mozdisallowselectionprint>
        <head>
        <meta charset="utf-8">
        </head>`;
    const tail = ['</html>'].join('\n');
    const output = head + `<body>
        <div id="x" style='color: ${color}; font-family: Menlo, Consolas, "Ubuntu Mono",
        "Roboto Mono", "DejaVu Sans Mono",
        monospace'>${messageHtml}</div></body>` + tail;
    this.webviewEditor.webview.html = output;
    this.update();
  }

  private async resolvePythonPath(
    resource: vscode.Uri,
    workspacePath: string
  ): Promise<PythonPathResolutionResult> {
    const configuredPythonPath = (getOption('vscode-pydata-viewer.pythonPath') as string | undefined) ?? 'default';
    const usePythonExtensionInterpreter =
      (getOption('vscode-pydata-viewer.usePythonExtensionInterpreter') as boolean | undefined) ?? true;
    const pythonExtensionPath = usePythonExtensionInterpreter
      ? await this.interpreterService.getActiveInterpreterPath(resource)
      : undefined;

    return resolvePythonPathPriority({
      configuredPythonPath,
      workspacePath,
      usePythonExtensionInterpreter,
      pythonExtensionPath,
      fallbackPythonPath: PythonShell.defaultPythonPath,
    });
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
