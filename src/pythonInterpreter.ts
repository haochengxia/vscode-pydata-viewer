import * as vscode from 'vscode';
import {
  ActiveEnvironmentPathChangeEvent,
  EnvironmentPath,
  PVSC_EXTENSION_ID,
  PythonExtension,
  Resource,
} from '@vscode/python-extension';

export type InterpreterSource = 'python-extension' | 'unknown';

export type InterpreterChange = {
  resource: Resource | undefined;
  path: string | undefined;
  source: InterpreterSource;
};

/**
 * Adapter around ms-python.python APIs.
 *
 * Goals:
 * 1) Keep all Python-extension API calls in one place.
 * 2) Expose a stable method to resolve active interpreter path per resource.
 * 3) Expose an event for interpreter changes.
 */
export class PythonInterpreterService implements vscode.Disposable {
  private pythonApi: PythonExtension | undefined;
  private apiLoadPromise: Promise<PythonExtension | undefined> | undefined;
  private activeEnvironmentListener: vscode.Disposable | undefined;
  private extensionsChangeListener: vscode.Disposable | undefined;
  private lastKnownExtensionState: { exists: boolean; isActive: boolean } | undefined;

  private readonly _onDidChangeInterpreter = new vscode.EventEmitter<InterpreterChange>();
  public readonly onDidChangeInterpreter = this._onDidChangeInterpreter.event;

  public async initialize(): Promise<void> {
    this.ensureExtensionsChangeListener();
    this.lastKnownExtensionState = this.getPythonExtensionState();
    console.log('[PyData Viewer] Initial Python extension state:', this.lastKnownExtensionState);
    await this.getPythonApi();
  }

  public async getActiveInterpreterPath(resource?: Resource): Promise<string | undefined> {
    const api = await this.getPythonApi();
    if (!api) {
      return undefined;
    }

    const environmentPath = api.environments.getActiveEnvironmentPath(resource);
    return this.resolveExecutablePath(api, environmentPath);
  }

  public dispose(): void {
    this.extensionsChangeListener?.dispose();
    this.activeEnvironmentListener?.dispose();
    this._onDidChangeInterpreter.dispose();
  }

  private async getPythonApi(): Promise<PythonExtension | undefined> {
    if (this.pythonApi) {
      return this.pythonApi;
    }

    if (!this.apiLoadPromise) {
      this.apiLoadPromise = this.activatePythonApi();
    }

    this.pythonApi = await this.apiLoadPromise;

    // Important: do not permanently cache failed initialization.
    // If Python extension is enabled later, we must retry loading API.
    if (!this.pythonApi) {
      this.apiLoadPromise = undefined;
    }

    return this.pythonApi;
  }

  private ensureExtensionsChangeListener(): void {
    if (this.extensionsChangeListener) {
      return;
    }

    this.extensionsChangeListener = vscode.extensions.onDidChange(() => {
      void this.handleExtensionsChanged();
    });
  }

  private getPythonExtensionState(): { exists: boolean; isActive: boolean } {
    const extension = vscode.extensions.getExtension(PVSC_EXTENSION_ID);
    return {
      exists: !!extension,
      isActive: extension?.isActive ?? false,
    };
  }

  private async handleExtensionsChanged(): Promise<void> {
    const currentState = this.getPythonExtensionState();
    const previousState = this.lastKnownExtensionState;
    this.lastKnownExtensionState = currentState;

    console.log('[PyData Viewer] Extension change detected.', {
      extensionId: PVSC_EXTENSION_ID,
      previousState,
      currentState,
    });

    // Skip unrelated extension changes.
    if (
      previousState &&
      previousState.exists === currentState.exists &&
      previousState.isActive === currentState.isActive
    ) {
      return;
    }

    // Extension removed/disabled/unloaded.
    if (!currentState.exists) {
      console.log('[PyData Viewer] Python extension unavailable. Resetting API cache.');
      this.resetPythonApiState();
      return;
    }

    // Extension is present but inactive now. Reset and wait for next activation.
    if (!currentState.isActive) {
      console.log('[PyData Viewer] Python extension is present but inactive. Waiting for activation.');
      this.resetPythonApiState();
      return;
    }

    // Extension became available/active again. Reconnect and notify previews.
    this.resetPythonApiState();
    console.log('[PyData Viewer] Python extension became active again. Attempting API recovery...');
    await this.tryRecoverPythonApiAndNotify();
  }

  private async tryRecoverPythonApiAndNotify(): Promise<void> {
    const api = await this.getPythonApi();
    if (!api) {
      console.log('[PyData Viewer] API recovery skipped: Python API still unavailable.');
      return;
    }

    const path = await this.getActiveInterpreterPath();
    console.log('[PyData Viewer] API recovered. Broadcasting interpreter refresh event.', {
      path,
      source: 'python-extension',
    });
    this._onDidChangeInterpreter.fire({
      resource: undefined,
      path,
      source: 'python-extension',
    });
  }

  private resetPythonApiState(): void {
    console.log('[PyData Viewer] Resetting Python API state cache and listeners.');
    this.pythonApi = undefined;
    this.apiLoadPromise = undefined;
    this.activeEnvironmentListener?.dispose();
    this.activeEnvironmentListener = undefined;
  }

  private async activatePythonApi(): Promise<PythonExtension | undefined> {
    const pythonExtension = vscode.extensions.getExtension(PVSC_EXTENSION_ID);
    if (!pythonExtension) {
      console.log('[PyData Viewer] Python extension is not installed.');
      return undefined;
    }

    try {
      if (!pythonExtension.isActive) {
        console.log('[PyData Viewer] Activating Python extension...');
        await pythonExtension.activate();
      }

      const api = await PythonExtension.api();
      console.log('[PyData Viewer] Python extension API activated successfully.');
      this.ensureEnvironmentListener(api);
      return api;
    } catch (error) {
      console.error('[PyData Viewer] Failed to activate Python extension API:', error);
      return undefined;
    }
  }

  private ensureEnvironmentListener(api: PythonExtension): void {
    if (this.activeEnvironmentListener) {
      return;
    }

    this.activeEnvironmentListener = api.environments.onDidChangeActiveEnvironmentPath((event) => {
      void this.handleActiveEnvironmentChange(event);
    });
  }

  private async handleActiveEnvironmentChange(event: ActiveEnvironmentPathChangeEvent): Promise<void> {
    const api = await this.getPythonApi();

    let resolvedPath: string | undefined = event.path;
    if (api) {
      resolvedPath = await this.resolveExecutablePath(api, event);
    }

    console.log('[PyData Viewer] Active interpreter changed.', {
      resource: event.resource,
      rawPath: event.path,
      resolvedPath,
    });

    this._onDidChangeInterpreter.fire({
      resource: event.resource,
      path: resolvedPath,
      source: 'python-extension',
    });
  }

  private async resolveExecutablePath(
    api: PythonExtension,
    environmentPath: EnvironmentPath | undefined
  ): Promise<string | undefined> {
    if (!environmentPath) {
      return undefined;
    }

    try {
      const resolved = await api.environments.resolveEnvironment(environmentPath);
      const executablePath = resolved?.executable.uri?.fsPath;
      if (executablePath && executablePath.trim().length > 0) {
        return executablePath;
      }

      const fallbackPath = resolved?.path ?? environmentPath.path;
      if (fallbackPath && fallbackPath.trim().length > 0) {
        return fallbackPath;
      }
    } catch (error) {
      console.error('[PyData Viewer] Failed to resolve active environment:', error);
    }

    return undefined;
  }
}
