import * as vscode from 'vscode';
import { PyDataPreview } from './pydataPreview';

export class PyDataCustomProvider implements vscode.CustomReadonlyEditorProvider {
  public static readonly viewType = 'pydata.preview';

  private readonly _previews = new Set<PyDataPreview>();
  private _activePreview: PyDataPreview | undefined;

  constructor(private readonly extensionRoot: vscode.Uri) { }

  public openCustomDocument(uri: vscode.Uri): vscode.CustomDocument {
    return { uri, dispose: (): void => { } };
  }

  public async resolveCustomEditor(
    document: vscode.CustomDocument,
    webviewEditor: vscode.WebviewPanel
  ): Promise<void> {
    const preview = new PyDataPreview(
      this.extensionRoot,
      document.uri,
      webviewEditor
    );
    this._previews.add(preview);
    this.setActivePreview(preview);

    webviewEditor.onDidDispose(() => {
      this._previews.delete(preview);
    });

    webviewEditor.onDidChangeViewState(() => {
      if (webviewEditor.active) {
        this.setActivePreview(preview);
      } else if (this._activePreview === preview && !webviewEditor.active) {
        this.setActivePreview(undefined);
      }
    });
  }

  public get activePreview(): PyDataPreview | undefined {
    return this._activePreview;
  }

  private setActivePreview(value: PyDataPreview | undefined): void {
    this._activePreview = value;
  }
}